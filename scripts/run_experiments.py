#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import shlex
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: str):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


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


def summarize_prompt_bank(bank: dict, scenario_ids: set[str], scenario_tags: set[str], persona_ids: set[str]) -> dict:
    scenarios = bank.get("scenarios", [])
    personas = bank.get("personas", [])

    selected_scenarios = []
    selected_tags = set()
    for scenario in scenarios:
        row_tags = {str(tag).strip() for tag in scenario.get("tags", []) if str(tag).strip()}
        if scenario_ids and scenario.get("id") not in scenario_ids:
            continue
        if scenario_tags and not scenario_tags.issubset(row_tags):
            continue
        selected_scenarios.append(scenario)
        selected_tags.update(row_tags)

    selected_personas = [persona for persona in personas if not persona_ids or persona.get("id") in persona_ids]
    selected_persona_style_tags = {
        str(tag).strip()
        for persona in selected_personas
        for tag in persona.get("style_tags", [])
        if str(tag).strip()
    }

    return {
        "scenario_count": len(selected_scenarios),
        "persona_count": len(selected_personas),
        "scenario_ids": [row.get("id") for row in selected_scenarios],
        "persona_ids": [row.get("id") for row in selected_personas],
        "scenario_tag_count": len(selected_tags),
        "scenario_tags": sorted(selected_tags),
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
        "scenario_tags",
        "persona_ids",
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
            for field in ("scenario_ids", "scenario_tags", "persona_ids", "persona_style_tags"):
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
        "scenario_tag_count",
        "scenario_tags",
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
            for field in ("scenario_tags", "scenario_ids", "persona_ids", "persona_style_tags"):
                value = out.get(field)
                if isinstance(value, list):
                    out[field] = ",".join(str(v) for v in value)
            w.writerow(out)


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
        "scenario_tag_count",
        "scenario_tags",
        "persona_style_tag_count",
        "persona_style_tags",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            out = {k: row.get(k) for k in keys}
            for field in ("scenario_tags", "persona_style_tags"):
                value = out.get(field)
                if isinstance(value, list):
                    out[field] = ",".join(str(v) for v in value)
            w.writerow(out)


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
        f"- prompt_bank_versions: `{', '.join(preflight_summary.get('prompt_bank_versions', []))}`",
        f"- min_scenario_count: `{preflight_summary.get('min_scenario_count', 0)}`",
        f"- min_persona_count: `{preflight_summary.get('min_persona_count', 0)}`",
        f"- min_temperature_span: `{preflight_summary.get('min_temperature_span', 0.0)}`",
        f"- min_planned_samples: `{preflight_summary.get('min_planned_samples', 0)}`",
        f"- unique_selected_scenarios: `{preflight_summary.get('unique_selected_scenarios', 0)}`",
        f"- unique_selected_personas: `{preflight_summary.get('unique_selected_personas', 0)}`",
        f"- unique_selected_scenario_tags: `{preflight_summary.get('unique_selected_scenario_tags', 0)}`",
        f"- unique_selected_persona_style_tags: `{preflight_summary.get('unique_selected_persona_style_tags', 0)}`",
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
) -> tuple[int, str, str, list[dict]]:
    attempts = []
    for attempt_index in range(max_retries + 1):
        started_at = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
        code, out, err = run(cmd)
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
        "--retry-backoff-seconds",
        type=float,
        default=0.0,
        help="sleep duration between retries when --max-retries > 0",
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

    label = args.run_label.strip() or utc_stamp()
    outdir = ROOT / args.outdir / label
    outdir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = outdir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    execution_log_path = ROOT / args.execution_log_jsonl if args.execution_log_jsonl else outdir / "command_log.jsonl"
    if execution_log_path.parent != outdir.parent:
        execution_log_path.parent.mkdir(parents=True, exist_ok=True)

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
    failure_streak = 0
    selected_run_cells = 0
    selected_total_samples = 0
    planned_samples_by_run: dict[str, int] = {}
    run_preflight_rows: list[dict] = []
    aggregate_scenario_ids: set[str] = set()
    aggregate_persona_ids: set[str] = set()
    aggregate_scenario_tags: set[str] = set()
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
        persona_ids = sorted(parse_csv_set(exp.get("persona_ids")))
        prompt_bank_path = ROOT / prompt_bank
        bank = load_prompt_bank(prompt_bank_path)
        prompt_summary = summarize_prompt_bank(bank, set(scenario_ids), set(scenario_tags), set(persona_ids))
        prompt_bank_version = str(bank.get("version") or "unknown")
        if args.require_prompt_bank_version and prompt_bank_version != args.require_prompt_bank_version:
            raise RuntimeError(
                f"{run_id}: prompt_bank_version={prompt_bank_version} != require_prompt_bank_version={args.require_prompt_bank_version}"
            )
        prompt_bank_versions.add(prompt_bank_version)
        aggregate_scenario_ids.update(prompt_summary["scenario_ids"])
        aggregate_persona_ids.update(prompt_summary["persona_ids"])
        aggregate_scenario_tags.update(prompt_summary["scenario_tags"])
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
                "persona_ids": prompt_summary["persona_ids"],
                "temperature_count": len(temperatures),
                "condition_cells": condition_cells,
                "planned_samples": planned_samples,
                "scenario_tag_count": prompt_summary["scenario_tag_count"],
                "scenario_tags": prompt_summary["scenario_tags"],
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
                "scenario_tag_count": prompt_summary["scenario_tag_count"],
                "scenario_tags": prompt_summary["scenario_tags"],
                "persona_style_tag_count": prompt_summary["persona_style_tag_count"],
                "persona_style_tags": prompt_summary["persona_style_tags"],
            }
        )

        for rep in range(repeats):
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
                "persona_ids": persona_ids,
                "scenario_count": prompt_summary["scenario_count"],
                "persona_count": prompt_summary["persona_count"],
                "temperature_count": len(temperatures),
                "condition_cells": condition_cells,
                "planned_samples": n * condition_cells,
                "persona_style_tag_count": prompt_summary["persona_style_tag_count"],
                "persona_style_tags": prompt_summary["persona_style_tags"],
                "prompt_bank_fingerprint": file_sha256(prompt_snapshot),
                "dataset": str(dataset_path.relative_to(ROOT)),
                "metrics": str(metrics_path.relative_to(ROOT)),
                "status": "planned",
            }
            selected_run_cells += 1
            selected_total_samples += n * condition_cells

            if run_key in completed:
                row["status"] = "skipped_resume"
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                row["metrics_sha256"] = maybe_file_sha256(metrics_path)
                runs.append(row)
                all_metric_paths.append(metrics_path)
                run_metric_paths.setdefault(run_id, []).append(metrics_path)
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
            cell_started = time.perf_counter()
            code, _, err, gen_attempts = execute_with_retries(
                gen_cmd,
                run_key=run_key,
                stage="generate_dataset",
                max_retries=max(0, args.max_retries),
                retry_backoff_seconds=max(0.0, args.retry_backoff_seconds),
                execution_log_path=execution_log_path,
            )
            row["generation_attempts"] = len(gen_attempts)
            if code != 0:
                row["status"] = "failed_generation"
                row["error"] = str(err).strip()
                runs.append(row)
                failed_cells += 1
                failure_streak += 1
                if not args.continue_on_error:
                    raise RuntimeError(f"generation failed for {run_key}: {err}")
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

            code, _, err2, analyze_attempts = execute_with_retries(
                analyze_cmd,
                run_key=run_key,
                stage="analyze_regret_markers",
                max_retries=max(0, args.max_retries),
                retry_backoff_seconds=max(0.0, args.retry_backoff_seconds),
                execution_log_path=execution_log_path,
            )
            row["analysis_attempts"] = len(analyze_attempts)
            if code != 0:
                row["status"] = "failed_analysis"
                row["error"] = str(err2).strip()
                row["dataset_sha256"] = maybe_file_sha256(dataset_path)
                runs.append(row)
                failed_cells += 1
                failure_streak += 1
                if not args.continue_on_error:
                    raise RuntimeError(f"analysis failed for {run_key}: {err2}")
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

            row["duration_seconds"] = round(time.perf_counter() - cell_started, 3)
            row["dataset_sha256"] = maybe_file_sha256(dataset_path)
            row["metrics_sha256"] = maybe_file_sha256(metrics_path)
            row["status"] = "ok"
            failure_streak = 0
            runs.append(row)
            all_metric_paths.append(metrics_path)
            run_metric_paths.setdefault(run_id, []).append(metrics_path)
            executed += 1
            executed_ids.append(run_key)

    successful_cells = sum(1 for row in runs if row.get("status") in {"ok", "skipped_resume"})
    success_rate = round(successful_cells / max(1, selected_run_cells), 4) if selected_run_cells else 0.0

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
        "unique_selected_scenario_tags": len(aggregate_scenario_tags),
        "unique_selected_persona_style_tags": len(aggregate_persona_style_tags),
    }
    snapshot_hashes = {
        "experiment_matrix": file_sha256(matrix_snapshot),
        "prompt_banks": {},
    }
    for snap in sorted(snapshots_dir.glob("*.prompt_bank.json")):
        snapshot_hashes["prompt_banks"][snap.name] = file_sha256(snap)

    total_duration_seconds = round(time.perf_counter() - batch_started, 3)
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
        "final_failure_streak": failure_streak,
        "stopped_early": stop_requested,
        "selected_run_cells": selected_run_cells,
        "successful_cells": successful_cells,
        "success_rate": success_rate,
        "selected_total_samples": selected_total_samples,
        "planned_samples_by_run": planned_samples_by_run,
        "require_min_condition_cells": args.require_min_condition_cells,
        "require_min_successful_cells": args.require_min_successful_cells,
        "require_min_success_rate": args.require_min_success_rate,
        "require_min_temperature_count": args.require_min_temperature_count,
        "require_min_total_samples": args.require_min_total_samples,
        "require_min_run_ids": args.require_min_run_ids,
        "require_min_planned_samples_per_run": args.require_min_planned_samples_per_run,
        "require_min_repeats": args.require_min_repeats,
        "require_min_temperature_span": args.require_min_temperature_span,
        "require_min_unique_scenario_tags": args.require_min_unique_scenario_tags,
        "require_min_unique_persona_style_tags": args.require_min_unique_persona_style_tags,
        "require_min_selected_scenario_tags": args.require_min_selected_scenario_tags,
        "require_min_selected_persona_style_tags": args.require_min_selected_persona_style_tags,
        "require_prompt_bank_version": args.require_prompt_bank_version,
        "resume_verify_hashes": args.resume_verify_hashes,
        "resume_verified": resume_verified,
        "run_id_file": args.run_id_file,
        "max_retries": args.max_retries,
        "retry_backoff_seconds": args.retry_backoff_seconds,
        "execution_log_jsonl": str(execution_log_path.relative_to(ROOT)),
        "require_freeze_artifacts": args.require_freeze_artifact,
        "freeze_artifacts": freeze_artifacts,
        "run_preflight": run_preflight_rows,
        "duration_seconds": total_duration_seconds,
        "reproduce_script": str(reproduce_script.relative_to(ROOT)),
        "preflight_json": str(preflight_json_path.relative_to(ROOT)),
        "preflight_csv": str(preflight_csv_path.relative_to(ROOT)),
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
            st = row.get("scenario_tag_count")
            pst = row.get("persona_style_tag_count")
            print(
                f"selection {rid}: scenarios={sc}, personas={pc}, scenario_tags={st}, persona_style_tags={pst}, temps={tc}, "
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
