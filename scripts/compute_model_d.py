#!/usr/bin/env python3
"""Compute per-model Cohen's d with bootstrap 95% CI for embedding regret bias.

Loads all .emb.jsonl files, computes:
  - Per model: mean embedding_regret_bias per condition (D, N, C)
  - Cohen's d (D vs N, C vs N) using pooled SD within each model
  - Bootstrap 95% CI (1000 samples) for models with n < 50
  - Flags models with n < 30 as unstable

Output: results/real_experiments/model_d_corrected.json
"""

import json, os, sys, math
from collections import defaultdict
from pathlib import Path
import numpy as np

EMB_DIR = Path("results/real_experiments")
OUT_PATH = EMB_DIR / "model_d_corrected.json"
N_BOOT = 1000
RNG_SEED = 42


def load_all_emb_records():
    records = []
    for f in sorted(EMB_DIR.glob("*.emb.jsonl")):
        with open(f, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                    bias = r.get("embedding_regret_bias")
                    if bias is None:
                        continue
                    records.append({
                        "model": r["model"],
                        "condition": r["condition"],
                        "bias": float(bias),
                    })
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    return records


def pooled_sd(a, b):
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return float("nan")
    v1, v2 = np.var(a, ddof=1), np.var(b, ddof=1)
    return math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))


def cohen_d(group1, group2):
    sd = pooled_sd(group1, group2)
    if sd == 0 or math.isnan(sd):
        return float("nan")
    return (np.mean(group1) - np.mean(group2)) / sd


def bootstrap_d(group1, group2, n_boot=N_BOOT, seed=RNG_SEED):
    rng = np.random.RandomState(seed)
    ds = []
    for _ in range(n_boot):
        s1 = rng.choice(group1, size=len(group1), replace=True)
        s2 = rng.choice(group2, size=len(group2), replace=True)
        ds.append(cohen_d(s1, s2))
    ds = [d for d in ds if not math.isnan(d)]
    if len(ds) < 10:
        return (float("nan"), float("nan"))
    return (float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5)))


def main():
    records = load_all_emb_records()
    if not records:
        print("ERROR: No .emb.jsonl records found", file=sys.stderr)
        sys.exit(1)

    # Group by model and condition
    by_model = defaultdict(lambda: defaultdict(list))
    for r in records:
        by_model[r["model"]][r["condition"]].append(r["bias"])

    results = []
    for model in sorted(by_model.keys()):
        conds = by_model[model]
        d_vals = np.array(conds.get("deprivation", []))
        n_vals = np.array(conds.get("neutral", []))
        c_vals = np.array(conds.get("counterfactual", []))

        entry = {
            "model": model,
            "n_deprivation": len(d_vals),
            "n_neutral": len(n_vals),
            "n_counterfactual": len(c_vals),
            "n_total": len(d_vals) + len(n_vals) + len(c_vals),
            "mean_D": float(np.mean(d_vals)) if len(d_vals) else None,
            "mean_N": float(np.mean(n_vals)) if len(n_vals) else None,
            "mean_C": float(np.mean(c_vals)) if len(c_vals) else None,
        }

        # D vs N
        if len(d_vals) >= 2 and len(n_vals) >= 2:
            entry["d_DN"] = round(cohen_d(d_vals, n_vals), 3)
            min_n = min(len(d_vals), len(n_vals))
            if min_n < 50:
                ci = bootstrap_d(d_vals, n_vals)
                entry["d_DN_CI95"] = [round(ci[0], 3), round(ci[1], 3)]
            if min_n < 30:
                entry["d_DN_flag"] = "unstable (n<30)"
        else:
            entry["d_DN"] = None

        # C vs N
        if len(c_vals) >= 2 and len(n_vals) >= 2:
            entry["d_CN"] = round(cohen_d(c_vals, n_vals), 3)
            min_n = min(len(c_vals), len(n_vals))
            if min_n < 50:
                ci = bootstrap_d(c_vals, n_vals)
                entry["d_CN_CI95"] = [round(ci[0], 3), round(ci[1], 3)]
            if min_n < 30:
                entry["d_CN_flag"] = "unstable (n<30)"
        else:
            entry["d_CN"] = None

        results.append(entry)

    # Summary
    print(f"Computed d for {len(results)} models from {len(records)} records")
    for e in results:
        flag = ""
        if e.get("d_DN_flag"):
            flag = f" [{e['d_DN_flag']}]"
        ci_str = ""
        if "d_DN_CI95" in e:
            ci_str = f" CI95={e['d_DN_CI95']}"
        print(f"  {e['model']}: d_DN={e['d_DN']}{ci_str}{flag}  (n={e['n_total']})")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"method": "two-sample pooled-SD Cohen's d per model",
                    "bootstrap_n": N_BOOT,
                    "models": results}, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
