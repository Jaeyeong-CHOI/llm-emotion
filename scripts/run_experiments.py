#!/usr/bin/env python3
import argparse
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/experiment_matrix.json")
    ap.add_argument("--outdir", default="results/experiments")
    ap.add_argument("--run-label", default="")
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    label = args.run_label.strip() or utc_stamp()
    outdir = ROOT / args.outdir / label
    outdir.mkdir(parents=True, exist_ok=True)

    runs = []
    all_metric_paths = []
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

            gen_cmd = (
                f"python3 scripts/generate_dataset.py --out {dataset_path} --n {n} "
                f"--seed {rep_seed} --prompt-bank {prompt_bank} --temperatures {temp_csv}"
            )
            code, out, err = run(gen_cmd)
            if code != 0:
                raise RuntimeError(f"generation failed for {run_key}: {err}")

            analyze_cmd = f"python3 scripts/analyze_regret_markers.py --in {dataset_path} --out {metrics_path}"
            code, out2, err2 = run(analyze_cmd)
            if code != 0:
                raise RuntimeError(f"analysis failed for {run_key}: {err2}")

            runs.append(
                {
                    "id": run_id,
                    "run_key": run_key,
                    "repeat_index": rep + 1,
                    "n": n,
                    "seed": rep_seed,
                    "temperatures": temperatures,
                    "prompt_bank": prompt_bank,
                    "dataset": str(dataset_path.relative_to(ROOT)),
                    "metrics": str(metrics_path.relative_to(ROOT)),
                }
            )
            all_metric_paths.append(metrics_path)

    summary = aggregate_metrics(all_metric_paths)
    manifest = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "config": args.config,
        "config_fingerprint": config_fingerprint(cfg),
        "run_label": label,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "summary": summary,
        "runs": runs,
    }
    manifest_path = outdir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] completed {len(runs)} runs -> {outdir}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
