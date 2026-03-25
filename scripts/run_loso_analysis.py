#!/usr/bin/env python3
"""
Leave-One-Scenario-Out (LOSO) analysis for embedding regret bias.
Fits the confirmatory LME on all data EXCLUDING one scenario at a time,
recording beta(cond_D) and beta(cond_C) for embedding_regret_bias.
"""

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Primary 8-model batches (same as confirmatory LME)
PRIMARY_MODELS = {
    "gpt-4o", "gpt-3.5-turbo", "gpt-5.4-mini", "gpt-5.4-nano",
    "gemini-2.5-flash", "gemini-2.5-flash-lite",
    "llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct",
}


def load_data() -> pd.DataFrame:
    sys.path.insert(0, str(ROOT / "scripts"))
    from analyze_real_results import analyze

    data_dir = ROOT / "results" / "real_experiments"
    rows = []
    for f in sorted(data_dir.glob("*.emb.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            model = r.get("model", "unknown")
            if model not in PRIMARY_MODELS:
                continue
            if "embedding_regret_bias" not in r:
                continue
            m = analyze(r.get("output", ""))
            rows.append({
                "condition": r.get("condition", "unknown"),
                "persona": r.get("persona", "none"),
                "temperature": float(r.get("temperature", 0.2)),
                "model": model,
                "scenario_id": r.get("scenario_id", r.get("scenario", "s0")),
                "embedding_regret_bias": float(r["embedding_regret_bias"]),
            })
    return pd.DataFrame(rows)


def fit_lme_embedding(df: pd.DataFrame) -> dict:
    """Fit LME for embedding_regret_bias, return cond_D and cond_C betas."""
    import statsmodels.formula.api as smf

    df2 = df.copy()
    df2["cond_D"] = (df2["condition"] == "deprivation").astype(float)
    df2["cond_C"] = (df2["condition"] == "counterfactual").astype(float)
    df2["pers_rfl"] = (df2["persona"] == "reflective").astype(float)
    df2["pers_rum"] = (df2["persona"] == "ruminative").astype(float)
    df2["temp_z"] = (df2["temperature"] - df2["temperature"].mean()) / max(df2["temperature"].std(), 1e-9)

    n_groups = df2["scenario_id"].nunique()
    if n_groups < 2:
        return None

    model = smf.mixedlm(
        "embedding_regret_bias ~ cond_D + cond_C + pers_rfl + pers_rum + temp_z",
        df2,
        groups=df2["scenario_id"],
    )
    fit = model.fit(reml=True, method="lbfgs", disp=False)
    return {
        "beta_D": round(float(fit.params.get("cond_D", np.nan)), 4),
        "beta_C": round(float(fit.params.get("cond_C", np.nan)), 4),
        "p_D": round(float(fit.pvalues.get("cond_D", np.nan)), 5),
        "p_C": round(float(fit.pvalues.get("cond_C", np.nan)), 5),
    }


def main():
    print("Loading primary 8-model data...")
    df = load_data()
    print(f"Loaded {len(df)} samples, {df['scenario_id'].nunique()} unique scenarios")

    scenarios = sorted(df["scenario_id"].unique())
    results = []

    for i, scenario in enumerate(scenarios):
        train = df[df["scenario_id"] != scenario]
        n_train = len(train)
        try:
            res = fit_lme_embedding(train)
            if res is None:
                print(f"  [{i+1}/{len(scenarios)}] Skip {scenario} (too few groups)")
                continue
            res["held_out"] = scenario
            res["n_train"] = n_train
            results.append(res)
            print(f"  [{i+1}/{len(scenarios)}] {scenario}: beta_D={res['beta_D']}, beta_C={res['beta_C']}")
        except Exception as e:
            print(f"  [{i+1}/{len(scenarios)}] {scenario}: ERROR {e}")

    if not results:
        print("No LOSO results.")
        return

    betas_D = [r["beta_D"] for r in results]
    betas_C = [r["beta_C"] for r in results]

    summary = {
        "n_scenarios": len(scenarios),
        "n_successful": len(results),
        "deprivation_effect": {
            "mean_beta": round(np.mean(betas_D), 4),
            "sd_beta": round(np.std(betas_D, ddof=1), 4),
            "min_beta": round(min(betas_D), 4),
            "max_beta": round(max(betas_D), 4),
            "all_positive": all(b > 0 for b in betas_D),
        },
        "counterfactual_effect": {
            "mean_beta": round(np.mean(betas_C), 4),
            "sd_beta": round(np.std(betas_C, ddof=1), 4),
            "min_beta": round(min(betas_C), 4),
            "max_beta": round(max(betas_C), 4),
            "all_positive": all(b > 0 for b in betas_C),
        },
        "per_scenario": results,
    }

    out_path = ROOT / "results" / "real_experiments" / "loso_results.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nLOSO Summary:")
    print(f"  Deprivation: mean_beta={summary['deprivation_effect']['mean_beta']}, "
          f"SD={summary['deprivation_effect']['sd_beta']}, "
          f"range=[{summary['deprivation_effect']['min_beta']}, {summary['deprivation_effect']['max_beta']}], "
          f"all_positive={summary['deprivation_effect']['all_positive']}")
    print(f"  Counterfactual: mean_beta={summary['counterfactual_effect']['mean_beta']}, "
          f"SD={summary['counterfactual_effect']['sd_beta']}, "
          f"range=[{summary['counterfactual_effect']['min_beta']}, {summary['counterfactual_effect']['max_beta']}], "
          f"all_positive={summary['counterfactual_effect']['all_positive']}")
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
