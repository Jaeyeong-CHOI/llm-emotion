#!/usr/bin/env python3
"""
Analyze ablation minimal-pair data.
Field names: cf_rate, regret_word_rate, neg_emotion_rate, semantic_regret_bias.
Computes per-condition and per-topic stats, Cohen's d, Welch t-tests.
"""

import json
import math
import pathlib
import statistics
from collections import defaultdict
from scipy import stats as sp_stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_GEMINI = ROOT / "results/real_experiments/ablation_minimal_pairs_v1.jsonl"
DATA_GPT4O  = ROOT / "results/real_experiments/ablation_gpt4o_v1.jsonl"

METRICS = ["cf_rate", "regret_word_rate", "neg_emotion_rate", "semantic_regret_bias"]


def load():
    rows = []
    for path in [DATA_GEMINI, DATA_GPT4O]:
        if path.exists():
            rows.extend(json.loads(l) for l in path.read_text().splitlines() if l.strip())
    return rows


def cohens_d(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    va, vb = statistics.variance(a), statistics.variance(b)
    pooled_sd = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if pooled_sd == 0:
        return float("nan")
    return (statistics.mean(a) - statistics.mean(b)) / pooled_sd


def main():
    rows = load()
    from collections import Counter as _Counter
    providers = _Counter(r.get("provider", "?") for r in rows)
    print(f"Ablation data: N={len(rows)}  ({dict(providers)})")

    # Group by condition
    by_cond = defaultdict(list)
    for r in rows:
        by_cond[r["condition"]].append(r)

    # Group by (pair_id, condition)
    by_pair_cond = defaultdict(list)
    for r in rows:
        by_pair_cond[(r["pair_id"], r["condition"])].append(r)

    print("\n=== CONDITION-LEVEL SUMMARY ===")
    print(f"{'Condition':<16} {'n':>4}  {'cf_rate':>10} {'regret_wd':>10} {'neg_emo':>10} {'sem_bias':>10}")
    print("-" * 70)
    for cond in ["neutral", "deprivation", "counterfactual"]:
        g = by_cond[cond]
        n = len(g)
        vals = {m: [r[m] for r in g] for m in METRICS}
        means = {m: statistics.mean(vals[m]) for m in METRICS}
        print(f"{cond:<16} {n:>4}  {means['cf_rate']:>10.4f} {means['regret_word_rate']:>10.4f} "
              f"{means['neg_emotion_rate']:>10.4f} {means['semantic_regret_bias']:>10.4f}")

    # Pairwise comparisons vs neutral
    print("\n=== PAIRWISE vs NEUTRAL (Welch t-test) ===")
    neutral_vals = {m: [r[m] for r in by_cond["neutral"]] for m in METRICS}
    results = {}
    for cond in ["deprivation", "counterfactual"]:
        cond_vals = {m: [r[m] for r in by_cond[cond]] for m in METRICS}
        print(f"\n--- {cond.upper()} vs NEUTRAL ---")
        print(f"{'Metric':<22} {'d':>7} {'t':>8} {'p':>10}")
        for m in METRICS:
            d = cohens_d(cond_vals[m], neutral_vals[m])
            t, p = sp_stats.ttest_ind(cond_vals[m], neutral_vals[m], equal_var=False)
            print(f"{m:<22} {d:>7.3f} {t:>8.3f} {p:>10.4g}")
            results[(cond, m)] = {"d": d, "t": t, "p": p}

    # Per-topic breakdown
    print("\n=== PER-TOPIC BREAKDOWN (semantic_regret_bias) ===")
    topics = sorted(set(r["pair_id"] for r in rows))
    print(f"{'Topic':<22} {'Cond':<16} {'n':>4} {'mean':>8} {'sd':>8} {'d_vs_N':>8}")
    print("-" * 70)
    for topic in topics:
        neutral = [r["semantic_regret_bias"] for r in by_pair_cond.get((topic, "neutral"), [])]
        for cond in ["neutral", "deprivation", "counterfactual"]:
            g = by_pair_cond.get((topic, cond), [])
            vals = [r["semantic_regret_bias"] for r in g]
            if not vals:
                continue
            m = statistics.mean(vals)
            sd = statistics.stdev(vals) if len(vals) > 1 else 0
            d = cohens_d(vals, neutral) if cond != "neutral" else 0
            print(f"{topic:<22} {cond:<16} {len(vals):>4} {m:>8.4f} {sd:>8.4f} {d:>8.3f}")

    # Save JSON summary
    summary = {
        "n_total": len(rows),
        "conditions": {},
        "per_topic": {},
        "comparisons": {},
    }
    for cond in ["neutral", "deprivation", "counterfactual"]:
        g = by_cond[cond]
        summary["conditions"][cond] = {
            "n": len(g),
            **{m: round(statistics.mean([r[m] for r in g]), 5) for m in METRICS},
            **{f"{m}_sd": round(statistics.stdev([r[m] for r in g]), 5) if len(g) > 1 else 0 for m in METRICS},
        }
    for (cond, m), v in results.items():
        summary["comparisons"][f"{cond}_vs_neutral_{m}"] = {
            "d": round(v["d"], 4),
            "t": round(v["t"], 4),
            "p": round(v["p"], 6),
        }
    # Per-topic semantic bias
    for topic in topics:
        neutral = [r["semantic_regret_bias"] for r in by_pair_cond.get((topic, "neutral"), [])]
        summary["per_topic"][topic] = {}
        for cond in ["neutral", "deprivation", "counterfactual"]:
            g = by_pair_cond.get((topic, cond), [])
            vals = [r["semantic_regret_bias"] for r in g]
            if not vals:
                continue
            summary["per_topic"][topic][cond] = {
                "n": len(vals),
                "mean": round(statistics.mean(vals), 5),
                "sd": round(statistics.stdev(vals), 5) if len(vals) > 1 else 0,
                "d_vs_neutral": round(cohens_d(vals, neutral), 4) if cond != "neutral" and neutral else 0,
            }

    out_path = ROOT / "results/real_experiments/ablation_analysis.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nSaved summary to {out_path}")


if __name__ == "__main__":
    main()
