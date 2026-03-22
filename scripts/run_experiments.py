#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: str):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def utc_stamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/experiment_matrix.json")
    ap.add_argument("--outdir", default="results/experiments")
    args = ap.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    outdir = ROOT / args.outdir / utc_stamp()
    outdir.mkdir(parents=True, exist_ok=True)

    runs = []
    for exp in cfg.get("runs", []):
        run_id = exp["id"]
        n = int(exp.get("n", 20))
        seed = int(exp.get("seed", 42))
        temperatures = exp.get("temperatures", [0.2, 0.7])
        temp_csv = ",".join(str(t) for t in temperatures)
        prompt_bank = exp.get("prompt_bank", "prompts/prompt_bank_ko.json")

        dataset_path = outdir / f"{run_id}.jsonl"
        metrics_path = outdir / f"{run_id}.metrics.json"

        gen_cmd = (
            f"python3 scripts/generate_dataset.py --out {dataset_path} --n {n} "
            f"--seed {seed} --prompt-bank {prompt_bank} --temperatures {temp_csv}"
        )
        code, out, err = run(gen_cmd)
        if code != 0:
            raise RuntimeError(f"generation failed for {run_id}: {err}")

        analyze_cmd = f"python3 scripts/analyze_regret_markers.py --in {dataset_path} --out {metrics_path}"
        code, out2, err2 = run(analyze_cmd)
        if code != 0:
            raise RuntimeError(f"analysis failed for {run_id}: {err2}")

        runs.append(
            {
                "id": run_id,
                "n": n,
                "seed": seed,
                "temperatures": temperatures,
                "prompt_bank": prompt_bank,
                "dataset": str(dataset_path.relative_to(ROOT)),
                "metrics": str(metrics_path.relative_to(ROOT)),
            }
        )

    manifest = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "config": args.config,
        "runs": runs,
    }
    manifest_path = outdir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] completed {len(runs)} runs -> {outdir}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    main()
