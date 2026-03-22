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
    for scenario in scenarios:
        row_tags = {str(tag).strip() for tag in scenario.get("tags", []) if str(tag).strip()}
        if scenario_ids and scenario.get("id") not in scenario_ids:
            continue
        if scenario_tags and not scenario_tags.issubset(row_tags):
            continue
        selected_scenarios.append(scenario)

    selected_personas = [persona for persona in personas if not persona_ids or persona.get("id") in persona_ids]

    return {
        "scenario_count": len(selected_scenarios),
        "persona_count": len(selected_personas),
        "scenario_ids": [row.get("id") for row in selected_scenarios],
        "persona_ids": [row.get("id") for row in selected_personas],
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
        "scenario_count",
        "persona_count",
        "temperature_count",
        "condition_cells",
        "prompt_bank_fingerprint",
        "dataset",
        "metrics",
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
            for field in ("scenario_ids", "scenario_tags", "persona_ids"):
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
        "prompt_bank_fingerprint",
        "scenario_count",
        "persona_count",
        "scenario_ids",
        "persona_ids",
        "temperature_count",
        "condition_cells",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            out = {k: row.get(k) for k in keys}
            for field in ("scenario_ids", "persona_ids"):
                value = out.get(field)
                if isinstance(value, list):
                    out[field] = ",".join(str(v) for v in value)
            w.writerow(out)


def write_manifest_markdown(path: Path, manifest: dict):
    summary = manifest.get("summary") or {}
    run_id_summary = manifest.get("run_id_summary") or []
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
        "",
        "## Aggregate metrics",
        "",
        f"- cells: `{summary.get('cells', 0)}`",
        f"- counterfactual_per_sample_mean: `{summary.get('counterfactual_per_sample_mean', 'n/a')}`",
        f"- regret_words_per_sample_mean: `{summary.get('regret_words_per_sample_mean', 'n/a')}`",
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/experiment_matrix.json")
    ap.add_argument("--outdir", default="results/experiments")
    ap.add_argument("--run-label", default="")
    ap.add_argument("--resume", action="store_true", help="reuse existing label and skip completed run cells")
    ap.add_argument("--max-runs", type=int, default=0, help="optional cap on number of run cells executed")
    ap.add_argument("--plan-only", action="store_true", help="write manifest/plan without executing generation or analysis")
    ap.add_argument("--include-run-id", action="append", default=[], help="restrict execution to specific run id(s)")
    ap.add_argument("--manifest-note", default="", help="free-text note stored in manifest for traceability")
    ap.add_argument("--strict-clean", action="store_true", help="fail if git working tree is dirty")
    ap.add_argument("--list-run-ids", action="store_true", help="print run ids from config and exit")
    ap.add_argument("--selection-report", default="", help="optional JSON path for selected scenario/persona counts")
    ap.add_argument("--print-selection", action="store_true", help="print selected scenario/persona counts per run id")
    ap.add_argument("--selection-csv", default="", help="optional CSV path for selected scenario/persona counts")
    ap.add_argument("--require-min-scenarios", type=int, default=0, help="fail if a run selects fewer than this many scenarios")
    ap.add_argument("--require-min-personas", type=int, default=0, help="fail if a run selects fewer than this many personas")
    ap.add_argument("--fail-on-missing-run-id", action="store_true", help="fail when --include-run-id contains unknown ids")
    ap.add_argument("--manifest-markdown", action="store_true", help="emit a human-readable manifest summary markdown")
    ap.add_argument("--require-min-run-cells", type=int, default=0, help="fail if selected run cells are fewer than this minimum")
    ap.add_argument("--require-min-condition-cells", type=int, default=0, help="fail if any run selects fewer than this many scenario×persona×temperature condition cells")
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

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

    manifest_path = outdir / "manifest.json"
    existing_manifest = {}
    if args.resume and manifest_path.exists():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    completed = {
        r.get("run_key")
        for r in existing_manifest.get("runs", [])
        if r.get("status") == "ok" and (ROOT / r.get("dataset", "")).exists() and (ROOT / r.get("metrics", "")).exists()
    }

    runs = []
    selection_rows = []
    all_metric_paths = []
    batch_started = time.perf_counter()
    run_metric_paths: dict[str, list[Path]] = {}
    executed = 0
    selected_run_cells = 0
    include_run_ids = set(args.include_run_id)
    executed_ids = []

    known_run_ids = {str(exp.get("id")) for exp in cfg.get("runs", []) if exp.get("id")}
    missing_run_ids = sorted(include_run_ids - known_run_ids)
    if args.fail_on_missing_run_id and missing_run_ids:
        raise RuntimeError(f"unknown include-run-id values: {', '.join(missing_run_ids)}")

    matrix_snapshot = snapshots_dir / "experiment_matrix.json"
    write_json(matrix_snapshot, cfg)

    for exp in cfg.get("runs", []):
        run_id = exp["id"]
        if include_run_ids and run_id not in include_run_ids:
            continue
        n = int(exp.get("n", 20))
        seed = int(exp.get("seed", 42))
        temperatures = exp.get("temperatures", [0.2, 0.7])
        repeats = int(exp.get("repeats", 1))
        temp_csv = ",".join(str(t) for t in temperatures)
        prompt_bank = exp.get("prompt_bank", "prompts/prompt_bank_ko.json")
        scenario_ids = sorted(parse_csv_set(exp.get("scenario_ids")))
        scenario_tags = sorted(parse_csv_set(exp.get("scenario_tags")))
        persona_ids = sorted(parse_csv_set(exp.get("persona_ids")))
        prompt_bank_path = ROOT / prompt_bank
        bank = load_prompt_bank(prompt_bank_path)
        prompt_summary = summarize_prompt_bank(bank, set(scenario_ids), set(scenario_tags), set(persona_ids))
        condition_cells = prompt_summary["scenario_count"] * prompt_summary["persona_count"] * max(1, len(temperatures))
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

        if args.require_min_condition_cells and condition_cells < args.require_min_condition_cells:
            raise RuntimeError(
                f"{run_id}: condition_cells={condition_cells} < require_min_condition_cells={args.require_min_condition_cells}"
            )

        prompt_snapshot = snapshots_dir / f"{run_id}.prompt_bank.json"
        write_json(prompt_snapshot, bank)
        selection_rows.append(
            {
                "id": run_id,
                "prompt_bank": prompt_bank,
                "prompt_bank_fingerprint": file_sha256(prompt_snapshot),
                "scenario_count": prompt_summary["scenario_count"],
                "persona_count": prompt_summary["persona_count"],
                "scenario_ids": prompt_summary["scenario_ids"],
                "persona_ids": prompt_summary["persona_ids"],
                "temperature_count": len(temperatures),
                "condition_cells": condition_cells,
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
                "scenario_ids": scenario_ids,
                "scenario_tags": scenario_tags,
                "persona_ids": persona_ids,
                "scenario_count": prompt_summary["scenario_count"],
                "persona_count": prompt_summary["persona_count"],
                "temperature_count": len(temperatures),
                "condition_cells": condition_cells,
                "prompt_bank_fingerprint": file_sha256(prompt_snapshot),
                "dataset": str(dataset_path.relative_to(ROOT)),
                "metrics": str(metrics_path.relative_to(ROOT)),
                "status": "planned",
            }
            selected_run_cells += 1

            if run_key in completed:
                row["status"] = "skipped_resume"
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

            cell_started = time.perf_counter()
            code, _, err = run(gen_cmd)
            if code != 0:
                raise RuntimeError(f"generation failed for {run_key}: {err}")

            code, _, err2 = run(analyze_cmd)
            if code != 0:
                raise RuntimeError(f"analysis failed for {run_key}: {err2}")

            row["duration_seconds"] = round(time.perf_counter() - cell_started, 3)
            row["status"] = "ok"
            runs.append(row)
            all_metric_paths.append(metrics_path)
            run_metric_paths.setdefault(run_id, []).append(metrics_path)
            executed += 1
            executed_ids.append(run_key)

    if args.require_min_run_cells and selected_run_cells < args.require_min_run_cells:
        raise RuntimeError(
            f"selected_run_cells={selected_run_cells} < require_min_run_cells={args.require_min_run_cells}"
        )

    summary = aggregate_metrics(all_metric_paths)
    run_id_summary = aggregate_by_run_id(run_metric_paths)
    snapshot_hashes = {
        "experiment_matrix": file_sha256(matrix_snapshot),
        "prompt_banks": {},
    }
    for snap in sorted(snapshots_dir.glob("*.prompt_bank.json")):
        snapshot_hashes["prompt_banks"][snap.name] = file_sha256(snap)

    total_duration_seconds = round(time.perf_counter() - batch_started, 3)
    reproduce_script = outdir / "reproduce.sh"
    write_reproduce_script(reproduce_script, label, args.config, runs)

    manifest = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "config": args.config,
        "config_fingerprint": config_fingerprint(cfg),
        "run_label": label,
        "resume_mode": args.resume,
        "manifest_note": args.manifest_note,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git_commit": get_git_commit(),
            "git_status": git_status,
        },
        "summary": summary,
        "run_id_summary": run_id_summary,
        "snapshot_hashes": snapshot_hashes,
        "selected_run_ids": sorted(include_run_ids),
        "missing_run_ids": missing_run_ids,
        "plan_only": args.plan_only,
        "executed_run_keys": executed_ids,
        "selected_run_cells": selected_run_cells,
        "require_min_condition_cells": args.require_min_condition_cells,
        "duration_seconds": total_duration_seconds,
        "reproduce_script": str(reproduce_script.relative_to(ROOT)),
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
            print(f"selection {rid}: scenarios={sc}, personas={pc}, temps={tc}, condition_cells={cc}, prompt_bank_sha256={fp}")

    ok_n = sum(1 for r in runs if r.get("status") == "ok")
    print(f"[OK] executed {ok_n}/{len(runs)} run cells -> {outdir}")
    print(f"selected_run_cells: {selected_run_cells}")
    if args.plan_only:
        print(f"planned_only: {sum(1 for r in runs if r.get('status') == 'planned_only')}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
