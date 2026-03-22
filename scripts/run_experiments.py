#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import platform
import shlex
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalized_entropy_from_counts(counts: dict[str, int]) -> float:
    values = [int(v or 0) for v in counts.values() if int(v or 0) > 0]
    if not values:
        return 0.0
    total = sum(values)
    if total <= 0 or len(values) <= 1:
        return 0.0
    probs = [v / total for v in values]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    return round(entropy / math.log2(len(values)), 4)


def run(cmd: str, timeout_seconds: float | None = None):
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            shell=True,
            text=True,
            capture_output=True,
            timeout=None if timeout_seconds is None or timeout_seconds <= 0 else timeout_seconds,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        return 124, str(exc.stdout or ""), f"timeout_after_seconds={timeout_seconds}"


def utc_stamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def config_fingerprint(cfg: dict) -> str:
    payload = json.dumps(cfg, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def load_metrics(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_prompt_bank(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"prompt bank not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def row_list_values(row: dict, field: str) -> set[str]:
    return {str(v).strip() for v in row.get(field, []) if str(v).strip()}


def summarize_prompt_bank(
    bank: dict,
    scenario_ids: set[str],
    scenario_tags: set[str],
    scenario_domains: set[str],
    scenario_emotion_axes: set[str],
    scenario_difficulties: set[str],
    persona_ids: set[str],
) -> dict:
    scenarios = bank.get("scenarios", [])
    personas = bank.get("personas", [])

    selected_scenarios = []
    selected_tags = set()
    selected_labels = set()
    selected_domains = set()
    selected_emotion_axes = set()
    selected_difficulties = set()
    for scenario in scenarios:
        row_tags = row_list_values(scenario, "tags")
        row_domains = row_list_values(scenario, "domains")
        row_emotion_axes = row_list_values(scenario, "emotion_axes")
        row_difficulty = str(scenario.get("difficulty") or "").strip()
        if scenario_ids and scenario.get("id") not in scenario_ids:
            continue
        if scenario_tags and not scenario_tags.issubset(row_tags):
            continue
        if scenario_domains and not scenario_domains.issubset(row_domains):
            continue
        if scenario_emotion_axes and not scenario_emotion_axes.issubset(row_emotion_axes):
            continue
        if scenario_difficulties and row_difficulty not in scenario_difficulties:
            continue
        selected_scenarios.append(scenario)
        selected_tags.update(row_tags)
        selected_domains.update(row_domains)
        selected_emotion_axes.update(row_emotion_axes)
        label = str(scenario.get("label") or "").strip()
        if label:
            selected_labels.add(label)
        if row_difficulty:
            selected_difficulties.add(row_difficulty)

    selected_personas = [persona for persona in personas if not persona_ids or persona.get("id") in persona_ids]
    selected_persona_style_tags = {
        str(tag).strip()
        for persona in selected_personas
        for tag in persona.get("style_tags", [])
        if str(tag).strip()
    }

    scenario_label_counts = {
        label: sum(1 for row in selected_scenarios if str(row.get("label") or "").strip() == label)
        for label in sorted(selected_labels)
    }
    scenario_domain_counts = {
        domain: sum(1 for row in selected_scenarios if domain in row_list_values(row, "domains"))
        for domain in sorted(selected_domains)
    }
    scenario_emotion_axis_counts = {
        axis: sum(1 for row in selected_scenarios if axis in row_list_values(row, "emotion_axes"))
        for axis in sorted(selected_emotion_axes)
    }
    scenario_label_entropy = normalized_entropy_from_counts(scenario_label_counts)
    scenario_domain_entropy = normalized_entropy_from_counts(scenario_domain_counts)
    scenario_emotion_axis_entropy = normalized_entropy_from_counts(scenario_emotion_axis_counts)

    return {
        "scenario_count": len(selected_scenarios),
        "persona_count": len(selected_personas),
        "scenario_ids": [row.get("id") for row in selected_scenarios],
        "persona_ids": [row.get("id") for row in selected_personas],
        "scenario_tag_count": len(selected_tags),
        "scenario_tags": sorted(selected_tags),
        "scenario_label_count": len(selected_labels),
        "scenario_labels": sorted(selected_labels),
        "scenario_label_counts": scenario_label_counts,
        "scenario_domain_count": len(selected_domains),
        "scenario_domains": sorted(selected_domains),
        "scenario_domain_counts": scenario_domain_counts,
        "scenario_domain_entropy": scenario_domain_entropy,
        "scenario_emotion_axis_count": len(selected_emotion_axes),
        "scenario_emotion_axes": sorted(selected_emotion_axes),
        "scenario_emotion_axis_counts": scenario_emotion_axis_counts,
        "scenario_emotion_axis_entropy": scenario_emotion_axis_entropy,
        "scenario_difficulty_count": len(selected_difficulties),
        "scenario_difficulties": sorted(selected_difficulties),
        "scenario_label_dominance": round((max(scenario_label_counts.values(), default=0) / max(1, len(selected_scenarios))), 4) if selected_scenarios else 0.0,
        "scenario_label_entropy": scenario_label_entropy,
        "persona_style_tag_count": len(selected_persona_style_tags),
        "persona_style_tags": sorted(selected_persona_style_tags),
    }


def aggregate_metrics(metric_paths):
    rows = []
    for p in metric_paths:
        rows.extend(load_metrics(p))

    if not rows:
        return {}

    counter = [r.get("counterfactual_per_sample", 0.0) for r in rows]
    regret = [r.get("regret_words_per_sample", 0.0) for r in rows]

    return {
        "cells": len(rows),
        "counterfactual_per_sample_mean": round(statistics.fmean(counter), 6),
        "counterfactual_per_sample_sd": round(statistics.pstdev(counter), 6) if len(counter) > 1 else 0.0,
        "regret_words_per_sample_mean": round(statistics.fmean(regret), 6),
        "regret_words_per_sample_sd": round(statistics.pstdev(regret), 6) if len(regret) > 1 else 0.0,
    }


def get_git_commit() -> str:
    code, out, _ = run("git rev-parse HEAD")
    return out.strip() if code == 0 else "unknown"


def get_git_status() -> dict:
    code, out, _ = run("git status --porcelain")
    if code != 0:
        return {"available": False, "dirty": None, "changes": []}
    changes = [line.rstrip() for line in out.splitlines() if line.strip()]
    return {"available": True, "dirty": bool(changes), "changes": changes}


def parse_csv_set(value) -> set[str]:
    if isinstance(value, list):
        return {str(v).strip() for v in value if str(v).strip()}
    if isinstance(value, str):
        return {v.strip() for v in value.split(",") if v.strip()}
    return set()


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def write_json(path: Path, payload: dict):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, payload: dict):
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_runs_csv(path: Path, runs: list[dict]):
    if not runs:
        return
    keys = [
        "id",
        "run_key",
        "repeat_index",
        "n",
        "seed",
        "temperatures",
        "prompt_bank",
        "scenario_ids",
        "scenario_labels",
        "scenario_tags",
        "scenario_domains",
        "scenario_emotion_axes",
        "scenario_difficulties",
        "persona_ids",
        "scenario_label_count",
        "scenario_domain_count",
        "scenario_emotion_axis_count",
        "scenario_difficulty_count",
        "persona_style_tag_count",
        "persona_style_tags",
        "scenario_count",
        "persona_count",
        "temperature_count",
        "condition_cells",
        "planned_samples",
        "prompt_bank_fingerprint",
        "dataset",
        "metrics",
        "dataset_sha256",
        "metrics_sha256",
        "status",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in runs:
            out = {k: row.get(k) for k in keys}
            temps = out.get("temperatures")
            if isinstance(temps, list):
                out["temperatures"] = ",".join(str(t) for t in temps)
            for field in (
                "scenario_ids",
                "scenario_labels",
                "scenario_tags",
                "scenario_domains",
                "scenario_emotion_axes",
                "scenario_difficulties",
                "persona_ids",
                "persona_style_tags",
            ):
                value = out.get(field)
                if isinstance(value, list):
                    out[field] = ",".join(str(v) for v in value)
            w.writerow(out)


def aggregate_by_run_id(run_metric_paths: dict[str, list[Path]]) -> list[dict]:
    rows = []
    for run_id in sorted(run_metric_paths):
        metrics = aggregate_metrics(run_metric_paths[run_id])
        if not metrics:
            continue
        rows.append({"id": run_id, **metrics})
    return rows


def pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def live_attempt_share_exceeded(*, run_id: str, generation_attempts_by_run_id: dict[str, int], analysis_attempts_by_run_id: dict[str, int], generation_attempts_total: int, analysis_attempts_total: int, generation_retries_by_run_id: dict[str, int], analysis_retries_by_run_id: dict[str, int], generation_retries_total: int, analysis_retries_total: int, selected_cells_by_run_id: dict[str, int], selected_run_cells: int, max_live_generation_attempt_share_per_run_id: float, max_live_analysis_attempt_share_per_run_id: float, max_live_combined_attempt_share_per_run_id: float, max_live_stage_attempt_share_gap_per_run_id: float, max_live_retry_share_per_run_id: float, max_live_retry_over_selection_ratio_per_run_id: float, max_live_attempt_over_selection_ratio_per_run_id: float) -> tuple[bool, str]:
    run_generation = int(generation_attempts_by_run_id.get(run_id, 0) or 0)
    run_analysis = int(analysis_attempts_by_run_id.get(run_id, 0) or 0)
    run_combined = run_generation + run_analysis
    combined_total = generation_attempts_total + analysis_attempts_total
    if max_live_generation_attempt_share_per_run_id > 0 and generation_attempts_total > 0:
        share = run_generation / generation_attempts_total
        if share > max_live_generation_attempt_share_per_run_id:
            return True, f"generation_share={round(share,4)}>{max_live_generation_attempt_share_per_run_id}"
    if max_live_analysis_attempt_share_per_run_id > 0 and analysis_attempts_total > 0:
        share = run_analysis / analysis_attempts_total
        if share > max_live_analysis_attempt_share_per_run_id:
            return True, f"analysis_share={round(share,4)}>{max_live_analysis_attempt_share_per_run_id}"
    if max_live_combined_attempt_share_per_run_id > 0 and combined_total > 0:
        share = run_combined / combined_total
        if share > max_live_combined_attempt_share_per_run_id:
            return True, f"combined_share={round(share,4)}>{max_live_combined_attempt_share_per_run_id}"
    if max_live_stage_attempt_share_gap_per_run_id > 0 and generation_attempts_total > 0 and analysis_attempts_total > 0:
        generation_share = run_generation / generation_attempts_total
        analysis_share = run_analysis / analysis_attempts_total
        gap = abs(generation_share - analysis_share)
        if gap > max_live_stage_attempt_share_gap_per_run_id:
            return True, f"stage_share_gap={round(gap,4)}>{max_live_stage_attempt_share_gap_per_run_id}"
    run_retries = int(generation_retries_by_run_id.get(run_id, 0) or 0) + int(analysis_retries_by_run_id.get(run_id, 0) or 0)
    retries_total = generation_retries_total + analysis_retries_total
    if max_live_retry_share_per_run_id > 0 and retries_total > 0:
        retry_share = run_retries / retries_total
        if retry_share > max_live_retry_share_per_run_id:
            return True, f"retry_share={round(retry_share,4)}>{max_live_retry_share_per_run_id}"
    if max_live_retry_over_selection_ratio_per_run_id > 0 and retries_total > 0 and selected_run_cells > 0:
        selected_share = int(selected_cells_by_run_id.get(run_id, 0) or 0) / selected_run_cells
        if selected_share > 0:
            retry_share = run_retries / retries_total
            retry_over_selection_ratio = retry_share / selected_share
            if retry_over_selection_ratio > max_live_retry_over_selection_ratio_per_run_id:
                return True, f"retry_over_selection_ratio={round(retry_over_selection_ratio,4)}>{max_live_retry_over_selection_ratio_per_run_id}"
    if max_live_attempt_over_selection_ratio_per_run_id > 0 and combined_total > 0 and selected_run_cells > 0:
        selected_share = int(selected_cells_by_run_id.get(run_id, 0) or 0) / selected_run_cells
        if selected_share > 0:
            combined_share = run_combined / combined_total
            attempt_over_selection_ratio = combined_share / selected_share
            if attempt_over_selection_ratio > max_live_attempt_over_selection_ratio_per_run_id:
                return True, f"attempt_over_selection_ratio={round(attempt_over_selection_ratio,4)}>{max_live_attempt_over_selection_ratio_per_run_id}"
    return False, ""


def write_run_summary_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = [
        "id",
        "cells",
        "counterfactual_per_sample_mean",
        "counterfactual_per_sample_sd",
        "regret_words_per_sample_mean",
        "regret_words_per_sample_sd",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in keys})


def write_selection_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = [
        "id",
        "prompt_bank",
        "prompt_bank_version",
        "prompt_bank_fingerprint",
        "scenario_count",
        "persona_count",
        "scenario_label_count",
        "scenario_label_dominance",
        "scenario_labels",
        "scenario_tag_count",
        "scenario_tags",
        "scenario_domain_count",
        "scenario_domains",
        "scenario_emotion_axis_count",
        "scenario_emotion_axes",
        "scenario_difficulty_count",
        "scenario_difficulties",
        "scenario_ids",
        "persona_ids",
        "persona_style_tag_count",
        "persona_style_tags",
        "temperature_count",
        "condition_cells",
        "planned_samples",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            out = {k: row.get(k) for k in keys}
            for field in (
                "scenario_labels",
                "scenario_tags",
                "scenario_domains",
                "scenario_emotion_axes",
                "scenario_difficulties",
                "scenario_ids",
                "persona_ids",
                "persona_style_tags",
            ):
                value = out.get(field)
                if isinstance(value, list):
                    out[field] = ",".join(str(v) for v in value)
            label_counts = out.get("scenario_label_counts")
            if isinstance(label_counts, dict):
                out["scenario_label_counts"] = json.dumps(label_counts, ensure_ascii=False, sort_keys=True)
            w.writerow(out)
        return


def write_preflight_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = [
        "id",
        "prompt_bank_version",
        "scenario_count",
        "persona_count",
        "temperature_count",
        "temperature_span",
        "repeats",
        "condition_cells",
        "planned_samples",
        "scenario_label_count",
        "scenario_label_dominance",
        "scenario_labels",
        "scenario_tag_count",
        "scenario_tags",
        "scenario_domain_count",
        "scenario_domains",
        "scenario_emotion_axis_count",
        "scenario_emotion_axes",
        "scenario_difficulty_count",
        "scenario_difficulties",
        "persona_style_tag_count",
        "persona_style_tags",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            out = {k: row.get(k) for k in keys}
            for field in (
                "scenario_labels",
                "scenario_tags",
                "scenario_domains",
                "scenario_emotion_axes",
                "scenario_difficulties",
                "persona_style_tags",
            ):
                value = out.get(field)
                if isinstance(value, list):
                    out[field] = ",".join(str(v) for v in value)
            w.writerow(out)


def write_preflight_markdown(path: Path, payload: dict):
    summary = payload.get("summary") or {}
    lines = [
        f"# Preflight Report: {payload.get('run_label', '')}",
        "",
        f"- generated_at_utc: `{payload.get('generated_at_utc', '')}`",
        f"- config: `{payload.get('config', '')}`",
        f"- selected_run_ids: `{len(payload.get('selected_run_ids', []))}`",
        f"- prompt_bank_versions: `{', '.join(summary.get('prompt_bank_versions', []))}`",
        f"- min_scenario_count: `{summary.get('min_scenario_count', 0)}`",
        f"- min_persona_count: `{summary.get('min_persona_count', 0)}`",
        f"- min_temperature_count: `{summary.get('min_temperature_count', 0)}`",
        f"- min_temperature_span: `{summary.get('min_temperature_span', 0.0)}`",
        f"- min_condition_cells: `{summary.get('min_condition_cells', 0)}`",
        f"- min_planned_samples: `{summary.get('min_planned_samples', 0)}`",
        f"- max_scenario_label_dominance: `{summary.get('max_scenario_label_dominance', 0.0)}`",
        f"- unique_selected_scenarios: `{summary.get('unique_selected_scenarios', 0)}`",
        f"- unique_selected_personas: `{summary.get('unique_selected_personas', 0)}`",
        f"- unique_selected_scenario_labels: `{summary.get('unique_selected_scenario_labels', 0)}`",
        f"- unique_selected_scenario_tags: `{summary.get('unique_selected_scenario_tags', 0)}`",
        f"- unique_selected_scenario_domains: `{summary.get('unique_selected_scenario_domains', 0)}`",
        f"- unique_selected_scenario_emotion_axes: `{summary.get('unique_selected_scenario_emotion_axes', 0)}`",
        f"- unique_selected_scenario_difficulties: `{summary.get('unique_selected_scenario_difficulties', 0)}`",
        f"- unique_selected_persona_style_tags: `{summary.get('unique_selected_persona_style_tags', 0)}`",
        "",
        "| run_id | prompt_bank_version | scenarios | personas | temps | temp_span | condition_cells | planned_samples | labels | tags | domains | emotion_axes | difficulties | persona_style_tags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload.get("rows") or []:
        lines.append(
            f"| {row.get('id','')} | {row.get('prompt_bank_version','')} | {row.get('scenario_count',0)} | {row.get('persona_count',0)} | "
            f"{row.get('temperature_count',0)} | {row.get('temperature_span',0.0)} | {row.get('condition_cells',0)} | {row.get('planned_samples',0)} | "
            f"{row.get('scenario_label_count',0)} | {row.get('scenario_tag_count',0)} | {row.get('scenario_domain_count',0)} | "
            f"{row.get('scenario_emotion_axis_count',0)} | {row.get('scenario_difficulty_count',0)} | {row.get('persona_style_tag_count',0)} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_quarantine_candidates(runs: list[dict]) -> list[dict]:
    candidates = []
    for row in runs:
        status = str(row.get("status") or "")
        if not status.startswith("failed_"):
            continue
        candidates.append(
            {
                "id": row.get("id", ""),
                "run_key": row.get("run_key", ""),
                "status": status,
                "generation_attempts": int(row.get("generation_attempts") or 0),
                "analysis_attempts": int(row.get("analysis_attempts") or 0),
                "error": str(row.get("error") or "").strip(),
            }
        )
    return candidates


def write_quarantine_csv(path: Path, rows: list[dict]):
    keys = ["id", "run_key", "status", "generation_attempts", "analysis_attempts", "error"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in keys})


def build_budget_report(
    *,
    run_label: str,
    selected_cells_by_run_id: dict[str, int],
    successful_cells_by_run_id: dict[str, int],
    failed_cells_by_run_id: dict[str, int],
    generation_attempts_by_run_id: dict[str, int],
    analysis_attempts_by_run_id: dict[str, int],
    generation_retries_by_run_id: dict[str, int],
    analysis_retries_by_run_id: dict[str, int],
    selected_run_cells: int,
    generation_attempts_total: int,
    analysis_attempts_total: int,
    generation_retries_total: int,
    analysis_retries_total: int,
    failed_cells_total: int,
) -> dict:
    rows = []
    for run_id in sorted(selected_cells_by_run_id):
        selected_cells = int(selected_cells_by_run_id.get(run_id, 0) or 0)
        generation_attempts = int(generation_attempts_by_run_id.get(run_id, 0) or 0)
        analysis_attempts = int(analysis_attempts_by_run_id.get(run_id, 0) or 0)
        generation_retries = int(generation_retries_by_run_id.get(run_id, 0) or 0)
        analysis_retries = int(analysis_retries_by_run_id.get(run_id, 0) or 0)
        combined_attempts = generation_attempts + analysis_attempts
        combined_retries = generation_retries + analysis_retries
        rows.append(
            {
                "id": run_id,
                "selected_cells": selected_cells,
                "selected_cell_share": pct(selected_cells, selected_run_cells),
                "successful_cells": int(successful_cells_by_run_id.get(run_id, 0) or 0),
                "failed_cells": int(failed_cells_by_run_id.get(run_id, 0) or 0),
                "failed_cell_share": pct(
                    int(failed_cells_by_run_id.get(run_id, 0) or 0),
                    failed_cells_total,
                ),
                "run_id_success_rate": pct(
                    int(successful_cells_by_run_id.get(run_id, 0) or 0),
                    selected_cells,
                ),
                "generation_attempts": generation_attempts,
                "generation_attempt_share": pct(generation_attempts, generation_attempts_total),
                "analysis_attempts": analysis_attempts,
                "analysis_attempt_share": pct(analysis_attempts, analysis_attempts_total),
                "generation_retries": generation_retries,
                "analysis_retries": analysis_retries,
                "generation_retry_share": pct(generation_retries, generation_retries_total),
                "analysis_retry_share": pct(analysis_retries, analysis_retries_total),
                "combined_retries": combined_retries,
                "retry_share": pct(combined_retries, generation_retries_total + analysis_retries_total),
                "combined_attempts": combined_attempts,
                "combined_attempt_share": pct(
                    combined_attempts,
                    generation_attempts_total + analysis_attempts_total,
                ),
                "attempt_over_selection_ratio": round(
                    pct(combined_attempts, generation_attempts_total + analysis_attempts_total)
                    / max(pct(selected_cells, selected_run_cells), 0.0001),
                    4,
                )
                if selected_cells > 0 and (generation_attempts_total + analysis_attempts_total) > 0 and selected_run_cells > 0
                else 0.0,
                "retry_over_selection_ratio": round(
                    pct(combined_retries, generation_retries_total + analysis_retries_total)
                    / max(pct(selected_cells, selected_run_cells), 0.0001),
                    4,
                )
                if selected_cells > 0 and (generation_retries_total + analysis_retries_total) > 0 and selected_run_cells > 0
                else 0.0,
                "generation_attempt_over_selection_ratio": round(
                    pct(generation_attempts, generation_attempts_total)
                    / max(pct(selected_cells, selected_run_cells), 0.0001),
                    4,
                )
                if selected_cells > 0 and generation_attempts_total > 0 and selected_run_cells > 0
                else 0.0,
                "analysis_attempt_over_selection_ratio": round(
                    pct(analysis_attempts, analysis_attempts_total)
                    / max(pct(selected_cells, selected_run_cells), 0.0001),
                    4,
                )
                if selected_cells > 0 and analysis_attempts_total > 0 and selected_run_cells > 0
                else 0.0,
                "stage_attempt_pressure_ratio": round(
                    max(
                        (
                            pct(generation_attempts, generation_attempts_total)
                            / max(pct(selected_cells, selected_run_cells), 0.0001)
                        )
                        if selected_cells > 0 and generation_attempts_total > 0 and selected_run_cells > 0
                        else 0.0,
                        (
                            pct(analysis_attempts, analysis_attempts_total)
                            / max(pct(selected_cells, selected_run_cells), 0.0001)
                        )
                        if selected_cells > 0 and analysis_attempts_total > 0 and selected_run_cells > 0
                        else 0.0,
                    ),
                    4,
                ),
                "stage_attempt_share_gap": round(
                    abs(pct(generation_attempts, generation_attempts_total) - pct(analysis_attempts, analysis_attempts_total)),
                    4,
                )
                if generation_attempts_total > 0 and analysis_attempts_total > 0
                else 0.0,
                "stage_attempt_imbalance_ratio": round(
                    max(generation_attempts, analysis_attempts) / max(1, min(generation_attempts, analysis_attempts)),
                    4,
                )
                if combined_attempts > 0
                else 0.0,
                "failure_over_selection_ratio": round(
                    pct(int(failed_cells_by_run_id.get(run_id, 0) or 0), failed_cells_total)
                    / max(pct(selected_cells, selected_run_cells), 0.0001),
                    4,
                )
                if selected_cells > 0 and failed_cells_total > 0 and selected_run_cells > 0
                else 0.0,
            }
        )

    max_selected = max(rows, key=lambda row: (row["selected_cell_share"], row["id"]), default=None)
    max_attempt = max(rows, key=lambda row: (row["combined_attempt_share"], row["id"]), default=None)
    max_failed = max(rows, key=lambda row: (row["failed_cells"], row["id"]), default=None)
    max_failed_share = max(rows, key=lambda row: (row["failed_cell_share"], row["id"]), default=None)
    max_attempt_pressure = max(rows, key=lambda row: (row["attempt_over_selection_ratio"], row["id"]), default=None)
    max_retry_share = max(rows, key=lambda row: (row["retry_share"], row["id"]), default=None)
    max_generation_retry_share = max(rows, key=lambda row: (row["generation_retry_share"], row["id"]), default=None)
    max_analysis_retry_share = max(rows, key=lambda row: (row["analysis_retry_share"], row["id"]), default=None)
    max_retry_pressure = max(rows, key=lambda row: (row["retry_over_selection_ratio"], row["id"]), default=None)
    max_generation_attempt_pressure = max(rows, key=lambda row: (row["generation_attempt_over_selection_ratio"], row["id"]), default=None)
    max_analysis_attempt_pressure = max(rows, key=lambda row: (row["analysis_attempt_over_selection_ratio"], row["id"]), default=None)
    max_stage_attempt_pressure = max(rows, key=lambda row: (row["stage_attempt_pressure_ratio"], row["id"]), default=None)
    max_failure_pressure = max(rows, key=lambda row: (row["failure_over_selection_ratio"], row["id"]), default=None)
    max_stage_attempt_share_gap = max(rows, key=lambda row: (row["stage_attempt_share_gap"], row["id"]), default=None)
    max_stage_attempt_imbalance_ratio = max(
        rows,
        key=lambda row: (row["stage_attempt_imbalance_ratio"], row["id"]),
        default=None,
    )
    return {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "run_label": run_label,
        "summary": {
            "selected_run_cells": selected_run_cells,
            "generation_attempts_total": generation_attempts_total,
            "analysis_attempts_total": analysis_attempts_total,
            "generation_retries_total": generation_retries_total,
            "analysis_retries_total": analysis_retries_total,
            "combined_retries_total": generation_retries_total + analysis_retries_total,
            "combined_attempts_total": generation_attempts_total + analysis_attempts_total,
            "stage_total_attempt_gap_share": round(
                abs(generation_attempts_total - analysis_attempts_total)
                / max(1, generation_attempts_total + analysis_attempts_total),
                4,
            ),
            "stage_total_attempt_imbalance_ratio": round(
                max(generation_attempts_total, analysis_attempts_total)
                / max(1, min(generation_attempts_total, analysis_attempts_total)),
                4,
            )
            if (generation_attempts_total + analysis_attempts_total) > 0
            else 0.0,
            "max_selected_cell_share_run_id": (max_selected or {}).get("id", ""),
            "max_selected_cell_share": (max_selected or {}).get("selected_cell_share", 0.0),
            "min_selected_cell_share_run_id": (min(rows, key=lambda row: (row["selected_cell_share"], row["id"]), default={}) or {}).get("id", ""),
            "min_selected_cell_share": (min(rows, key=lambda row: (row["selected_cell_share"], row["id"]), default={}) or {}).get("selected_cell_share", 0.0),
            "selected_cell_share_gap": round(
                ((max_selected or {}).get("selected_cell_share", 0.0))
                - ((min(rows, key=lambda row: (row["selected_cell_share"], row["id"]), default={}) or {}).get("selected_cell_share", 0.0)),
                4,
            ) if rows else 0.0,
            "max_combined_attempt_share_run_id": (max_attempt or {}).get("id", ""),
            "max_combined_attempt_share": (max_attempt or {}).get("combined_attempt_share", 0.0),
            "max_failed_cells_run_id": (max_failed or {}).get("id", ""),
            "max_failed_cells": (max_failed or {}).get("failed_cells", 0),
            "max_failed_cell_share_run_id": (max_failed_share or {}).get("id", ""),
            "max_failed_cell_share": (max_failed_share or {}).get("failed_cell_share", 0.0),
            "max_attempt_over_selection_ratio_run_id": (max_attempt_pressure or {}).get("id", ""),
            "max_attempt_over_selection_ratio": (max_attempt_pressure or {}).get("attempt_over_selection_ratio", 0.0),
            "max_retry_share_run_id": (max_retry_share or {}).get("id", ""),
            "max_retry_share": (max_retry_share or {}).get("retry_share", 0.0),
            "max_generation_retry_share_run_id": (max_generation_retry_share or {}).get("id", ""),
            "max_generation_retry_share": (max_generation_retry_share or {}).get("generation_retry_share", 0.0),
            "max_analysis_retry_share_run_id": (max_analysis_retry_share or {}).get("id", ""),
            "max_analysis_retry_share": (max_analysis_retry_share or {}).get("analysis_retry_share", 0.0),
            "max_retry_over_selection_ratio_run_id": (max_retry_pressure or {}).get("id", ""),
            "max_retry_over_selection_ratio": (max_retry_pressure or {}).get("retry_over_selection_ratio", 0.0),
            "max_generation_attempt_over_selection_ratio_run_id": (max_generation_attempt_pressure or {}).get("id", ""),
            "max_generation_attempt_over_selection_ratio": (max_generation_attempt_pressure or {}).get("generation_attempt_over_selection_ratio", 0.0),
            "max_analysis_attempt_over_selection_ratio_run_id": (max_analysis_attempt_pressure or {}).get("id", ""),
            "max_analysis_attempt_over_selection_ratio": (max_analysis_attempt_pressure or {}).get("analysis_attempt_over_selection_ratio", 0.0),
            "max_stage_attempt_pressure_ratio_run_id": (max_stage_attempt_pressure or {}).get("id", ""),
            "max_stage_attempt_pressure_ratio": (max_stage_attempt_pressure or {}).get("stage_attempt_pressure_ratio", 0.0),
            "max_failure_over_selection_ratio_run_id": (max_failure_pressure or {}).get("id", ""),
            "max_failure_over_selection_ratio": (max_failure_pressure or {}).get("failure_over_selection_ratio", 0.0),
            "max_stage_attempt_share_gap_run_id": (max_stage_attempt_share_gap or {}).get("id", ""),
            "max_stage_attempt_share_gap": (max_stage_attempt_share_gap or {}).get("stage_attempt_share_gap", 0.0),
            "max_stage_attempt_imbalance_ratio_run_id": (max_stage_attempt_imbalance_ratio or {}).get("id", ""),
            "max_stage_attempt_imbalance_ratio": (max_stage_attempt_imbalance_ratio or {}).get("stage_attempt_imbalance_ratio", 0.0),
        },
        "rows": rows,
    }


def write_budget_report_markdown(path: Path, payload: dict):
    summary = payload.get("summary") or {}
    lines = [
        f"# Runner Budget Report: {payload.get('run_label', '')}",
        "",
        f"- generated_at_utc: `{payload.get('generated_at_utc', '')}`",
        f"- selected_run_cells: `{summary.get('selected_run_cells', 0)}`",
        f"- generation_attempts_total: `{summary.get('generation_attempts_total', 0)}`",
        f"- analysis_attempts_total: `{summary.get('analysis_attempts_total', 0)}`",
        f"- generation_retries_total: `{summary.get('generation_retries_total', 0)}`",
        f"- analysis_retries_total: `{summary.get('analysis_retries_total', 0)}`",
        f"- combined_retries_total: `{summary.get('combined_retries_total', 0)}`",
        f"- combined_attempts_total: `{summary.get('combined_attempts_total', 0)}`",
        f"- max_selected_cell_share: `{summary.get('max_selected_cell_share', 0.0)}` (`{summary.get('max_selected_cell_share_run_id', '')}`)",
        f"- min_selected_cell_share: `{summary.get('min_selected_cell_share', 0.0)}` (`{summary.get('min_selected_cell_share_run_id', '')}`)",
        f"- selected_cell_share_gap: `{summary.get('selected_cell_share_gap', 0.0)}`",
        f"- max_combined_attempt_share: `{summary.get('max_combined_attempt_share', 0.0)}` (`{summary.get('max_combined_attempt_share_run_id', '')}`)",
        f"- max_attempt_over_selection_ratio: `{summary.get('max_attempt_over_selection_ratio', 0.0)}` (`{summary.get('max_attempt_over_selection_ratio_run_id', '')}`)",
        f"- max_retry_share: `{summary.get('max_retry_share', 0.0)}` (`{summary.get('max_retry_share_run_id', '')}`)",
        f"- max_generation_retry_share: `{summary.get('max_generation_retry_share', 0.0)}` (`{summary.get('max_generation_retry_share_run_id', '')}`)",
        f"- max_analysis_retry_share: `{summary.get('max_analysis_retry_share', 0.0)}` (`{summary.get('max_analysis_retry_share_run_id', '')}`)",
        f"- max_retry_over_selection_ratio: `{summary.get('max_retry_over_selection_ratio', 0.0)}` (`{summary.get('max_retry_over_selection_ratio_run_id', '')}`)",
        f"- max_generation_attempt_over_selection_ratio: `{summary.get('max_generation_attempt_over_selection_ratio', 0.0)}` (`{summary.get('max_generation_attempt_over_selection_ratio_run_id', '')}`)",
        f"- max_analysis_attempt_over_selection_ratio: `{summary.get('max_analysis_attempt_over_selection_ratio', 0.0)}` (`{summary.get('max_analysis_attempt_over_selection_ratio_run_id', '')}`)",
        f"- max_stage_attempt_pressure_ratio: `{summary.get('max_stage_attempt_pressure_ratio', 0.0)}` (`{summary.get('max_stage_attempt_pressure_ratio_run_id', '')}`)",
        f"- max_failure_over_selection_ratio: `{summary.get('max_failure_over_selection_ratio', 0.0)}` (`{summary.get('max_failure_over_selection_ratio_run_id', '')}`)",
        f"- max_stage_attempt_share_gap: `{summary.get('max_stage_attempt_share_gap', 0.0)}` (`{summary.get('max_stage_attempt_share_gap_run_id', '')}`)",
        f"- max_stage_attempt_imbalance_ratio: `{summary.get('max_stage_attempt_imbalance_ratio', 0.0)}` (`{summary.get('max_stage_attempt_imbalance_ratio_run_id', '')}`)",
        f"- stage_total_attempt_gap_share: `{summary.get('stage_total_attempt_gap_share', 0.0)}`",
        f"- stage_total_attempt_imbalance_ratio: `{summary.get('stage_total_attempt_imbalance_ratio', 0.0)}`",
        f"- max_failed_cells: `{summary.get('max_failed_cells', 0)}` (`{summary.get('max_failed_cells_run_id', '')}`)",
        f"- max_failed_cell_share: `{summary.get('max_failed_cell_share', 0.0)}` (`{summary.get('max_failed_cell_share_run_id', '')}`)",
        "",
        "| run_id | selected_cells | selected_share | success_rate | gen_attempts | gen_share | gen_pressure | ana_attempts | ana_share | ana_pressure | stage_pressure | retries | retry_share | retry_pressure | stage_share_gap | stage_imbalance_ratio | combined_share | attempt_pressure | failed_cells | failed_share | failure_pressure |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|", 
    ]
    for row in payload.get("rows") or []:
        lines.append(
            f"| {row.get('id', '')} | {row.get('selected_cells', 0)} | {row.get('selected_cell_share', 0.0)} | "
            f"{row.get('run_id_success_rate', 0.0)} | {row.get('generation_attempts', 0)} | "
            f"{row.get('generation_attempt_share', 0.0)} | {row.get('generation_attempt_over_selection_ratio', 0.0)} | "
            f"{row.get('analysis_attempts', 0)} | {row.get('analysis_attempt_share', 0.0)} | {row.get('analysis_attempt_over_selection_ratio', 0.0)} | {row.get('stage_attempt_pressure_ratio', 0.0)} | "
            f"{row.get('combined_retries', 0)} | {row.get('retry_share', 0.0)} | {row.get('retry_over_selection_ratio', 0.0)} | "
            f"{row.get('stage_attempt_share_gap', 0.0)} | {row.get('stage_attempt_imbalance_ratio', 0.0)} | {row.get('combined_attempt_share', 0.0)} | {row.get('attempt_over_selection_ratio', 0.0)} | "
            f"{row.get('failed_cells', 0)} | {row.get('failed_cell_share', 0.0)} | {row.get('failure_over_selection_ratio', 0.0)} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest_markdown(path: Path, manifest: dict):
    summary = manifest.get("summary") or {}
    run_id_summary = manifest.get("run_id_summary") or []
    preflight_summary = manifest.get("preflight_summary") or {}
    lines = [
        f"# Experiment Manifest: {manifest.get('run_label', '')}",
        "",
        f"- generated_at_utc: `{manifest.get('generated_at_utc', '')}`",
        f"- config: `{manifest.get('config', '')}`",
        f"- config_fingerprint: `{manifest.get('config_fingerprint', '')}`",
        f"- git_commit: `{((manifest.get('environment') or {}).get('git_commit') or 'unknown')}`",
        f"- duration_seconds: `{manifest.get('duration_seconds', 0)}`",
        f"- plan_only: `{manifest.get('plan_only', False)}`",
        f"- executed_run_keys: `{len(manifest.get('executed_run_keys', []))}`",
        f"- failed_cells: `{manifest.get('failed_cells', 0)}`",
        f"- attempted_run_cells: `{manifest.get('attempted_run_cells', 0)}`",
        f"- failure_rate: `{manifest.get('failure_rate', 0.0)}`",
        f"- stopped_early: `{manifest.get('stopped_early', False)}`",
        f"- preflight_json: `{manifest.get('preflight_json', '')}`",
        f"- preflight_csv: `{manifest.get('preflight_csv', '')}`",
        f"- quarantine_json: `{manifest.get('quarantine_json', '')}`",
        f"- quarantine_csv: `{manifest.get('quarantine_csv', '')}`",
        f"- quarantine_failed_cells: `{manifest.get('quarantine_failed_cells', 0)}`",
        f"- generation_attempts_total: `{manifest.get('generation_attempts_total', 0)}`",
        f"- analysis_attempts_total: `{manifest.get('analysis_attempts_total', 0)}`",
        f"- max_generation_attempts_per_run_id: `{manifest.get('max_generation_attempts_per_run_id', 0)}`",
        f"- max_analysis_attempts_per_run_id: `{manifest.get('max_analysis_attempts_per_run_id', 0)}`",
        f"- max_attempts_per_cell: `{manifest.get('max_attempts_per_cell', 0)}`",
        f"- require_prompt_bank_version: `{manifest.get('require_prompt_bank_version', '')}`",
        f"- freeze_artifacts_checked: `{len(manifest.get('freeze_artifacts', []))}`",
        "",
        "## Aggregate metrics",
        "",
        f"- cells: `{summary.get('cells', 0)}`",
        f"- counterfactual_per_sample_mean: `{summary.get('counterfactual_per_sample_mean', 'n/a')}`",
        f"- regret_words_per_sample_mean: `{summary.get('regret_words_per_sample_mean', 'n/a')}`",
        "",
        "## Preflight summary",
        "",
        f"- selected_run_ids: `{preflight_summary.get('selected_run_id_count', 0)}`",
        f"- successful_cells: `{manifest.get('successful_cells', 0)}`",
        f"- success_rate: `{manifest.get('success_rate', 0.0)}`",
        f"- generation_success_rate: `{manifest.get('generation_success_rate', 0.0)}`",
        f"- analysis_success_rate: `{manifest.get('analysis_success_rate', 0.0)}`",
        f"- prompt_bank_versions: `{', '.join(preflight_summary.get('prompt_bank_versions', []))}`",
        f"- min_scenario_count: `{preflight_summary.get('min_scenario_count', 0)}`",
        f"- min_persona_count: `{preflight_summary.get('min_persona_count', 0)}`",
        f"- min_temperature_span: `{preflight_summary.get('min_temperature_span', 0.0)}`",
        f"- min_planned_samples: `{preflight_summary.get('min_planned_samples', 0)}`",
        f"- unique_selected_scenarios: `{preflight_summary.get('unique_selected_scenarios', 0)}`",
        f"- unique_selected_personas: `{preflight_summary.get('unique_selected_personas', 0)}`",
        f"- unique_selected_scenario_labels: `{preflight_summary.get('unique_selected_scenario_labels', 0)}`",
        f"- unique_selected_scenario_tags: `{preflight_summary.get('unique_selected_scenario_tags', 0)}`",
        f"- unique_selected_persona_style_tags: `{preflight_summary.get('unique_selected_persona_style_tags', 0)}`",
        f"- max_scenario_label_dominance: `{preflight_summary.get('max_scenario_label_dominance', 0.0)}`",
        f"- min_scenario_label_entropy: `{preflight_summary.get('min_scenario_label_entropy', 0.0)}`",
        f"- min_scenario_domain_entropy: `{preflight_summary.get('min_scenario_domain_entropy', 0.0)}`",
        f"- min_scenario_emotion_axis_entropy: `{preflight_summary.get('min_scenario_emotion_axis_entropy', 0.0)}`",
        "",
        "## Run-id summary",
        "",
        "| run_id | cells | counterfactual_mean | regret_mean |",
        "|---|---:|---:|---:|",
    ]
    for row in run_id_summary:
        lines.append(
            f"| {row.get('id','')} | {row.get('cells',0)} | {row.get('counterfactual_per_sample_mean','n/a')} | {row.get('regret_words_per_sample_mean','n/a')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reproduce_script(path: Path, run_label: str, config_path: str, runs: list[dict]):
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"# Auto-generated reproducibility script for run label: {run_label}",
        f"python3 scripts/run_experiments.py --config {shlex.quote(config_path)} --run-label {shlex.quote(run_label)} --plan-only",
        "",
        "# Cell-level regeneration",
    ]

    added = 0
    for row in runs:
        if row.get("status") not in {"ok", "planned_only", "skipped_resume"}:
            continue
        gen = row.get("generation_command")
        ana = row.get("analysis_command")
        if gen and ana:
            lines.append(gen)
            lines.append(ana)
            added += 1

    if added == 0:
        lines.append("# No executable cell commands captured in manifest.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o755)


def file_sha256(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha256(payload).hexdigest()


def maybe_file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return file_sha256(path)


def load_run_ids_from_file(path: Path) -> set[str]:
    run_ids = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        run_ids.add(line)
    return run_ids


def execute_with_retries(
    cmd: str,
    *,
    run_key: str,
    stage: str,
    max_retries: int,
    retry_backoff_seconds: float,
    execution_log_path: Path | None,
    timeout_seconds: float | None = None,
) -> tuple[int, str, str, list[dict]]:
    attempts = []
    for attempt_index in range(max_retries + 1):
        started_at = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        code, out, err = run(cmd, timeout_seconds=timeout_seconds)
        finished_at = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        attempt_payload = {
            "run_key": run_key,
            "stage": stage,
            "attempt": attempt_index + 1,
            "max_retries": max_retries,
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "return_code": code,
            "stdout": out,
            "stderr": err,
            "command": cmd,
            "timeout_seconds": timeout_seconds,
        }
        attempts.append(attempt_payload)
        if execution_log_path is not None:
            append_jsonl(execution_log_path, attempt_payload)
        if code == 0:
            return code, out, err, attempts
        if attempt_index < max_retries and retry_backoff_seconds > 0:
            time.sleep(retry_backoff_seconds)
    last = attempts[-1]
    return int(last["return_code"]), str(last["stdout"]), str(last["stderr"]), attempts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/experiment_matrix.json")
    ap.add_argument("--outdir", default="results/experiments")
    ap.add_argument("--run-label", default="")
    ap.add_argument("--resume", action="store_true", help="reuse existing label and skip completed run cells")
    ap.add_argument(
        "--resume-verify-hashes",
        action="store_true",
        help="when --resume, verify dataset/metrics sha256 against prior manifest before skipping",
    )
    ap.add_argument("--max-runs", type=int, default=0, help="optional cap on number of run cells executed")
    ap.add_argument("--plan-only", action="store_true", help="write manifest/plan without executing generation or analysis")
    ap.add_argument("--include-run-id", action="append", default=[], help="restrict execution to specific run id(s)")
    ap.add_argument("--run-id-file", default="", help="optional text file with one run id per line")
    ap.add_argument("--manifest-note", default="", help="free-text note stored in manifest for traceability")
    ap.add_argument("--strict-clean", action="store_true", help="fail if git working tree is dirty")
    ap.add_argument("--list-run-ids", action="store_true", help="print run ids from config and exit")
    ap.add_argument("--selection-report", default="", help="optional JSON path for selected scenario/persona counts")
    ap.add_argument("--print-selection", action="store_true", help="print selected scenario/persona counts per run id")
    ap.add_argument("--selection-csv", default="", help="optional CSV path for selected scenario/persona counts")
    ap.add_argument("--require-min-scenarios", type=int, default=0, help="fail if a run selects fewer than this many scenarios")
    ap.add_argument("--require-min-personas", type=int, default=0, help="fail if a run selects fewer than this many personas")
    ap.add_argument("--require-min-temperature-count", type=int, default=0, help="fail if a run uses fewer than this many temperatures")
    ap.add_argument(
        "--require-min-unique-scenario-domains",
        type=int,
        default=0,
        help="fail if a run selects fewer than this many unique scenario domains",
    )
    ap.add_argument(
        "--require-min-unique-scenario-emotion-axes",
        type=int,
        default=0,
        help="fail if a run selects fewer than this many unique scenario emotion axes",
    )
    ap.add_argument(
        "--require-min-unique-scenario-difficulties",
        type=int,
        default=0,
        help="fail if a run selects fewer than this many unique scenario difficulty levels",
    )
    ap.add_argument("--fail-on-missing-run-id", action="store_true", help="fail when --include-run-id contains unknown ids")
    ap.add_argument("--manifest-markdown", action="store_true", help="emit a human-readable manifest summary markdown")
    ap.add_argument("--require-min-run-cells", type=int, default=0, help="fail if selected run cells are fewer than this minimum")
    ap.add_argument("--require-min-successful-cells", type=int, default=0, help="fail if successfully executed or resumed cells are fewer than this minimum")
    ap.add_argument(
        "--require-min-success-rate",
        type=float,
        default=0.0,
        help="fail if successful_cells/selected_run_cells is below this ratio (0 disables)",
    )
    ap.add_argument(
        "--require-min-run-id-success-rate",
        type=float,
        default=0.0,
        help="fail if any selected run-id success rate falls below this ratio (0 disables)",
    )
    ap.add_argument(
        "--require-min-successful-cells-per-run-id",
        type=int,
        default=0,
        help="fail if any selected run id has fewer than this many successful cells (0 disables)",
    )
    ap.add_argument(
        "--require-min-generation-success-rate",
        type=float,
        default=0.0,
        help="fail if generation stage success rate falls below this ratio (0 disables)",
    )
    ap.add_argument(
        "--require-min-analysis-success-rate",
        type=float,
        default=0.0,
        help="fail if analysis stage success rate falls below this ratio (0 disables)",
    )
    ap.add_argument("--require-min-condition-cells", type=int, default=0, help="fail if any run selects fewer than this many scenario×persona×temperature condition cells")
    ap.add_argument("--require-min-total-samples", type=int, default=0, help="fail if total selected samples (sum of n×condition_cells×repeats) is below this threshold")
    ap.add_argument("--require-min-run-ids", type=int, default=0, help="fail if selected unique run ids are fewer than this minimum")
    ap.add_argument(
        "--require-min-planned-samples-per-run",
        type=int,
        default=0,
        help="fail if any selected run id plans fewer than this many total samples (n × condition_cells × repeats)",
    )
    ap.add_argument("--manifest-note-file", default="", help="optional markdown/text file appended to manifest_note for reproducible run context")
    ap.add_argument("--require-min-repeats", type=int, default=0, help="fail if a run config has fewer repeats than this minimum")
    ap.add_argument(
        "--require-min-temperature-span",
        type=float,
        default=0.0,
        help="fail if max(temperature)-min(temperature) is below this minimum for any selected run",
    )
    ap.add_argument(
        "--require-min-unique-scenario-tags",
        type=int,
        default=0,
        help="fail if a selected run has fewer than this many unique scenario tags",
    )
    ap.add_argument(
        "--require-min-unique-scenario-labels",
        type=int,
        default=0,
        help="fail if a selected run has fewer than this many unique scenario labels",
    )
    ap.add_argument(
        "--require-max-scenario-label-dominance",
        type=float,
        default=0.0,
        help="fail if a selected run has one scenario label above this share (0 disables)",
    )
    ap.add_argument(
        "--require-min-scenario-label-entropy",
        type=float,
        default=0.0,
        help="fail if a selected run has normalized scenario label entropy below this value (0 disables)",
    )
    ap.add_argument(
        "--require-min-scenario-domain-entropy",
        type=float,
        default=0.0,
        help="fail if a selected run has normalized scenario domain entropy below this value (0 disables)",
    )
    ap.add_argument(
        "--require-min-scenario-emotion-axis-entropy",
        type=float,
        default=0.0,
        help="fail if a selected run has normalized scenario emotion-axis entropy below this value (0 disables)",
    )
    ap.add_argument(
        "--require-min-unique-persona-style-tags",
        type=int,
        default=0,
        help="fail if a selected run has fewer than this many unique persona style tags",
    )
    ap.add_argument(
        "--require-min-selected-scenarios",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique scenario ids in total",
    )
    ap.add_argument(
        "--require-min-selected-personas",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique persona ids in total",
    )
    ap.add_argument(
        "--require-min-selected-scenario-tags",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique scenario tags in total",
    )
    ap.add_argument(
        "--require-min-selected-scenario-labels",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique scenario labels in total",
    )
    ap.add_argument(
        "--require-min-selected-scenario-domains",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique scenario domains in total",
    )
    ap.add_argument(
        "--require-min-selected-scenario-emotion-axes",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique scenario emotion axes in total",
    )
    ap.add_argument(
        "--require-min-selected-scenario-difficulties",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique scenario difficulty levels in total",
    )
    ap.add_argument(
        "--require-min-selected-persona-style-tags",
        type=int,
        default=0,
        help="fail if the selected batch covers fewer than this many unique persona style tags in total",
    )
    ap.add_argument(
        "--require-prompt-bank-version",
        default="",
        help="fail if selected run prompt-bank version does not match this exact value",
    )
    ap.add_argument(
        "--require-freeze-artifact",
        action="append",
        default=[],
        help="relative path(s) that must exist before execution for evidence freeze discipline",
    )
    ap.add_argument("--max-retries", type=int, default=0, help="retry each generation/analysis command up to N additional times")
    ap.add_argument(
        "--max-generation-retries",
        type=int,
        default=-1,
        help="override retry budget for generation stage only (-1 uses --max-retries)",
    )
    ap.add_argument(
        "--max-analysis-retries",
        type=int,
        default=-1,
        help="override retry budget for analysis stage only (-1 uses --max-retries)",
    )
    ap.add_argument(
        "--retry-backoff-seconds",
        type=float,
        default=0.0,
        help="sleep duration between retries when --max-retries > 0",
    )
    ap.add_argument(
        "--generation-timeout-seconds",
        type=float,
        default=0.0,
        help="timeout per generation command (0 disables timeout)",
    )
    ap.add_argument(
        "--analysis-timeout-seconds",
        type=float,
        default=0.0,
        help="timeout per analysis command (0 disables timeout)",
    )
    ap.add_argument(
        "--max-run-seconds",
        type=float,
        default=0.0,
        help="wall-clock ceiling per run cell across generation+analysis (0 disables)",
    )
    ap.add_argument(
        "--execution-log-jsonl",
        default="",
        help="optional JSONL path for per-attempt command logs (defaults to <outdir>/<run-label>/command_log.jsonl)",
    )
    ap.add_argument(
        "--continue-on-error",
        action="store_true",
        help="continue remaining run cells when a generation/analysis command fails",
    )
    ap.add_argument(
        "--max-failed-cells",
        type=int,
        default=0,
        help="when --continue-on-error, stop batch after this many failed cells (0 = no limit)",
    )
    ap.add_argument(
        "--max-failure-rate",
        type=float,
        default=0.0,
        help="when --continue-on-error, stop batch if failed_cells/executed_or_failed exceeds this ratio (0 = no limit)",
    )
    ap.add_argument(
        "--max-failure-streak",
        type=int,
        default=0,
        help="when --continue-on-error, stop batch after this many consecutive failed cells (0 = no limit)",
    )
    ap.add_argument(
        "--max-generation-failure-streak",
        type=int,
        default=0,
        help="stop batch after this many consecutive generation-stage failures (0 = no limit)",
    )
    ap.add_argument(
        "--max-analysis-failure-streak",
        type=int,
        default=0,
        help="stop batch after this many consecutive analysis-stage failures (0 = no limit)",
    )
    ap.add_argument(
        "--max-generation-failure-streak-per-run-id",
        type=int,
        default=0,
        help="skip remaining repeats for a run id after this many consecutive generation-stage failures for that run id (0 = no limit)",
    )
    ap.add_argument(
        "--max-analysis-failure-streak-per-run-id",
        type=int,
        default=0,
        help="skip remaining repeats for a run id after this many consecutive analysis-stage failures for that run id (0 = no limit)",
    )
    ap.add_argument(
        "--max-failure-streak-per-run-id",
        type=int,
        default=0,
        help="when --continue-on-error, skip remaining repeats for a run id after this many consecutive failed cells for that run id (0 = no limit)",
    )
    ap.add_argument(
        "--max-failed-cells-per-run-id",
        type=int,
        default=0,
        help="when --continue-on-error, skip remaining repeats for a run id after this many failed cells (0 = no limit)",
    )
    ap.add_argument(
        "--max-generation-attempts-total",
        type=int,
        default=0,
        help="global ceiling on generation command attempts (including retries); 0 disables",
    )
    ap.add_argument(
        "--max-analysis-attempts-total",
        type=int,
        default=0,
        help="global ceiling on analysis command attempts (including retries); 0 disables",
    )
    ap.add_argument(
        "--max-generation-attempts-per-run-id",
        type=int,
        default=0,
        help="ceiling on generation attempts per run id (including retries); 0 disables",
    )
    ap.add_argument(
        "--max-analysis-attempts-per-run-id",
        type=int,
        default=0,
        help="ceiling on analysis attempts per run id (including retries); 0 disables",
    )
    ap.add_argument(
        "--max-attempts-per-cell",
        type=int,
        default=0,
        help="ceiling on total attempts per run cell (generation+analysis, including retries); 0 disables",
    )
    ap.add_argument(
        "--max-attempt-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id consumes more than this share of total attempts; 0 disables",
    )
    ap.add_argument(
        "--max-generation-attempt-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id consumes more than this share of total generation attempts; 0 disables",
    )
    ap.add_argument(
        "--max-analysis-attempt-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id consumes more than this share of total analysis attempts; 0 disables",
    )
    ap.add_argument(
        "--max-live-generation-attempt-share-per-run-id",
        type=float,
        default=0.0,
        help="stop early if a run id exceeds this share of generation attempts while batch is running; 0 disables",
    )
    ap.add_argument(
        "--max-live-analysis-attempt-share-per-run-id",
        type=float,
        default=0.0,
        help="stop early if a run id exceeds this share of analysis attempts while batch is running; 0 disables",
    )
    ap.add_argument(
        "--max-live-combined-attempt-share-per-run-id",
        type=float,
        default=0.0,
        help="stop early if a run id exceeds this share of combined attempts while batch is running; 0 disables",
    )
    ap.add_argument(
        "--max-live-stage-attempt-share-gap-per-run-id",
        type=float,
        default=0.0,
        help="stop early if abs(live_generation_attempt_share-live_analysis_attempt_share) for a run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-live-retry-share-per-run-id",
        type=float,
        default=0.0,
        help="stop early if a run id exceeds this share of retries while batch is running; 0 disables",
    )
    ap.add_argument(
        "--max-live-retry-over-selection-ratio-per-run-id",
        type=float,
        default=0.0,
        help="stop early if live retry_share/selected_cell_share for a run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-live-attempt-over-selection-ratio-per-run-id",
        type=float,
        default=0.0,
        help="stop early if live combined_attempt_share/selected_cell_share for a run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-selected-cell-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id occupies more than this share of selected run cells; 0 disables",
    )
    ap.add_argument(
        "--max-selected-cell-share-gap-per-run-id",
        type=float,
        default=0.0,
        help="fail if max(selected_cell_share)-min(selected_cell_share) across selected run ids exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-attempt-over-selection-ratio",
        type=float,
        default=0.0,
        help="fail if a run id consumes attempts at more than this multiple of its selected-cell share; 0 disables",
    )
    ap.add_argument(
        "--max-retry-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id consumes more than this share of retry attempts; 0 disables",
    )
    ap.add_argument(
        "--max-generation-retry-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id consumes more than this share of generation retries; 0 disables",
    )
    ap.add_argument(
        "--max-analysis-retry-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a single run id consumes more than this share of analysis retries; 0 disables",
    )
    ap.add_argument(
        "--max-retry-over-selection-ratio",
        type=float,
        default=0.0,
        help="fail if a run id consumes retry attempts at more than this multiple of its selected-cell share; 0 disables",
    )
    ap.add_argument(
        "--max-generation-attempt-over-selection-ratio",
        type=float,
        default=0.0,
        help="fail if a run id consumes generation attempts at more than this multiple of its selected-cell share; 0 disables",
    )
    ap.add_argument(
        "--max-analysis-attempt-over-selection-ratio",
        type=float,
        default=0.0,
        help="fail if a run id consumes analysis attempts at more than this multiple of its selected-cell share; 0 disables",
    )
    ap.add_argument(
        "--max-stage-attempt-pressure-ratio-per-run-id",
        type=float,
        default=0.0,
        help="fail if max(generation_attempt_over_selection_ratio, analysis_attempt_over_selection_ratio) for any run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-stage-attempt-share-gap-per-run-id",
        type=float,
        default=0.0,
        help="fail if abs(generation_attempt_share-analysis_attempt_share) for any run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-stage-total-attempt-gap-share",
        type=float,
        default=0.0,
        help="fail if abs(generation_attempts_total-analysis_attempts_total)/combined_attempts_total exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-stage-attempt-imbalance-ratio-per-run-id",
        type=float,
        default=0.0,
        help="fail if max(generation_attempts,analysis_attempts)/min(generation_attempts,analysis_attempts) for any run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-stage-total-attempt-imbalance-ratio",
        type=float,
        default=0.0,
        help="fail if max(generation_attempts_total,analysis_attempts_total)/min(generation_attempts_total,analysis_attempts_total) exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--max-failure-over-selection-ratio",
        type=float,
        default=0.0,
        help="fail if a run id accumulates failed-cell share at more than this multiple of its selected-cell share; 0 disables",
    )
    ap.add_argument(
        "--max-failed-cell-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a run id owns more than this share of all failed cells; 0 disables",
    )
    ap.add_argument(
        "--max-timeout-failure-share-per-run-id",
        type=float,
        default=0.0,
        help="fail if a run id owns more than this share of timeout failures (failed_*timeout* statuses); 0 disables",
    )
    ap.add_argument(
        "--max-timeout-failure-over-selection-ratio-per-run-id",
        type=float,
        default=0.0,
        help="fail if timeout_failure_share/selected_cell_share for any run id exceeds this value; 0 disables",
    )
    ap.add_argument(
        "--quarantine-json",
        default="",
        help="optional JSON path for failed run-cell quarantine candidates (defaults to <outdir>/quarantine_candidates.json)",
    )
    ap.add_argument(
        "--quarantine-csv",
        default="",
        help="optional CSV path for failed run-cell quarantine candidates (defaults to <outdir>/quarantine_candidates.csv)",
    )
    ap.add_argument(
        "--budget-report-json",
        default="",
        help="optional JSON path for per-run-id budget pressure summary (defaults to <outdir>/budget_report.json)",
    )
    ap.add_argument(
        "--budget-report-md",
        default="",
        help="optional markdown path for per-run-id budget pressure summary (defaults to <outdir>/budget_report.md)",
    )
    ap.add_argument(
        "--budget-violations-json",
        default="",
        help="optional JSON path for threshold violations derived from budget report (defaults to <outdir>/budget_violations.json)",
    )
    ap.add_argument(
        "--preflight-markdown",
        action="store_true",
        help="emit a human-readable preflight markdown summary",
    )
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    cli_invocation = shell_join([sys.executable, *sys.argv])

    manifest_note = args.manifest_note
    if args.manifest_note_file:
        note_path = ROOT / args.manifest_note_file
        if not note_path.exists():
            raise FileNotFoundError(f"manifest note file not found: {note_path}")
        note_body = note_path.read_text(encoding="utf-8").strip()
        if note_body:
            manifest_note = f"{manifest_note}\n\n{note_body}".strip() if manifest_note else note_body

    if args.list_run_ids:
        for exp in cfg.get("runs", []):
            print(exp.get("id", "<missing-id>"))
        return

    git_status = get_git_status()
    if args.strict_clean and git_status.get("dirty"):
        raise RuntimeError("git working tree is dirty; commit/stash changes or run without --strict-clean")

    generation_retry_budget = args.max_retries if args.max_generation_retries < 0 else args.max_generation_retries
    analysis_retry_budget = args.max_retries if args.max_analysis_retries < 0 else args.max_analysis_retries
    if generation_retry_budget < 0 or analysis_retry_budget < 0:
        raise RuntimeError("retry budget cannot be negative")

    label = args.run_label.strip() or utc_stamp()
    outdir = ROOT / args.outdir / label
    outdir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = outdir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    execution_log_path = ROOT / args.execution_log_jsonl if args.execution_log_jsonl else outdir / "command_log.jsonl"
    if execution_log_path.parent != outdir.parent:
        execution_log_path.parent.mkdir(parents=True, exist_ok=True)
    quarantine_json_path = ROOT / args.quarantine_json if args.quarantine_json else outdir / "quarantine_candidates.json"
    quarantine_csv_path = ROOT / args.quarantine_csv if args.quarantine_csv else outdir / "quarantine_candidates.csv"
    if quarantine_json_path.parent != outdir.parent:
        quarantine_json_path.parent.mkdir(parents=True, exist_ok=True)
    if quarantine_csv_path.parent != outdir.parent:
        quarantine_csv_path.parent.mkdir(parents=True, exist_ok=True)
    budget_report_json_path = ROOT / args.budget_report_json if args.budget_report_json else outdir / "budget_report.json"
    budget_report_md_path = ROOT / args.budget_report_md if args.budget_report_md else outdir / "budget_report.md"
    budget_violations_json_path = ROOT / args.budget_violations_json if args.budget_violations_json else outdir / "budget_violations.json"
    if budget_report_json_path.parent != outdir.parent:
        budget_report_json_path.parent.mkdir(parents=True, exist_ok=True)
    if budget_report_md_path.parent != outdir.parent:
        budget_report_md_path.parent.mkdir(parents=True, exist_ok=True)
    if budget_violations_json_path.parent != outdir.parent:
        budget_violations_json_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_path = outdir / "manifest.json"
    existing_manifest = {}
    if args.resume and manifest_path.exists():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    resume_verified = []
    completed = set()
    for r in existing_manifest.get("runs", []):
        if r.get("status") != "ok":
            continue
        dataset_rel = r.get("dataset", "")
        metrics_rel = r.get("metrics", "")
        dataset_path = ROOT / dataset_rel
        metrics_path = ROOT / metrics_rel
        if not dataset_path.exists() or not metrics_path.exists():
            continue

        if args.resume and args.resume_verify_hashes:
            expected_dataset_hash = str(r.get("dataset_sha256") or "")
            expected_metrics_hash = str(r.get("metrics_sha256") or "")
            actual_dataset_hash = maybe_file_sha256(dataset_path)
            actual_metrics_hash = maybe_file_sha256(metrics_path)
            if expected_dataset_hash and expected_dataset_hash != actual_dataset_hash:
                raise RuntimeError(
                    f"resume hash mismatch ({r.get('run_key')}): dataset_sha256 expected={expected_dataset_hash} actual={actual_dataset_hash}"
                )
            if expected_metrics_hash and expected_metrics_hash != actual_metrics_hash:
                raise RuntimeError(
                    f"resume hash mismatch ({r.get('run_key')}): metrics_sha256 expected={expected_metrics_hash} actual={actual_metrics_hash}"
                )
            resume_verified.append(
                {
                    "run_key": r.get("run_key"),
                    "dataset_sha256": actual_dataset_hash,
                    "metrics_sha256": actual_metrics_hash,
                }
            )

        completed.add(r.get("run_key"))

    runs = []
    selection_rows = []
    all_metric_paths = []
    batch_started = time.perf_counter()
    run_metric_paths: dict[str, list[Path]] = {}
    executed = 0
    failed_cells = 0
    attempted_run_cells = 0
    generation_attempted_cells = 0
    generation_successful_cells = 0
    analysis_attempted_cells = 0
    analysis_successful_cells = 0
    generation_attempts_total = 0
    analysis_attempts_total = 0
    generation_retries_total = 0
    analysis_retries_total = 0
    generation_attempts_by_run_id: dict[str, int] = {}
    analysis_attempts_by_run_id: dict[str, int] = {}
    generation_retries_by_run_id: dict[str, int] = {}
    analysis_retries_by_run_id: dict[str, int] = {}
    failure_streak = 0
    generation_failure_streak = 0
    analysis_failure_streak = 0
    run_id_failure_streak: dict[str, int] = {}
    run_id_generation_failure_streak: dict[str, int] = {}
    run_id_analysis_failure_streak: dict[str, int] = {}
    selected_run_cells = 0
    failed_cells_by_run_id: dict[str, int] = {}
    selected_total_samples = 0
    planned_samples_by_run: dict[str, int] = {}
    selected_cells_by_run_id: dict[str, int] = {}
    successful_cells_by_run_id: dict[str, int] = {}
    run_preflight_rows: list[dict] = []
    aggregate_scenario_ids: set[str] = set()
    aggregate_persona_ids: set[str] = set()
    aggregate_scenario_tags: set[str] = set()
    aggregate_scenario_domains: set[str] = set()
    aggregate_scenario_emotion_axes: set[str] = set()
    aggregate_scenario_difficulties: set[str] = set()
    aggregate_scenario_labels: set[str] = set()
    aggregate_persona_style_tags: set[str] = set()
    include_run_ids = set(args.include_run_id)
    if args.run_id_file:
        run_id_file = ROOT / args.run_id_file
        if not run_id_file.exists():
            raise FileNotFoundError(f"run id file not found: {run_id_file}")
        include_run_ids |= load_run_ids_from_file(run_id_file)
    selected_run_ids = set()
    executed_ids = []
    prompt_bank_versions = set()
    stop_requested = False

    known_run_ids = {str(exp.get("id")) for exp in cfg.get("runs", []) if exp.get("id")}
    missing_run_ids = sorted(include_run_ids - known_run_ids)
    if args.fail_on_missing_run_id and missing_run_ids:
        raise RuntimeError(f"unknown include-run-id values: {', '.join(missing_run_ids)}")

    freeze_artifacts = []
    missing_freeze_artifacts = []
    for rel in args.require_freeze_artifact:
        rel_path = str(rel).strip()
        if not rel_path:
            continue
        full_path = ROOT / rel_path
        exists = full_path.exists()
        freeze_artifacts.append({"path": rel_path, "exists": exists})
        if not exists:
            missing_freeze_artifacts.append(rel_path)
    if missing_freeze_artifacts:
        raise RuntimeError(
            "missing required freeze artifact(s): " + ", ".join(missing_freeze_artifacts)
        )

    matrix_snapshot = snapshots_dir / "experiment_matrix.json"
    write_json(matrix_snapshot, cfg)

    for exp in cfg.get("runs", []):
        if stop_requested:
            break
        run_id = exp["id"]
        if include_run_ids and run_id not in include_run_ids:
            continue
        selected_run_ids.add(run_id)
        n = int(exp.get("n", 20))
        seed = int(exp.get("seed", 42))
        temperatures = exp.get("temperatures", [0.2, 0.7])
        repeats = int(exp.get("repeats", 1))
        if args.require_min_repeats and repeats < args.require_min_repeats:
            raise RuntimeError(
                f"{run_id}: repeats={repeats} < require_min_repeats={args.require_min_repeats}"
            )
        temp_span = 0.0
        if temperatures:
            temp_span = max(float(t) for t in temperatures) - min(float(t) for t in temperatures)
        if args.require_min_temperature_span and temp_span < args.require_min_temperature_span:
            raise RuntimeError(
                f"{run_id}: temperature_span={round(temp_span, 4)} < require_min_temperature_span={args.require_min_temperature_span}"
            )
        temp_csv = ",".join(str(t) for t in temperatures)
        prompt_bank = exp.get("prompt_bank", "prompts/prompt_bank_ko.json")
        scenario_ids = sorted(parse_csv_set(exp.get("scenario_ids")))
        scenario_tags = sorted(parse_csv_set(exp.get("scenario_tags")))
        scenario_domains = sorted(parse_csv_set(exp.get("scenario_domains")))
        scenario_emotion_axes = sorted(parse_csv_set(exp.get("scenario_emotion_axes")))
        scenario_difficulties = sorted(parse_csv_set(exp.get("scenario_difficulties")))
        persona_ids = sorted(parse_csv_set(exp.get("persona_ids")))
        prompt_bank_path = ROOT / prompt_bank
        bank = load_prompt_bank(prompt_bank_path)
        prompt_summary = summarize_prompt_bank(
            bank,
            set(scenario_ids),
            set(scenario_tags),
            set(scenario_domains),
            set(scenario_emotion_axes),
            set(scenario_difficulties),
            set(persona_ids),
        )
        prompt_bank_version = str(bank.get("version") or "unknown")
        if args.require_prompt_bank_version and prompt_bank_version != args.require_prompt_bank_version:
            raise RuntimeError(
                f"{run_id}: prompt_bank_version={prompt_bank_version} != require_prompt_bank_version={args.require_prompt_bank_version}"
            )
        prompt_bank_versions.add(prompt_bank_version)
        aggregate_scenario_ids.update(prompt_summary["scenario_ids"])
        aggregate_persona_ids.update(prompt_summary["persona_ids"])
        aggregate_scenario_tags.update(prompt_summary["scenario_tags"])
        aggregate_scenario_domains.update(prompt_summary["scenario_domains"])
        aggregate_scenario_emotion_axes.update(prompt_summary["scenario_emotion_axes"])
        aggregate_scenario_difficulties.update(prompt_summary["scenario_difficulties"])
        aggregate_scenario_labels.update(prompt_summary["scenario_labels"])
        aggregate_persona_style_tags.update(prompt_summary["persona_style_tags"])
        condition_cells = prompt_summary["scenario_count"] * prompt_summary["persona_count"] * max(1, len(temperatures))
        planned_samples = n * condition_cells * max(1, repeats)
        planned_samples_by_run[run_id] = planned_samples
        if prompt_summary["scenario_count"] == 0:
            raise RuntimeError(f"{run_id}: no scenarios selected from {prompt_bank}")
        if prompt_summary["persona_count"] == 0:
            raise RuntimeError(f"{run_id}: no personas selected from {prompt_bank}")
        if args.require_min_scenarios and prompt_summary["scenario_count"] < args.require_min_scenarios:
            raise RuntimeError(
                f"{run_id}: scenario_count={prompt_summary['scenario_count']} < require_min_scenarios={args.require_min_scenarios}"
            )
        if args.require_min_personas and prompt_summary["persona_count"] < args.require_min_personas:
            raise RuntimeError(
                f"{run_id}: persona_count={prompt_summary['persona_count']} < require_min_personas={args.require_min_personas}"
            )
        if args.require_min_temperature_count and len(temperatures) < args.require_min_temperature_count:
            raise RuntimeError(
                f"{run_id}: temperature_count={len(temperatures)} < require_min_temperature_count={args.require_min_temperature_count}"
            )

        if args.require_min_condition_cells and condition_cells < args.require_min_condition_cells:
            raise RuntimeError(
                f"{run_id}: condition_cells={condition_cells} < require_min_condition_cells={args.require_min_condition_cells}"
            )
        if args.require_min_unique_scenario_tags and prompt_summary["scenario_tag_count"] < args.require_min_unique_scenario_tags:
            raise RuntimeError(
                f"{run_id}: scenario_tag_count={prompt_summary['scenario_tag_count']} < "
                f"require_min_unique_scenario_tags={args.require_min_unique_scenario_tags}"
            )
        if (
            args.require_min_unique_scenario_domains
            and prompt_summary["scenario_domain_count"] < args.require_min_unique_scenario_domains
        ):
            raise RuntimeError(
                f"{run_id}: scenario_domain_count={prompt_summary['scenario_domain_count']} < "
                f"require_min_unique_scenario_domains={args.require_min_unique_scenario_domains}"
            )
        if (
            args.require_min_unique_scenario_emotion_axes
            and prompt_summary["scenario_emotion_axis_count"] < args.require_min_unique_scenario_emotion_axes
        ):
            raise RuntimeError(
                f"{run_id}: scenario_emotion_axis_count={prompt_summary['scenario_emotion_axis_count']} < "
                f"require_min_unique_scenario_emotion_axes={args.require_min_unique_scenario_emotion_axes}"
            )
        if (
            args.require_min_unique_scenario_difficulties
            and prompt_summary["scenario_difficulty_count"] < args.require_min_unique_scenario_difficulties
        ):
            raise RuntimeError(
                f"{run_id}: scenario_difficulty_count={prompt_summary['scenario_difficulty_count']} < "
                f"require_min_unique_scenario_difficulties={args.require_min_unique_scenario_difficulties}"
            )
        if args.require_min_unique_scenario_labels and prompt_summary["scenario_label_count"] < args.require_min_unique_scenario_labels:
            raise RuntimeError(
                f"{run_id}: scenario_label_count={prompt_summary['scenario_label_count']} < "
                f"require_min_unique_scenario_labels={args.require_min_unique_scenario_labels}"
            )
        if args.require_max_scenario_label_dominance and prompt_summary["scenario_label_dominance"] > args.require_max_scenario_label_dominance:
            raise RuntimeError(
                f"{run_id}: scenario_label_dominance={prompt_summary['scenario_label_dominance']} > "
                f"require_max_scenario_label_dominance={args.require_max_scenario_label_dominance}"
            )
        if args.require_min_scenario_label_entropy and prompt_summary["scenario_label_entropy"] < args.require_min_scenario_label_entropy:
            raise RuntimeError(
                f"{run_id}: scenario_label_entropy={prompt_summary['scenario_label_entropy']} < "
                f"require_min_scenario_label_entropy={args.require_min_scenario_label_entropy}"
            )
        if args.require_min_scenario_domain_entropy and prompt_summary["scenario_domain_entropy"] < args.require_min_scenario_domain_entropy:
            raise RuntimeError(
                f"{run_id}: scenario_domain_entropy={prompt_summary['scenario_domain_entropy']} < "
                f"require_min_scenario_domain_entropy={args.require_min_scenario_domain_entropy}"
            )
        if args.require_min_scenario_emotion_axis_entropy and prompt_summary["scenario_emotion_axis_entropy"] < args.require_min_scenario_emotion_axis_entropy:
            raise RuntimeError(
                f"{run_id}: scenario_emotion_axis_entropy={prompt_summary['scenario_emotion_axis_entropy']} < "
                f"require_min_scenario_emotion_axis_entropy={args.require_min_scenario_emotion_axis_entropy}"
            )
        if (
            args.require_min_unique_persona_style_tags
            and prompt_summary["persona_style_tag_count"] < args.require_min_unique_persona_style_tags
        ):
            raise RuntimeError(
                f"{run_id}: persona_style_tag_count={prompt_summary['persona_style_tag_count']} < "
                f"require_min_unique_persona_style_tags={args.require_min_unique_persona_style_tags}"
            )

        prompt_snapshot = snapshots_dir / f"{run_id}.prompt_bank.json"
        write_json(prompt_snapshot, bank)
        selection_rows.append(
            {
                "id": run_id,
                "prompt_bank": prompt_bank,
                "prompt_bank_version": prompt_bank_version,
                "prompt_bank_fingerprint": file_sha256(prompt_snapshot),
                "scenario_count": prompt_summary["scenario_count"],
                "persona_count": prompt_summary["persona_count"],
                "scenario_ids": prompt_summary["scenario_ids"],
                "scenario_labels": prompt_summary["scenario_labels"],
                "persona_ids": prompt_summary["persona_ids"],
                "temperature_count": len(temperatures),
                "condition_cells": condition_cells,
                "planned_samples": planned_samples,
                "scenario_label_count": prompt_summary["scenario_label_count"],
                "scenario_label_counts": prompt_summary["scenario_label_counts"],
                "scenario_label_dominance": prompt_summary["scenario_label_dominance"],
                "scenario_label_entropy": prompt_summary["scenario_label_entropy"],
                "scenario_tag_count": prompt_summary["scenario_tag_count"],
                "scenario_tags": prompt_summary["scenario_tags"],
                "scenario_domain_count": prompt_summary["scenario_domain_count"],
                "scenario_domains": prompt_summary["scenario_domains"],
                "scenario_domain_counts": prompt_summary["scenario_domain_counts"],
                "scenario_domain_entropy": prompt_summary["scenario_domain_entropy"],
                "scenario_emotion_axis_count": prompt_summary["scenario_emotion_axis_count"],
                "scenario_emotion_axes": prompt_summary["scenario_emotion_axes"],
                "scenario_emotion_axis_counts": prompt_summary["scenario_emotion_axis_counts"],
                "scenario_emotion_axis_entropy": prompt_summary["scenario_emotion_axis_entropy"],
                "scenario_difficulty_count": prompt_summary["scenario_difficulty_count"],
                "scenario_difficulties": prompt_summary["scenario_difficulties"],
                "persona_style_tag_count": prompt_summary["persona_style_tag_count"],
                "persona_style_tags": prompt_summary["persona_style_tags"],
            }
        )
        run_preflight_rows.append(
            {
                "id": run_id,
                "prompt_bank_version": prompt_bank_version,
                "scenario_count": prompt_summary["scenario_count"],
                "persona_count": prompt_summary["persona_count"],
                "temperature_count": len(temperatures),
                "temperature_span": round(temp_span, 4),
                "repeats": repeats,
                "condition_cells": condition_cells,
                "planned_samples": planned_samples,
                "scenario_label_count": prompt_summary["scenario_label_count"],
                "scenario_label_counts": prompt_summary["scenario_label_counts"],
                "scenario_label_dominance": prompt_summary["scenario_label_dominance"],
                "scenario_label_entropy": prompt_summary["scenario_label_entropy"],
                "scenario_labels": prompt_summary["scenario_labels"],
                "scenario_tag_count": prompt_summary["scenario_tag_count"],
                "scenario_tags": prompt_summary["scenario_tags"],
                "scenario_domain_count": prompt_summary["scenario_domain_count"],
                "scenario_domains": prompt_summary["scenario_domains"],
                "scenario_domain_counts": prompt_summary["scenario_domain_counts"],
                "scenario_domain_entropy": prompt_summary["scenario_domain_entropy"],
                "scenario_emotion_axis_count": prompt_summary["scenario_emotion_axis_count"],
                "scenario_emotion_axes": prompt_summary["scenario_emotion_axes"],
                "scenario_emotion_axis_counts": prompt_summary["scenario_emotion_axis_counts"],
                "scenario_emotion_axis_entropy": prompt_summary["scenario_emotion_axis_entropy"],
                "scenario_difficulty_count": prompt_summary["scenario_difficulty_count"],
                "scenario_difficulties": prompt_summary["scenario_difficulties"],
                "persona_style_tag_count": prompt_summary["persona_style_tag_count"],
                "persona_style_tags": prompt_summary["persona_style_tags"],
            }
        )

        run_id_blocked = False
        for rep in range(repeats):
            if run_id_blocked:
                break
            rep_seed = seed + rep
            run_key = f"{run_id}__rep{rep + 1}"
            dataset_path = outdir / f"{run_key}.jsonl"
            metrics_path = outdir / f"{run_key}.metrics.json"

            row = {
                "id": run_id,
                "run_key": run_key,
                "repeat_index": rep + 1,
                "n": n,
                "seed": rep_seed,
                "temperatures": temperatures,
                "prompt_bank": prompt_bank,
                "prompt_bank_version": prompt_bank_version,
                "scenario_ids": scenario_ids,
                "scenario_tags": scenario_tags,
                "scenario_domains": scenario_domains,
                "scenario_emotion_axes": scenario_emotion_axes,
                "scenario_difficulties": scenario_difficulties,
                "scenario_labels": prompt_summary["scenario_labels"],
                "persona_ids": persona_ids,
                "scenario_count": prompt_summary["scenario_count"],
                "persona_count": prompt_summary["persona_count"],
                "temperature_count": len(temperatures),
                "condition_cells": condition_cells,
                "planned_samples": n * condition_cells,
                "scenario_label_count": prompt_summary["scenario_label_count"],
                "persona_style_tag_count": prompt_summary["persona_style_tag_count"],
                "persona_style_tags": prompt_summary["persona_style_tags"],
                "prompt_bank_fingerprint": file_sha256(prompt_snapshot),
                "dataset": str(dataset_path.relative_to(ROOT)),
                "metrics": str(metrics_path.relative_to(ROOT)),
                "status": "planned",
            }
            selected_run_cells += 1
            selected_total_samples += n * condition_cells
            selected_cells_by_run_id[run_id] = selected_cells_by_run_id.get(run_id, 0) + 1

            if run_key in completed:
                row["status"] = "skipped_resume"
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                row["metrics_sha256"] = maybe_file_sha256(metrics_path)
                runs.append(row)
                all_metric_paths.append(metrics_path)
                run_metric_paths.setdefault(run_id, []).append(metrics_path)
                successful_cells_by_run_id[run_id] = successful_cells_by_run_id.get(run_id, 0) + 1
                run_id_failure_streak[run_id] = 0
                run_id_generation_failure_streak[run_id] = 0
                run_id_analysis_failure_streak[run_id] = 0
                continue

            if args.max_runs > 0 and executed >= args.max_runs:
                row["status"] = "skipped_cap"
                runs.append(row)
                continue

            gen_parts = [
                "python3",
                "scripts/generate_dataset.py",
                "--out",
                str(dataset_path),
                "--n",
                str(n),
                "--seed",
                str(rep_seed),
                "--prompt-bank",
                prompt_bank,
                "--temperatures",
                temp_csv,
            ]
            if scenario_ids:
                gen_parts.extend(["--scenario-ids", ",".join(scenario_ids)])
            if scenario_tags:
                gen_parts.extend(["--scenario-tags", ",".join(scenario_tags)])
            if scenario_domains:
                gen_parts.extend(["--scenario-domains", ",".join(scenario_domains)])
            if scenario_emotion_axes:
                gen_parts.extend(["--scenario-emotion-axes", ",".join(scenario_emotion_axes)])
            if scenario_difficulties:
                gen_parts.extend(["--scenario-difficulties", ",".join(scenario_difficulties)])
            if persona_ids:
                gen_parts.extend(["--persona-ids", ",".join(persona_ids)])
            gen_cmd = shell_join(gen_parts)
            analyze_cmd = shell_join(
                ["python3", "scripts/analyze_regret_markers.py", "--in", str(dataset_path), "--out", str(metrics_path)]
            )
            row["generation_command"] = gen_cmd
            row["analysis_command"] = analyze_cmd

            if args.plan_only:
                row["status"] = "planned_only"
                runs.append(row)
                continue

            attempted_run_cells += 1
            if (
                args.max_generation_attempts_per_run_id > 0
                and generation_attempts_by_run_id.get(run_id, 0) >= args.max_generation_attempts_per_run_id
            ):
                row["status"] = "failed_generation_budget"
                row["error"] = (
                    "generation attempt budget exceeded for run id "
                    f"({generation_attempts_by_run_id.get(run_id, 0)}/{args.max_generation_attempts_per_run_id})"
                )
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                if not args.continue_on_error:
                    raise RuntimeError(f"generation budget exceeded for {run_key}: {row['error']}")
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue

            generation_attempted_cells += 1
            cell_started = time.perf_counter()
            code, _, err, gen_attempts = execute_with_retries(
                gen_cmd,
                run_key=run_key,
                stage="generate_dataset",
                max_retries=generation_retry_budget,
                retry_backoff_seconds=max(0.0, args.retry_backoff_seconds),
                execution_log_path=execution_log_path,
                timeout_seconds=args.generation_timeout_seconds,
            )
            row["generation_attempts"] = len(gen_attempts)
            generation_attempts_total += len(gen_attempts)
            generation_attempts_by_run_id[run_id] = generation_attempts_by_run_id.get(run_id, 0) + len(gen_attempts)
            generation_retries = max(0, len(gen_attempts) - 1)
            generation_retries_total += generation_retries
            generation_retries_by_run_id[run_id] = generation_retries_by_run_id.get(run_id, 0) + generation_retries
            exceeded, exceeded_reason = live_attempt_share_exceeded(
                run_id=run_id,
                generation_attempts_by_run_id=generation_attempts_by_run_id,
                analysis_attempts_by_run_id=analysis_attempts_by_run_id,
                generation_attempts_total=generation_attempts_total,
                analysis_attempts_total=analysis_attempts_total,
                generation_retries_by_run_id=generation_retries_by_run_id,
                analysis_retries_by_run_id=analysis_retries_by_run_id,
                generation_retries_total=generation_retries_total,
                analysis_retries_total=analysis_retries_total,
                selected_cells_by_run_id=selected_cells_by_run_id,
                selected_run_cells=selected_run_cells,
                max_live_generation_attempt_share_per_run_id=args.max_live_generation_attempt_share_per_run_id,
                max_live_analysis_attempt_share_per_run_id=args.max_live_analysis_attempt_share_per_run_id,
                max_live_combined_attempt_share_per_run_id=args.max_live_combined_attempt_share_per_run_id,
                max_live_stage_attempt_share_gap_per_run_id=args.max_live_stage_attempt_share_gap_per_run_id,
                max_live_retry_share_per_run_id=args.max_live_retry_share_per_run_id,
                max_live_retry_over_selection_ratio_per_run_id=args.max_live_retry_over_selection_ratio_per_run_id,
                max_live_attempt_over_selection_ratio_per_run_id=args.max_live_attempt_over_selection_ratio_per_run_id,
            )
            if exceeded:
                print(
                    "[WARN] live attempt share ceiling exceeded; stopping batch early "
                    f"({run_key}: {exceeded_reason})"
                )
                stop_requested = True
            if code != 0:
                row["status"] = "failed_generation"
                row["error"] = str(err).strip()
                runs.append(row)
                failed_cells += 1
                generation_failure_streak += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                run_id_generation_failure_streak[run_id] = run_id_generation_failure_streak.get(run_id, 0) + 1
                run_id_analysis_failure_streak[run_id] = 0
                if args.max_generation_failure_streak > 0 and generation_failure_streak >= args.max_generation_failure_streak:
                    print(
                        "[WARN] generation_failure_streak reached max_generation_failure_streak "
                        f"({generation_failure_streak}/{args.max_generation_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if not args.continue_on_error:
                    raise RuntimeError(f"generation failed for {run_key}: {err}")
                if (
                    args.max_generation_failure_streak_per_run_id > 0
                    and run_id_generation_failure_streak.get(run_id, 0) >= args.max_generation_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id generation_failure_streak reached max_generation_failure_streak_per_run_id "
                        f"({run_id}: {run_id_generation_failure_streak.get(run_id, 0)}/{args.max_generation_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue

            if args.max_generation_attempts_total > 0 and generation_attempts_total >= args.max_generation_attempts_total:
                print(f"[WARN] generation_attempts_total reached ceiling ({generation_attempts_total}/{args.max_generation_attempts_total}); stopping batch early")
                stop_requested = True
                break
            if stop_requested:
                row["status"] = "failed_live_attempt_share"
                row["error"] = f"live attempt share ceiling exceeded after generation ({exceeded_reason})"
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                break

            generation_successful_cells += 1
            generation_failure_streak = 0
            run_id_generation_failure_streak[run_id] = 0
            if args.max_attempts_per_cell > 0 and len(gen_attempts) >= args.max_attempts_per_cell:
                row["status"] = "failed_cell_attempt_budget"
                row["error"] = (
                    "cell attempt budget exhausted before analysis "
                    f"({len(gen_attempts)}/{args.max_attempts_per_cell})"
                )
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                if not args.continue_on_error:
                    raise RuntimeError(f"cell attempt budget exceeded for {run_key}: {row['error']}")
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue
            if args.max_run_seconds > 0 and (time.perf_counter() - cell_started) > args.max_run_seconds:
                row["status"] = "failed_run_timeout"
                row["error"] = (
                    f"run cell wall-clock exceeded max_run_seconds={args.max_run_seconds} before analysis"
                )
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                if not args.continue_on_error:
                    raise RuntimeError(f"run timeout for {run_key}: {row['error']}")
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue

            if (
                args.max_analysis_attempts_per_run_id > 0
                and analysis_attempts_by_run_id.get(run_id, 0) >= args.max_analysis_attempts_per_run_id
            ):
                row["status"] = "failed_analysis_budget"
                row["error"] = (
                    "analysis attempt budget exceeded for run id "
                    f"({analysis_attempts_by_run_id.get(run_id, 0)}/{args.max_analysis_attempts_per_run_id})"
                )
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                if not args.continue_on_error:
                    raise RuntimeError(f"analysis budget exceeded for {run_key}: {row['error']}")
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue

            analysis_attempted_cells += 1
            code, _, err2, analyze_attempts = execute_with_retries(
                analyze_cmd,
                run_key=run_key,
                stage="analyze_regret_markers",
                max_retries=analysis_retry_budget,
                retry_backoff_seconds=max(0.0, args.retry_backoff_seconds),
                execution_log_path=execution_log_path,
                timeout_seconds=args.analysis_timeout_seconds,
            )
            row["analysis_attempts"] = len(analyze_attempts)
            analysis_attempts_total += len(analyze_attempts)
            analysis_attempts_by_run_id[run_id] = analysis_attempts_by_run_id.get(run_id, 0) + len(analyze_attempts)
            analysis_retries = max(0, len(analyze_attempts) - 1)
            analysis_retries_total += analysis_retries
            analysis_retries_by_run_id[run_id] = analysis_retries_by_run_id.get(run_id, 0) + analysis_retries
            exceeded, exceeded_reason = live_attempt_share_exceeded(
                run_id=run_id,
                generation_attempts_by_run_id=generation_attempts_by_run_id,
                analysis_attempts_by_run_id=analysis_attempts_by_run_id,
                generation_attempts_total=generation_attempts_total,
                analysis_attempts_total=analysis_attempts_total,
                generation_retries_by_run_id=generation_retries_by_run_id,
                analysis_retries_by_run_id=analysis_retries_by_run_id,
                generation_retries_total=generation_retries_total,
                analysis_retries_total=analysis_retries_total,
                selected_cells_by_run_id=selected_cells_by_run_id,
                selected_run_cells=selected_run_cells,
                max_live_generation_attempt_share_per_run_id=args.max_live_generation_attempt_share_per_run_id,
                max_live_analysis_attempt_share_per_run_id=args.max_live_analysis_attempt_share_per_run_id,
                max_live_combined_attempt_share_per_run_id=args.max_live_combined_attempt_share_per_run_id,
                max_live_stage_attempt_share_gap_per_run_id=args.max_live_stage_attempt_share_gap_per_run_id,
                max_live_retry_share_per_run_id=args.max_live_retry_share_per_run_id,
                max_live_retry_over_selection_ratio_per_run_id=args.max_live_retry_over_selection_ratio_per_run_id,
                max_live_attempt_over_selection_ratio_per_run_id=args.max_live_attempt_over_selection_ratio_per_run_id,
            )
            if exceeded:
                print(
                    "[WARN] live attempt share ceiling exceeded; stopping batch early "
                    f"({run_key}: {exceeded_reason})"
                )
                stop_requested = True
            if code != 0:
                row["status"] = "failed_analysis"
                row["error"] = str(err2).strip()
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                runs.append(row)
                failed_cells += 1
                analysis_failure_streak += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                run_id_analysis_failure_streak[run_id] = run_id_analysis_failure_streak.get(run_id, 0) + 1
                if args.max_analysis_failure_streak > 0 and analysis_failure_streak >= args.max_analysis_failure_streak:
                    print(
                        "[WARN] analysis_failure_streak reached max_analysis_failure_streak "
                        f"({analysis_failure_streak}/{args.max_analysis_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if not args.continue_on_error:
                    raise RuntimeError(f"analysis failed for {run_key}: {err2}")
                if (
                    args.max_analysis_failure_streak_per_run_id > 0
                    and run_id_analysis_failure_streak.get(run_id, 0) >= args.max_analysis_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id analysis_failure_streak reached max_analysis_failure_streak_per_run_id "
                        f"({run_id}: {run_id_analysis_failure_streak.get(run_id, 0)}/{args.max_analysis_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue

            if args.max_analysis_attempts_total > 0 and analysis_attempts_total >= args.max_analysis_attempts_total:
                print(f"[WARN] analysis_attempts_total reached ceiling ({analysis_attempts_total}/{args.max_analysis_attempts_total}); stopping batch early")
                stop_requested = True
                break
            if stop_requested:
                row["status"] = "failed_live_attempt_share"
                row["error"] = f"live attempt share ceiling exceeded after analysis ({exceeded_reason})"
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                row["metrics_sha256"] = maybe_file_sha256(metrics_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                break

            total_cell_attempts = len(gen_attempts) + len(analyze_attempts)
            if args.max_attempts_per_cell > 0 and total_cell_attempts > args.max_attempts_per_cell:
                row["status"] = "failed_cell_attempt_budget"
                row["error"] = (
                    "cell attempt budget exhausted "
                    f"({total_cell_attempts}/{args.max_attempts_per_cell})"
                )
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                row["metrics_sha256"] = maybe_file_sha256(metrics_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                if not args.continue_on_error:
                    raise RuntimeError(f"cell attempt budget exceeded for {run_key}: {row['error']}")
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue

            analysis_successful_cells += 1
            analysis_failure_streak = 0
            run_id_analysis_failure_streak[run_id] = 0
            row["duration_seconds"] = round(time.perf_counter() - cell_started, 3)
            if args.max_run_seconds > 0 and row["duration_seconds"] > args.max_run_seconds:
                row["status"] = "failed_run_timeout"
                row["error"] = f"run cell wall-clock exceeded max_run_seconds={args.max_run_seconds}"
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                row["metrics_sha256"] = maybe_file_sha256(metrics_path)
                runs.append(row)
                failed_cells += 1
                failed_cells_by_run_id[run_id] = failed_cells_by_run_id.get(run_id, 0) + 1
                failure_streak += 1
                run_id_failure_streak[run_id] = run_id_failure_streak.get(run_id, 0) + 1
                if not args.continue_on_error:
                    raise RuntimeError(f"run timeout for {run_key}: {row['error']}")
                if (
                    args.max_failed_cells_per_run_id > 0
                    and failed_cells_by_run_id.get(run_id, 0) >= args.max_failed_cells_per_run_id
                ):
                    print(
                        "[WARN] run-id failed_cells reached max_failed_cells_per_run_id "
                        f"({run_id}: {failed_cells_by_run_id.get(run_id, 0)}/{args.max_failed_cells_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if (
                    args.max_failure_streak_per_run_id > 0
                    and run_id_failure_streak.get(run_id, 0) >= args.max_failure_streak_per_run_id
                ):
                    print(
                        "[WARN] run-id failure_streak reached max_failure_streak_per_run_id "
                        f"({run_id}: {run_id_failure_streak.get(run_id, 0)}/{args.max_failure_streak_per_run_id}); "
                        "skipping remaining repeats for this run id"
                    )
                    run_id_blocked = True
                    continue
                if args.max_failed_cells > 0 and failed_cells >= args.max_failed_cells:
                    print(
                        f"[WARN] failed_cells reached max_failed_cells ({failed_cells}/{args.max_failed_cells}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_streak > 0 and failure_streak >= args.max_failure_streak:
                    print(
                        "[WARN] failure_streak reached max_failure_streak "
                        f"({failure_streak}/{args.max_failure_streak}); stopping batch early"
                    )
                    stop_requested = True
                    break
                if args.max_failure_rate > 0:
                    current_failure_rate = failed_cells / max(1, attempted_run_cells)
                    if current_failure_rate > args.max_failure_rate:
                        print(
                            "[WARN] failure_rate exceeded max_failure_rate "
                            f"({round(current_failure_rate, 4)} > {args.max_failure_rate}); stopping batch early"
                        )
                        stop_requested = True
                        break
                continue
            row["dataset_sha256"] = maybe_file_sha256(dataset_path)
            row["metrics_sha256"] = maybe_file_sha256(metrics_path)
            row["status"] = "ok"
            failure_streak = 0
            run_id_failure_streak[run_id] = 0
            runs.append(row)
            all_metric_paths.append(metrics_path)
            run_metric_paths.setdefault(run_id, []).append(metrics_path)
            successful_cells_by_run_id[run_id] = successful_cells_by_run_id.get(run_id, 0) + 1
            executed += 1
            executed_ids.append(run_key)

    successful_cells = sum(1 for row in runs if row.get("status") in {"ok", "skipped_resume"})
    success_rate = round(successful_cells / max(1, selected_run_cells), 4) if selected_run_cells else 0.0
    generation_success_rate = (
        round(generation_successful_cells / max(1, generation_attempted_cells), 4)
        if generation_attempted_cells
        else 0.0
    )
    analysis_success_rate = (
        round(analysis_successful_cells / max(1, analysis_attempted_cells), 4)
        if analysis_attempted_cells
        else 0.0
    )
    run_id_success_rates = {
        run_id: round(successful_cells_by_run_id.get(run_id, 0) / max(1, selected_cells_by_run_id.get(run_id, 0)), 4)
        for run_id in sorted(selected_cells_by_run_id)
    }
    selected_cell_shares = {
        run_id: pct(selected_cells_by_run_id.get(run_id, 0), selected_run_cells)
        for run_id in sorted(selected_cells_by_run_id)
    }
    selected_cell_share_gap = (
        round(max(selected_cell_shares.values()) - min(selected_cell_shares.values()), 4)
        if len(selected_cell_shares) > 1
        else 0.0
    )
    combined_attempts_by_run_id = {
        run_id: int(generation_attempts_by_run_id.get(run_id, 0) or 0) + int(analysis_attempts_by_run_id.get(run_id, 0) or 0)
        for run_id in sorted(selected_cells_by_run_id)
    }
    combined_attempts_total = generation_attempts_total + analysis_attempts_total
    stage_total_attempt_gap_share = (
        round(abs(generation_attempts_total - analysis_attempts_total) / combined_attempts_total, 4)
        if combined_attempts_total > 0
        else 0.0
    )
    stage_total_attempt_imbalance_ratio = (
        round(max(generation_attempts_total, analysis_attempts_total) / max(1, min(generation_attempts_total, analysis_attempts_total)), 4)
        if combined_attempts_total > 0
        else 0.0
    )
    combined_attempt_shares = {
        run_id: pct(combined_attempts_by_run_id.get(run_id, 0), combined_attempts_total)
        for run_id in sorted(combined_attempts_by_run_id)
    }
    generation_attempt_shares = {
        run_id: pct(generation_attempts_by_run_id.get(run_id, 0), generation_attempts_total)
        for run_id in sorted(selected_cells_by_run_id)
    }
    analysis_attempt_shares = {
        run_id: pct(analysis_attempts_by_run_id.get(run_id, 0), analysis_attempts_total)
        for run_id in sorted(selected_cells_by_run_id)
    }

    if args.require_min_run_cells and selected_run_cells < args.require_min_run_cells:
        raise RuntimeError(
            f"selected_run_cells={selected_run_cells} < require_min_run_cells={args.require_min_run_cells}"
        )
    if args.require_min_successful_cells and successful_cells < args.require_min_successful_cells:
        raise RuntimeError(
            f"successful_cells={successful_cells} < require_min_successful_cells={args.require_min_successful_cells}"
        )
    if args.require_min_success_rate and success_rate < args.require_min_success_rate:
        raise RuntimeError(
            f"success_rate={success_rate} < require_min_success_rate={args.require_min_success_rate}"
        )
    if args.require_min_run_id_success_rate:
        underfilled = [
            f"{run_id}:{rate}"
            for run_id, rate in run_id_success_rates.items()
            if rate < args.require_min_run_id_success_rate
        ]
        if underfilled:
            raise RuntimeError(
                "run-id success rate below floor "
                f"{args.require_min_run_id_success_rate}: {', '.join(underfilled)}"
            )
    if args.require_min_successful_cells_per_run_id:
        underfilled_success_cells = [
            f"{run_id}:{successful_cells_by_run_id.get(run_id, 0)}"
            for run_id in sorted(selected_cells_by_run_id)
            if successful_cells_by_run_id.get(run_id, 0) < args.require_min_successful_cells_per_run_id
        ]
        if underfilled_success_cells:
            raise RuntimeError(
                "run-id successful cell count below floor "
                f"{args.require_min_successful_cells_per_run_id}: {', '.join(underfilled_success_cells)}"
            )
    if args.require_min_generation_success_rate and generation_success_rate < args.require_min_generation_success_rate:
        raise RuntimeError(
            "generation_success_rate="
            f"{generation_success_rate} < require_min_generation_success_rate={args.require_min_generation_success_rate}"
        )
    if args.require_min_analysis_success_rate and analysis_success_rate < args.require_min_analysis_success_rate:
        raise RuntimeError(
            "analysis_success_rate="
            f"{analysis_success_rate} < require_min_analysis_success_rate={args.require_min_analysis_success_rate}"
        )
    if args.require_min_total_samples and selected_total_samples < args.require_min_total_samples:
        raise RuntimeError(
            f"selected_total_samples={selected_total_samples} < require_min_total_samples={args.require_min_total_samples}"
        )
    if args.require_min_run_ids and len(selected_run_ids) < args.require_min_run_ids:
        raise RuntimeError(
            f"selected_run_ids={len(selected_run_ids)} < require_min_run_ids={args.require_min_run_ids}"
        )
    if args.require_min_selected_scenarios and len(aggregate_scenario_ids) < args.require_min_selected_scenarios:
        raise RuntimeError(
            "selected_unique_scenarios="
            f"{len(aggregate_scenario_ids)} < require_min_selected_scenarios={args.require_min_selected_scenarios}"
        )
    if args.require_min_selected_personas and len(aggregate_persona_ids) < args.require_min_selected_personas:
        raise RuntimeError(
            "selected_unique_personas="
            f"{len(aggregate_persona_ids)} < require_min_selected_personas={args.require_min_selected_personas}"
        )
    if args.require_min_selected_scenario_tags and len(aggregate_scenario_tags) < args.require_min_selected_scenario_tags:
        raise RuntimeError(
            "selected_unique_scenario_tags="
            f"{len(aggregate_scenario_tags)} < require_min_selected_scenario_tags={args.require_min_selected_scenario_tags}"
        )
    if args.require_min_selected_scenario_labels and len(aggregate_scenario_labels) < args.require_min_selected_scenario_labels:
        raise RuntimeError(
            "selected_unique_scenario_labels="
            f"{len(aggregate_scenario_labels)} < require_min_selected_scenario_labels={args.require_min_selected_scenario_labels}"
        )
    if args.require_min_selected_scenario_domains and len(aggregate_scenario_domains) < args.require_min_selected_scenario_domains:
        raise RuntimeError(
            "selected_unique_scenario_domains="
            f"{len(aggregate_scenario_domains)} < require_min_selected_scenario_domains={args.require_min_selected_scenario_domains}"
        )
    if args.require_min_selected_scenario_emotion_axes and len(aggregate_scenario_emotion_axes) < args.require_min_selected_scenario_emotion_axes:
        raise RuntimeError(
            "selected_unique_scenario_emotion_axes="
            f"{len(aggregate_scenario_emotion_axes)} < require_min_selected_scenario_emotion_axes={args.require_min_selected_scenario_emotion_axes}"
        )
    if args.require_min_selected_scenario_difficulties and len(aggregate_scenario_difficulties) < args.require_min_selected_scenario_difficulties:
        raise RuntimeError(
            "selected_unique_scenario_difficulties="
            f"{len(aggregate_scenario_difficulties)} < require_min_selected_scenario_difficulties={args.require_min_selected_scenario_difficulties}"
        )
    if args.require_min_selected_persona_style_tags and len(aggregate_persona_style_tags) < args.require_min_selected_persona_style_tags:
        raise RuntimeError(
            "selected_unique_persona_style_tags="
            f"{len(aggregate_persona_style_tags)} < require_min_selected_persona_style_tags={args.require_min_selected_persona_style_tags}"
        )
    if args.require_min_planned_samples_per_run:
        underfilled = [
            f"{run_id}:{planned}"
            for run_id, planned in sorted(planned_samples_by_run.items())
            if planned < args.require_min_planned_samples_per_run
        ]
        if underfilled:
            raise RuntimeError(
                "run(s) below require_min_planned_samples_per_run="
                f"{args.require_min_planned_samples_per_run}: {', '.join(underfilled)}"
            )
    if args.max_selected_cell_share_per_run_id:
        overfilled = [
            f"{run_id}:{share}"
            for run_id, share in selected_cell_shares.items()
            if share > args.max_selected_cell_share_per_run_id
        ]
        if overfilled:
            raise RuntimeError(
                "run-id selected cell share above ceiling "
                f"{args.max_selected_cell_share_per_run_id}: {', '.join(overfilled)}"
            )
    if args.max_selected_cell_share_gap_per_run_id and selected_cell_share_gap > args.max_selected_cell_share_gap_per_run_id:
        raise RuntimeError(
            "selected cell share gap above ceiling "
            f"{args.max_selected_cell_share_gap_per_run_id}: observed={selected_cell_share_gap}"
        )
    if args.max_attempt_share_per_run_id:
        overfilled = [
            f"{run_id}:{share}"
            for run_id, share in combined_attempt_shares.items()
            if share > args.max_attempt_share_per_run_id
        ]
        if overfilled:
            raise RuntimeError(
                "run-id attempt share above ceiling "
                f"{args.max_attempt_share_per_run_id}: {', '.join(overfilled)}"
            )
    if args.max_generation_attempt_share_per_run_id:
        over_generation_share = [
            f"{run_id}:{share}"
            for run_id, share in generation_attempt_shares.items()
            if share > args.max_generation_attempt_share_per_run_id
        ]
        if over_generation_share:
            raise RuntimeError(
                "run-id generation attempt share above ceiling "
                f"{args.max_generation_attempt_share_per_run_id}: {', '.join(over_generation_share)}"
            )
    if args.max_analysis_attempt_share_per_run_id:
        over_analysis_share = [
            f"{run_id}:{share}"
            for run_id, share in analysis_attempt_shares.items()
            if share > args.max_analysis_attempt_share_per_run_id
        ]
        if over_analysis_share:
            raise RuntimeError(
                "run-id analysis attempt share above ceiling "
                f"{args.max_analysis_attempt_share_per_run_id}: {', '.join(over_analysis_share)}"
            )
    if args.max_stage_total_attempt_gap_share and stage_total_attempt_gap_share > args.max_stage_total_attempt_gap_share:
        raise RuntimeError(
            "stage total attempt gap share above ceiling "
            f"{args.max_stage_total_attempt_gap_share}: observed={stage_total_attempt_gap_share}"
        )
    if args.max_stage_total_attempt_imbalance_ratio and stage_total_attempt_imbalance_ratio > args.max_stage_total_attempt_imbalance_ratio:
        raise RuntimeError(
            "stage total attempt imbalance ratio above ceiling "
            f"{args.max_stage_total_attempt_imbalance_ratio}: observed={stage_total_attempt_imbalance_ratio}"
        )
    summary = aggregate_metrics(all_metric_paths)
    run_id_summary = aggregate_by_run_id(run_metric_paths)
    preflight_summary = {
        "selected_run_id_count": len(run_preflight_rows),
        "prompt_bank_versions": sorted(prompt_bank_versions),
        "min_scenario_count": min((row.get("scenario_count", 0) for row in run_preflight_rows), default=0),
        "min_persona_count": min((row.get("persona_count", 0) for row in run_preflight_rows), default=0),
        "min_temperature_count": min((row.get("temperature_count", 0) for row in run_preflight_rows), default=0),
        "min_temperature_span": round(min((row.get("temperature_span", 0.0) for row in run_preflight_rows), default=0.0), 4),
        "min_condition_cells": min((row.get("condition_cells", 0) for row in run_preflight_rows), default=0),
        "min_planned_samples": min((row.get("planned_samples", 0) for row in run_preflight_rows), default=0),
        "unique_selected_scenarios": len(aggregate_scenario_ids),
        "unique_selected_personas": len(aggregate_persona_ids),
        "unique_selected_scenario_labels": len(aggregate_scenario_labels),
        "unique_selected_scenario_tags": len(aggregate_scenario_tags),
        "unique_selected_scenario_domains": len(aggregate_scenario_domains),
        "unique_selected_scenario_emotion_axes": len(aggregate_scenario_emotion_axes),
        "unique_selected_scenario_difficulties": len(aggregate_scenario_difficulties),
        "unique_selected_persona_style_tags": len(aggregate_persona_style_tags),
        "max_scenario_label_dominance": max((row.get("scenario_label_dominance", 0.0) for row in run_preflight_rows), default=0.0),
        "min_scenario_label_entropy": min((row.get("scenario_label_entropy", 0.0) for row in run_preflight_rows), default=0.0),
        "min_scenario_domain_entropy": min((row.get("scenario_domain_entropy", 0.0) for row in run_preflight_rows), default=0.0),
        "min_scenario_emotion_axis_entropy": min((row.get("scenario_emotion_axis_entropy", 0.0) for row in run_preflight_rows), default=0.0),
    }
    snapshot_hashes = {
        "experiment_matrix": file_sha256(matrix_snapshot),
        "prompt_banks": {},
    }
    for snap in sorted(snapshots_dir.glob("*.prompt_bank.json")):
        snapshot_hashes["prompt_banks"][snap.name] = file_sha256(snap)

    total_duration_seconds = round(time.perf_counter() - batch_started, 3)
    quarantine_candidates = build_quarantine_candidates(runs)
    write_json(
        quarantine_json_path,
        {
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "run_label": label,
            "failed_cells": len(quarantine_candidates),
            "rows": quarantine_candidates,
        },
    )
    write_quarantine_csv(quarantine_csv_path, quarantine_candidates)
    budget_report = build_budget_report(
        run_label=label,
        selected_cells_by_run_id=selected_cells_by_run_id,
        successful_cells_by_run_id=successful_cells_by_run_id,
        failed_cells_by_run_id=failed_cells_by_run_id,
        generation_attempts_by_run_id=generation_attempts_by_run_id,
        analysis_attempts_by_run_id=analysis_attempts_by_run_id,
        generation_retries_by_run_id=generation_retries_by_run_id,
        analysis_retries_by_run_id=analysis_retries_by_run_id,
        selected_run_cells=selected_run_cells,
        generation_attempts_total=generation_attempts_total,
        analysis_attempts_total=analysis_attempts_total,
        generation_retries_total=generation_retries_total,
        analysis_retries_total=analysis_retries_total,
        failed_cells_total=failed_cells,
    )
    timeout_failure_statuses = {
        "failed_run_timeout",
        "failed_generation_timeout",
        "failed_analysis_timeout",
    }
    timeout_failures_by_run_id: dict[str, int] = {}
    timeout_failures_total = 0
    for run_row in runs:
        status = str(run_row.get("status") or "")
        if "timeout" not in status and "timeout_after_seconds=" not in str(run_row.get("error") or ""):
            continue
        run_id = str(run_row.get("id") or "")
        if not run_id:
            continue
        timeout_failures_total += 1
        timeout_failures_by_run_id[run_id] = timeout_failures_by_run_id.get(run_id, 0) + 1

    budget_violations = []
    if args.max_attempt_over_selection_ratio:
        overpressured = [
            f"{row.get('id')}:{row.get('attempt_over_selection_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("attempt_over_selection_ratio") or 0.0) > args.max_attempt_over_selection_ratio
        ]
        if overpressured:
            budget_violations.append({"rule": "max_attempt_over_selection_ratio", "threshold": args.max_attempt_over_selection_ratio, "violations": overpressured})
    if args.max_retry_share_per_run_id:
        over_retry_share = [
            f"{row.get('id')}:{row.get('retry_share')}"
            for row in budget_report.get("rows") or []
            if float(row.get("retry_share") or 0.0) > args.max_retry_share_per_run_id
        ]
        if over_retry_share:
            budget_violations.append({"rule": "max_retry_share_per_run_id", "threshold": args.max_retry_share_per_run_id, "violations": over_retry_share})
    if args.max_generation_retry_share_per_run_id:
        over_generation_retry_share = [
            f"{row.get('id')}:{row.get('generation_retry_share')}"
            for row in budget_report.get("rows") or []
            if float(row.get("generation_retry_share") or 0.0) > args.max_generation_retry_share_per_run_id
        ]
        if over_generation_retry_share:
            budget_violations.append({"rule": "max_generation_retry_share_per_run_id", "threshold": args.max_generation_retry_share_per_run_id, "violations": over_generation_retry_share})
    if args.max_analysis_retry_share_per_run_id:
        over_analysis_retry_share = [
            f"{row.get('id')}:{row.get('analysis_retry_share')}"
            for row in budget_report.get("rows") or []
            if float(row.get("analysis_retry_share") or 0.0) > args.max_analysis_retry_share_per_run_id
        ]
        if over_analysis_retry_share:
            budget_violations.append({"rule": "max_analysis_retry_share_per_run_id", "threshold": args.max_analysis_retry_share_per_run_id, "violations": over_analysis_retry_share})
    if args.max_retry_over_selection_ratio:
        over_retry_pressure = [
            f"{row.get('id')}:{row.get('retry_over_selection_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("retry_over_selection_ratio") or 0.0) > args.max_retry_over_selection_ratio
        ]
        if over_retry_pressure:
            budget_violations.append({"rule": "max_retry_over_selection_ratio", "threshold": args.max_retry_over_selection_ratio, "violations": over_retry_pressure})
    if args.max_generation_attempt_over_selection_ratio:
        overpressured_generation = [
            f"{row.get('id')}:{row.get('generation_attempt_over_selection_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("generation_attempt_over_selection_ratio") or 0.0)
            > args.max_generation_attempt_over_selection_ratio
        ]
        if overpressured_generation:
            budget_violations.append({"rule": "max_generation_attempt_over_selection_ratio", "threshold": args.max_generation_attempt_over_selection_ratio, "violations": overpressured_generation})
    if args.max_analysis_attempt_over_selection_ratio:
        overpressured_analysis = [
            f"{row.get('id')}:{row.get('analysis_attempt_over_selection_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("analysis_attempt_over_selection_ratio") or 0.0)
            > args.max_analysis_attempt_over_selection_ratio
        ]
        if overpressured_analysis:
            budget_violations.append({"rule": "max_analysis_attempt_over_selection_ratio", "threshold": args.max_analysis_attempt_over_selection_ratio, "violations": overpressured_analysis})
    if args.max_stage_attempt_pressure_ratio_per_run_id:
        overpressured_stage = [
            f"{row.get('id')}:{row.get('stage_attempt_pressure_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("stage_attempt_pressure_ratio") or 0.0)
            > args.max_stage_attempt_pressure_ratio_per_run_id
        ]
        if overpressured_stage:
            budget_violations.append({"rule": "max_stage_attempt_pressure_ratio_per_run_id", "threshold": args.max_stage_attempt_pressure_ratio_per_run_id, "violations": overpressured_stage})
    if args.max_stage_attempt_share_gap_per_run_id:
        overpressured_stage_gap = [
            f"{row.get('id')}:{row.get('stage_attempt_share_gap')}"
            for row in budget_report.get("rows") or []
            if float(row.get("stage_attempt_share_gap") or 0.0) > args.max_stage_attempt_share_gap_per_run_id
        ]
        if overpressured_stage_gap:
            budget_violations.append({"rule": "max_stage_attempt_share_gap_per_run_id", "threshold": args.max_stage_attempt_share_gap_per_run_id, "violations": overpressured_stage_gap})
    if args.max_stage_attempt_imbalance_ratio_per_run_id:
        overpressured_stage_imbalance = [
            f"{row.get('id')}:{row.get('stage_attempt_imbalance_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("stage_attempt_imbalance_ratio") or 0.0) > args.max_stage_attempt_imbalance_ratio_per_run_id
        ]
        if overpressured_stage_imbalance:
            budget_violations.append({"rule": "max_stage_attempt_imbalance_ratio_per_run_id", "threshold": args.max_stage_attempt_imbalance_ratio_per_run_id, "violations": overpressured_stage_imbalance})
    if args.max_failure_over_selection_ratio:
        overpressured_failures = [
            f"{row.get('id')}:{row.get('failure_over_selection_ratio')}"
            for row in budget_report.get("rows") or []
            if float(row.get("failure_over_selection_ratio") or 0.0) > args.max_failure_over_selection_ratio
        ]
        if overpressured_failures:
            budget_violations.append({"rule": "max_failure_over_selection_ratio", "threshold": args.max_failure_over_selection_ratio, "violations": overpressured_failures})
    if args.max_failed_cell_share_per_run_id:
        overfailed_share = [
            f"{row.get('id')}:{row.get('failed_cell_share')}"
            for row in budget_report.get("rows") or []
            if float(row.get("failed_cell_share") or 0.0) > args.max_failed_cell_share_per_run_id
        ]
        if overfailed_share:
            budget_violations.append({"rule": "max_failed_cell_share_per_run_id", "threshold": args.max_failed_cell_share_per_run_id, "violations": overfailed_share})
    if args.max_timeout_failure_share_per_run_id and timeout_failures_total > 0:
        over_timeout_share = [
            f"{run_id}:{round(count / timeout_failures_total, 4)}"
            for run_id, count in sorted(timeout_failures_by_run_id.items())
            if (count / timeout_failures_total) > args.max_timeout_failure_share_per_run_id
        ]
        if over_timeout_share:
            budget_violations.append({
                "rule": "max_timeout_failure_share_per_run_id",
                "threshold": args.max_timeout_failure_share_per_run_id,
                "violations": over_timeout_share,
            })
    if args.max_timeout_failure_over_selection_ratio_per_run_id and timeout_failures_total > 0 and selected_run_cells > 0:
        over_timeout_pressure = []
        for run_id, count in sorted(timeout_failures_by_run_id.items()):
            timeout_share = count / timeout_failures_total
            selected_share = int(selected_cells_by_run_id.get(run_id, 0) or 0) / max(1, selected_run_cells)
            if selected_share <= 0:
                continue
            ratio = timeout_share / selected_share
            if ratio > args.max_timeout_failure_over_selection_ratio_per_run_id:
                over_timeout_pressure.append(f"{run_id}:{round(ratio, 4)}")
        if over_timeout_pressure:
            budget_violations.append({
                "rule": "max_timeout_failure_over_selection_ratio_per_run_id",
                "threshold": args.max_timeout_failure_over_selection_ratio_per_run_id,
                "violations": over_timeout_pressure,
            })
    write_json(budget_report_json_path, budget_report)
    write_budget_report_markdown(budget_report_md_path, budget_report)
    write_json(
        budget_violations_json_path,
        {
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "run_label": label,
            "violation_count": len(budget_violations),
            "violations": budget_violations,
        },
    )
    if budget_violations:
        detail = "; ".join(
            f"{row['rule']}>{row['threshold']}: {', '.join(row['violations'])}" for row in budget_violations
        )
        raise RuntimeError(f"budget threshold violation(s): {detail}")
    reproduce_script = outdir / "reproduce.sh"
    preflight_json_path = outdir / "preflight.json"
    preflight_csv_path = outdir / "preflight.csv"
    write_reproduce_script(reproduce_script, label, args.config, runs)
    write_json(
        preflight_json_path,
        {
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "config": args.config,
            "run_label": label,
            "selected_run_ids": sorted(selected_run_ids),
            "summary": preflight_summary,
            "require_prompt_bank_version": args.require_prompt_bank_version,
            "freeze_artifacts": freeze_artifacts,
            "rows": run_preflight_rows,
        },
    )
    write_preflight_csv(preflight_csv_path, run_preflight_rows)
    if args.preflight_markdown:
        write_preflight_markdown(
            outdir / "preflight.md",
            {
                "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                "config": args.config,
                "run_label": label,
                "selected_run_ids": sorted(selected_run_ids),
                "summary": preflight_summary,
                "rows": run_preflight_rows,
            },
        )

    manifest = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "config": args.config,
        "config_fingerprint": config_fingerprint(cfg),
        "run_label": label,
        "resume_mode": args.resume,
        "manifest_note": manifest_note,
        "manifest_note_file": args.manifest_note_file,
        "cli_invocation": cli_invocation,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git_commit": get_git_commit(),
            "git_status": git_status,
        },
        "summary": summary,
        "preflight_summary": preflight_summary,
        "run_id_summary": run_id_summary,
        "snapshot_hashes": snapshot_hashes,
        "selected_run_ids": sorted(selected_run_ids),
        "selected_run_id_count": len(selected_run_ids),
        "missing_run_ids": missing_run_ids,
        "plan_only": args.plan_only,
        "executed_run_keys": executed_ids,
        "failed_cells": failed_cells,
        "attempted_run_cells": attempted_run_cells,
        "failure_rate": round(failed_cells / max(1, attempted_run_cells), 4) if attempted_run_cells else 0.0,
        "continue_on_error": args.continue_on_error,
        "max_failed_cells": args.max_failed_cells,
        "max_failure_rate": args.max_failure_rate,
        "max_failure_streak": args.max_failure_streak,
        "max_generation_failure_streak": args.max_generation_failure_streak,
        "max_analysis_failure_streak": args.max_analysis_failure_streak,
        "max_generation_failure_streak_per_run_id": args.max_generation_failure_streak_per_run_id,
        "max_analysis_failure_streak_per_run_id": args.max_analysis_failure_streak_per_run_id,
        "max_failure_streak_per_run_id": args.max_failure_streak_per_run_id,
        "max_failed_cells_per_run_id": args.max_failed_cells_per_run_id,
        "failed_cells_by_run_id": failed_cells_by_run_id,
        "max_generation_attempts_total": args.max_generation_attempts_total,
        "max_analysis_attempts_total": args.max_analysis_attempts_total,
        "max_generation_attempts_per_run_id": args.max_generation_attempts_per_run_id,
        "max_analysis_attempts_per_run_id": args.max_analysis_attempts_per_run_id,
        "max_attempts_per_cell": args.max_attempts_per_cell,
        "generation_attempts_by_run_id": generation_attempts_by_run_id,
        "analysis_attempts_by_run_id": analysis_attempts_by_run_id,
        "final_failure_streak": failure_streak,
        "final_generation_failure_streak": generation_failure_streak,
        "final_analysis_failure_streak": analysis_failure_streak,
        "final_run_id_failure_streak": run_id_failure_streak,
        "final_run_id_generation_failure_streak": run_id_generation_failure_streak,
        "final_run_id_analysis_failure_streak": run_id_analysis_failure_streak,
        "stopped_early": stop_requested,
        "selected_run_cells": selected_run_cells,
        "successful_cells": successful_cells,
        "success_rate": success_rate,
        "generation_attempted_cells": generation_attempted_cells,
        "generation_successful_cells": generation_successful_cells,
        "generation_success_rate": generation_success_rate,
        "analysis_attempted_cells": analysis_attempted_cells,
        "analysis_successful_cells": analysis_successful_cells,
        "analysis_success_rate": analysis_success_rate,
        "generation_attempts_total": generation_attempts_total,
        "analysis_attempts_total": analysis_attempts_total,
        "generation_retries_total": generation_retries_total,
        "analysis_retries_total": analysis_retries_total,
        "generation_retries_by_run_id": generation_retries_by_run_id,
        "analysis_retries_by_run_id": analysis_retries_by_run_id,
        "run_id_success_rates": run_id_success_rates,
        "selected_total_samples": selected_total_samples,
        "planned_samples_by_run": planned_samples_by_run,
        "require_min_condition_cells": args.require_min_condition_cells,
        "require_min_successful_cells": args.require_min_successful_cells,
        "require_min_success_rate": args.require_min_success_rate,
        "require_min_run_id_success_rate": args.require_min_run_id_success_rate,
        "require_min_successful_cells_per_run_id": args.require_min_successful_cells_per_run_id,
        "require_min_generation_success_rate": args.require_min_generation_success_rate,
        "require_min_analysis_success_rate": args.require_min_analysis_success_rate,
        "require_min_temperature_count": args.require_min_temperature_count,
        "require_min_total_samples": args.require_min_total_samples,
        "require_min_run_ids": args.require_min_run_ids,
        "require_min_planned_samples_per_run": args.require_min_planned_samples_per_run,
        "require_min_repeats": args.require_min_repeats,
        "require_min_temperature_span": args.require_min_temperature_span,
        "require_min_unique_scenario_labels": args.require_min_unique_scenario_labels,
        "require_max_scenario_label_dominance": args.require_max_scenario_label_dominance,
        "require_min_scenario_label_entropy": args.require_min_scenario_label_entropy,
        "require_min_unique_scenario_tags": args.require_min_unique_scenario_tags,
        "require_min_unique_persona_style_tags": args.require_min_unique_persona_style_tags,
        "require_min_selected_scenario_labels": args.require_min_selected_scenario_labels,
        "require_min_selected_scenario_tags": args.require_min_selected_scenario_tags,
        "require_min_selected_scenario_domains": args.require_min_selected_scenario_domains,
        "require_min_selected_scenario_emotion_axes": args.require_min_selected_scenario_emotion_axes,
        "require_min_selected_scenario_difficulties": args.require_min_selected_scenario_difficulties,
        "require_min_selected_persona_style_tags": args.require_min_selected_persona_style_tags,
        "require_prompt_bank_version": args.require_prompt_bank_version,
        "resume_verify_hashes": args.resume_verify_hashes,
        "resume_verified": resume_verified,
        "run_id_file": args.run_id_file,
        "max_retries": args.max_retries,
        "max_generation_retries": generation_retry_budget,
        "max_analysis_retries": analysis_retry_budget,
        "retry_backoff_seconds": args.retry_backoff_seconds,
        "generation_timeout_seconds": args.generation_timeout_seconds,
        "analysis_timeout_seconds": args.analysis_timeout_seconds,
        "max_run_seconds": args.max_run_seconds,
        "execution_log_jsonl": str(execution_log_path.relative_to(ROOT)),
        "quarantine_json": str(quarantine_json_path.relative_to(ROOT)),
        "quarantine_csv": str(quarantine_csv_path.relative_to(ROOT)),
        "quarantine_failed_cells": len(quarantine_candidates),
        "budget_report_json": str(budget_report_json_path.relative_to(ROOT)),
        "budget_report_md": str(budget_report_md_path.relative_to(ROOT)),
        "budget_violations_json": str(budget_violations_json_path.relative_to(ROOT)),
        "budget_violation_count": len(budget_violations),
        "budget_violations": budget_violations,
        "budget_report_summary": budget_report.get("summary") or {},
        "selected_cell_shares": selected_cell_shares,
        "selected_cell_share_gap": selected_cell_share_gap,
        "combined_attempt_shares": combined_attempt_shares,
        "generation_attempt_shares": generation_attempt_shares,
        "analysis_attempt_shares": analysis_attempt_shares,
        "max_attempt_share_per_run_id": args.max_attempt_share_per_run_id,
        "max_generation_attempt_share_per_run_id": args.max_generation_attempt_share_per_run_id,
        "max_analysis_attempt_share_per_run_id": args.max_analysis_attempt_share_per_run_id,
        "max_live_generation_attempt_share_per_run_id": args.max_live_generation_attempt_share_per_run_id,
        "max_live_analysis_attempt_share_per_run_id": args.max_live_analysis_attempt_share_per_run_id,
        "max_live_combined_attempt_share_per_run_id": args.max_live_combined_attempt_share_per_run_id,
        "max_live_stage_attempt_share_gap_per_run_id": args.max_live_stage_attempt_share_gap_per_run_id,
        "max_live_retry_share_per_run_id": args.max_live_retry_share_per_run_id,
        "max_live_retry_over_selection_ratio_per_run_id": args.max_live_retry_over_selection_ratio_per_run_id,
        "max_live_attempt_over_selection_ratio_per_run_id": args.max_live_attempt_over_selection_ratio_per_run_id,
        "max_selected_cell_share_per_run_id": args.max_selected_cell_share_per_run_id,
        "max_selected_cell_share_gap_per_run_id": args.max_selected_cell_share_gap_per_run_id,
        "max_attempt_over_selection_ratio": args.max_attempt_over_selection_ratio,
        "max_retry_share_per_run_id": args.max_retry_share_per_run_id,
        "max_generation_retry_share_per_run_id": args.max_generation_retry_share_per_run_id,
        "max_analysis_retry_share_per_run_id": args.max_analysis_retry_share_per_run_id,
        "max_retry_over_selection_ratio": args.max_retry_over_selection_ratio,
        "max_generation_attempt_over_selection_ratio": args.max_generation_attempt_over_selection_ratio,
        "max_analysis_attempt_over_selection_ratio": args.max_analysis_attempt_over_selection_ratio,
        "max_stage_attempt_pressure_ratio_per_run_id": args.max_stage_attempt_pressure_ratio_per_run_id,
        "max_stage_attempt_share_gap_per_run_id": args.max_stage_attempt_share_gap_per_run_id,
        "max_stage_attempt_imbalance_ratio_per_run_id": args.max_stage_attempt_imbalance_ratio_per_run_id,
        "max_stage_total_attempt_gap_share": args.max_stage_total_attempt_gap_share,
        "max_stage_total_attempt_imbalance_ratio": args.max_stage_total_attempt_imbalance_ratio,
        "stage_total_attempt_gap_share": stage_total_attempt_gap_share,
        "stage_total_attempt_imbalance_ratio": stage_total_attempt_imbalance_ratio,
        "max_failure_over_selection_ratio": args.max_failure_over_selection_ratio,
        "max_failed_cell_share_per_run_id": args.max_failed_cell_share_per_run_id,
        "max_timeout_failure_share_per_run_id": args.max_timeout_failure_share_per_run_id,
        "max_timeout_failure_over_selection_ratio_per_run_id": args.max_timeout_failure_over_selection_ratio_per_run_id,
        "require_freeze_artifacts": args.require_freeze_artifact,
        "freeze_artifacts": freeze_artifacts,
        "run_preflight": run_preflight_rows,
        "duration_seconds": total_duration_seconds,
        "reproduce_script": str(reproduce_script.relative_to(ROOT)),
        "preflight_json": str(preflight_json_path.relative_to(ROOT)),
        "preflight_csv": str(preflight_csv_path.relative_to(ROOT)),
        "preflight_markdown": str((outdir / 'preflight.md').relative_to(ROOT)) if args.preflight_markdown else "",
        "runs": runs,
    }
    write_json(manifest_path, manifest)
    write_runs_csv(outdir / "runs.csv", runs)
    write_run_summary_csv(outdir / "run_id_summary.csv", run_id_summary)

    if args.selection_report:
        selection_payload = {
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "config": args.config,
            "run_label": label,
            "selected_run_ids": sorted(include_run_ids),
            "missing_run_ids": missing_run_ids,
            "rows": selection_rows,
        }
        report_path = ROOT / args.selection_report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(report_path, selection_payload)

    if args.selection_csv:
        selection_csv_path = ROOT / args.selection_csv
        selection_csv_path.parent.mkdir(parents=True, exist_ok=True)
        write_selection_csv(selection_csv_path, selection_rows)

    if args.manifest_markdown:
        write_manifest_markdown(outdir / "manifest.md", manifest)

    if args.print_selection:
        for row in selection_rows:
            rid = row.get("id")
            sc = row.get("scenario_count")
            pc = row.get("persona_count")
            fp = row.get("prompt_bank_fingerprint", "")
            cc = row.get("condition_cells")
            tc = row.get("temperature_count")
            sl = row.get("scenario_label_count")
            st = row.get("scenario_tag_count")
            pst = row.get("persona_style_tag_count")
            print(
                f"selection {rid}: scenarios={sc}, personas={pc}, scenario_labels={sl}, scenario_tags={st}, persona_style_tags={pst}, temps={tc}, "
                f"condition_cells={cc}, prompt_bank_sha256={fp}"
            )

    ok_n = sum(1 for r in runs if r.get("status") == "ok")
    failed_n = sum(1 for r in runs if str(r.get("status","")).startswith("failed_"))
    print(f"[OK] executed {ok_n}/{len(runs)} run cells -> {outdir}")
    print(f"failed_cells: {failed_n}")
    print(f"selected_run_cells: {selected_run_cells}")
    print(f"successful_cells: {successful_cells}")
    print(f"success_rate: {success_rate}")
    print(f"selected_total_samples: {selected_total_samples}")
    if args.plan_only:
        print(f"planned_only: {sum(1 for r in runs if r.get('status') == 'planned_only')}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
