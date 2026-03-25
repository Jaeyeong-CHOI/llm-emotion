#!/usr/bin/env python3
"""
Multi-model comparison table for embedding regret bias.
Loads all .emb.jsonl files, groups by model, computes per-condition stats and Cohen's d.
"""

import json
import math
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "results" / "real_experiments"

# Map batch file prefixes to model display names (fallback: read from data)
BATCH_FILES = sorted(DATA_DIR.glob("*.emb.jsonl"))


def load_all():
    """Load all emb.jsonl files and return list of dicts."""
    rows = []
    for f in BATCH_FILES:
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def cohens_d(group_a: list[float], group_b: list[float]) -> float:
    """Pooled-variance Cohen's d (a vs b)."""
    n1, n2 = len(group_a), len(group_b)
    if n1 < 2 or n2 < 2:
        return float("nan")
    m1, m2 = sum(group_a) / n1, sum(group_b) / n2
    v1 = sum((x - m1) ** 2 for x in group_a) / (n1 - 1)
    v2 = sum((x - m2) ** 2 for x in group_b) / (n2 - 1)
    sp = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    if sp == 0:
        return float("nan")
    return (m1 - m2) / sp


def main():
    rows = load_all()
    print(f"Loaded {len(rows)} total samples from {len(BATCH_FILES)} files")

    # Group by model -> condition -> list of embedding_regret_bias
    by_model = defaultdict(lambda: defaultdict(list))
    for r in rows:
        model = r.get("model", "unknown")
        cond = r.get("condition", "unknown")
        bias = r.get("embedding_regret_bias")
        if bias is not None:
            by_model[model][cond].append(bias)

    # Build table
    table = []
    for model in sorted(by_model.keys()):
        conds = by_model[model]
        n_vals = conds.get("neutral", [])
        d_vals = conds.get("deprivation", [])
        c_vals = conds.get("counterfactual", [])

        entry = {
            "model": model,
            "N_bias": round(sum(n_vals) / len(n_vals), 4) if n_vals else None,
            "D_bias": round(sum(d_vals) / len(d_vals), 4) if d_vals else None,
            "C_bias": round(sum(c_vals) / len(c_vals), 4) if c_vals else None,
            "d_DN": round(cohens_d(d_vals, n_vals), 3) if d_vals and n_vals else None,
            "d_CN": round(cohens_d(c_vals, n_vals), 3) if c_vals and n_vals else None,
            "n_D": len(d_vals),
            "n_N": len(n_vals),
            "n_C": len(c_vals),
        }
        table.append(entry)

    # Print table
    header = f"{'Model':<25s} {'D_bias':>8s} {'N_bias':>8s} {'C_bias':>8s} {'d(D-N)':>8s} {'d(C-N)':>8s} {'n_D':>5s} {'n_N':>5s} {'n_C':>5s}"
    print("\n" + header)
    print("-" * len(header))
    for e in table:
        fmt = lambda v, d=4: f"{v:.{d}f}" if v is not None else "N/A"
        print(
            f"{e['model']:<25s} {fmt(e['D_bias']):>8s} {fmt(e['N_bias']):>8s} {fmt(e['C_bias']):>8s} "
            f"{fmt(e['d_DN'], 3):>8s} {fmt(e['d_CN'], 3):>8s} {e['n_D']:>5d} {e['n_N']:>5d} {e['n_C']:>5d}"
        )

    # Save JSON
    out_path = DATA_DIR / "model_comparison_table.json"
    out_path.write_text(json.dumps(table, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
