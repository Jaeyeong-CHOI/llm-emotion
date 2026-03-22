#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import statistics
import subprocess
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
            w.writerow(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/experiment_matrix.json")
    ap.add_argument("--outdir", default="results/experiments")
    ap.add_argument("--run-label", default="")
    ap.add_argument("--resume", action="store_true", help="reuse existing label and skip completed run cells")
    ap.add_argument("--max-runs", type=int, default=0, help="optional cap on number of run cells executed")
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    label = args.run_label.strip() or utc_stamp()
    outdir = ROOT / args.outdir / label
    outdir.mkdir(parents=True, exist_ok=True)

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
    all_metric_paths = []
    executed = 0

    for exp in cfg.get("runs", []):
        run_id = exp["id"]
        n = int(exp.get("n", 20))
        seed = int(exp.get("seed", 42))
        temperatures = exp.get("temperatures", [0.2, 0.7])
        repeats = int(exp.get("repeats", 1))
        temp_csv = ",".join(str(t) for t in temperatures)
        prompt_bank = exp.get("prompt_bank", "prompts/prompt_bank_ko.json")

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
                "dataset": str(dataset_path.relative_to(ROOT)),
                "metrics": str(metrics_path.relative_to(ROOT)),
                "status": "planned",
            }

            if run_key in completed:
                row["status"] = "skipped_resume"
                runs.append(row)
                all_metric_paths.append(metrics_path)
                continue

            if args.max_runs > 0 and executed >= args.max_runs:
                row["status"] = "skipped_cap"
                runs.append(row)
                continue

            gen_cmd = (
                f"python3 scripts/generate_dataset.py --out {dataset_path} --n {n} "
                f"--seed {rep_seed} --prompt-bank {prompt_bank} --temperatures {temp_csv}"
            )
            code, _, err = run(gen_cmd)
            if code != 0:
                raise RuntimeError(f"generation failed for {run_key}: {err}")

            analyze_cmd = f"python3 scripts/analyze_regret_markers.py --in {dataset_path} --out {metrics_path}"
            code, _, err2 = run(analyze_cmd)
            if code != 0:
                raise RuntimeError(f"analysis failed for {run_key}: {err2}")

            row["status"] = "ok"
            runs.append(row)
            all_metric_paths.append(metrics_path)
            executed += 1

    summary = aggregate_metrics(all_metric_paths)
    manifest = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "config": args.config,
        "config_fingerprint": config_fingerprint(cfg),
        "run_label": label,
        "resume_mode": args.resume,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git_commit": get_git_commit(),
        },
        "summary": summary,
        "runs": runs,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_runs_csv(outdir / "runs.csv", runs)

    ok_n = sum(1 for r in runs if r.get("status") == "ok")
    print(f"[OK] executed {ok_n}/{len(runs)} run cells -> {outdir}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
