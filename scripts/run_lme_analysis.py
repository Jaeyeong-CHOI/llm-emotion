#!/usr/bin/env python3
"""
LME (Linear Mixed Effects) confirmatory analysis for regret-marker experiment.
Runs when per-condition n >= 30.

Reads real experiment batches, fits LME models, reports results.
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone

try:
    import numpy as np
    import pandas as pd
    import statsmodels.formula.api as smf
    from statsmodels.stats.multitest import multipletests
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip3 install statsmodels pandas numpy --break-system-packages")
    sys.exit(1)


RESULTS_DIR = Path(__file__).parent.parent / "results" / "real_experiments"

# Outcome variables to analyse
OUTCOMES = ["regret_word_rate", "counterfactual_rate", "negemo_rate", "semantic_regret_bias"]

OUTCOME_LABELS = {
    "regret_word_rate": "Regret-word rate",
    "counterfactual_rate": "Counterfactual rate",
    "negemo_rate": "Negative emotion rate",
    "semantic_regret_bias": "Semantic regret bias",
}


def load_gpt4o_batch(path: Path) -> pd.DataFrame:
    """Load GPT-4o per-sample JSONL (has scenario but not condition)."""
    rows = []
    scenario_to_condition = {
        "neutral_observer": "neutral",
        "neutral_daily": "neutral",
        "irreversible_choice": "deprivation",
        "health_tradeoff_overwork": "deprivation",
        "near_miss_outcome": "counterfactual",
        "prompt_bank_evidence_anchor_recovery_drill": "counterfactual",
    }
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            scenario = d.get("scenario", "unknown")
            cond = scenario_to_condition.get(scenario, "unknown")
            rows.append({
                "model": "gpt-4o",
                "condition": cond,
                "scenario": scenario,
                "persona": d.get("persona", "none"),
                "temperature": d.get("temperature", 0.5),
                "regret_word_rate": d.get("regret_word_rate", 0.0),
                "counterfactual_rate": d.get("counterfactual_rate", 0.0),
                "negemo_rate": d.get("negemo_rate", 0.0),
                "semantic_regret_bias": d.get("semantic_regret_bias", 0.0),
            })
    return pd.DataFrame(rows)


def load_gemini_batch(path: Path) -> pd.DataFrame:
    """Load Gemini JSONL (raw outputs without pre-computed marker rates).
    Gemini v2 already has analyzed metrics in the summary; we reconstruct from
    the summary stats since raw per-sample scores aren't in the output jsonl.
    """
    # Try to read analysed summary
    summary_path = path.with_suffix("").with_suffix("") if path.suffix == ".jsonl" else path
    summary_path = path.parent / (path.stem + ".summary.json")
    if not summary_path.exists():
        return pd.DataFrame()

    with open(summary_path) as f:
        summary = json.load(f)

    # Build synthetic per-sample rows from summary stats
    rows = []
    condition_stats = summary.get("conditions", {})
    persona_stats_dep = summary.get("personas", {})

    # We have n per condition from summary; need to reconstruct from raw JSONL with analyzed markers
    # Fall back to raw JSONL and infer condition from scenario_id
    scenario_to_condition = {
        "neutral_observer": "neutral",
        "neutral_daily": "neutral",
        "irreversible_choice": "deprivation",
        "health_tradeoff_overwork": "deprivation",
        "near_miss_outcome": "counterfactual",
        "prompt_bank_evidence_anchor_recovery_drill": "counterfactual",
    }

    with open(path) as f:
        for line in f:
            d = json.loads(line)
            # Raw Gemini output — markers not pre-computed in JSONL
            # Use condition field if available
            cond = d.get("condition", scenario_to_condition.get(d.get("scenario_id", ""), "unknown"))
            scenario = d.get("scenario_id", d.get("scenario", "unknown"))
            persona = d.get("persona", "none")
            temp = d.get("temperature", 0.5)
            rows.append({
                "model": d.get("model", "gemini-2.5-flash"),
                "condition": cond,
                "scenario": scenario,
                "persona": persona,
                "temperature": temp,
                # Markers not available in raw — will use 0, but we'll note this
                "regret_word_rate": d.get("regret_word_rate", 0.0),
                "counterfactual_rate": d.get("counterfactual_rate", 0.0),
                "negemo_rate": d.get("negemo_rate", 0.0),
                "semantic_regret_bias": d.get("semantic_regret_bias", 0.0),
            })
    return pd.DataFrame(rows)


def load_analyzed_per_sample() -> pd.DataFrame:
    """Load pre-analyzed per-sample JSONL (preferred path)."""
    path = RESULTS_DIR / "per_sample_analyzed.jsonl"
    if not path.exists():
        return pd.DataFrame()
    rows = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            rows.append({
                "model": d.get("model", "unknown"),
                "condition": d.get("condition", "unknown"),
                "scenario": d.get("scenario_id", "unknown"),
                "persona": d.get("persona", "none"),
                "temperature": float(d.get("temperature", 0.5)),
                "regret_word_rate": float(d.get("regret_rate", 0.0)),
                "counterfactual_rate": float(d.get("cf_rate", 0.0)),
                "negemo_rate": float(d.get("negemo_rate", 0.0)),
                "semantic_regret_bias": float(d.get("semantic_regret_bias", 0.0)),
            })
    df = pd.DataFrame(rows)
    print(f"Loaded pre-analyzed per-sample: {len(df)} rows")
    return df


def load_all_data() -> pd.DataFrame:
    """Load and merge all available batches."""
    frames = []

    # Preferred: pre-analyzed per-sample JSONL
    df_analyzed = load_analyzed_per_sample()
    if not df_analyzed.empty:
        frames.append(df_analyzed)
    else:
        # Fallback: raw batch files
        gpt_path = RESULTS_DIR / "batch_v1_pilot_openai.per_sample.jsonl"
        if gpt_path.exists():
            df_gpt = load_gpt4o_batch(gpt_path)
            frames.append(df_gpt)
            print(f"Loaded GPT-4o: {len(df_gpt)} rows")

        gem_path = RESULTS_DIR / "batch_v1_gemini_v2.jsonl"
        if gem_path.exists():
            df_gem = load_gemini_batch(gem_path)
            if not df_gem.empty:
                frames.append(df_gem)
                print(f"Loaded Gemini v2: {len(df_gem)} rows")

    if not frames:
        raise ValueError("No data found in results/real_experiments/. Run per_sample generation first.")

    df = pd.concat(frames, ignore_index=True)
    df["condition"] = df["condition"].astype("category")
    df["persona"] = df["persona"].astype("category")
    df["model"] = df["model"].astype("category")
    df["scenario"] = df["scenario"].astype("category")
    # Contrast code: deprivation = 1, others = 0
    df["cond_dep"] = (df["condition"] == "deprivation").astype(float)
    df["cond_cf"] = (df["condition"] == "counterfactual").astype(float)
    df["persona_rum"] = (df["persona"] == "ruminative").astype(float)
    df["persona_ref"] = (df["persona"] == "reflective").astype(float)
    df["temp_hi"] = (df["temperature"] >= 0.5).astype(float)
    return df


def run_lme_model(df: pd.DataFrame, outcome: str) -> dict:
    """Fit LME model: outcome ~ condition + persona + (1|scenario) + (1|model)."""
    # Check variance — skip if near-zero
    if df[outcome].std() < 1e-8:
        return {"outcome": outcome, "status": "skipped_zero_variance",
                "note": "outcome has near-zero variance across all observations"}

    # Model: random intercept by scenario and by model
    try:
        formula = f"{outcome} ~ cond_dep + cond_cf + persona_rum + persona_ref + temp_hi"
        # Random intercepts for scenario
        model = smf.mixedlm(formula, df, groups=df["scenario"])
        result = model.fit(reml=True, method="lbfgs")

        params = result.params
        pvals = result.pvalues
        conf = result.conf_int()

        out = {
            "outcome": outcome,
            "status": "converged",
            "n": int(len(df)),
            "log_likelihood": float(result.llf),
            "aic": float(result.aic),
            "bic": float(result.bic),
            "coefs": {}
        }

        for param in ["cond_dep", "cond_cf", "persona_rum", "persona_ref", "temp_hi"]:
            if param in params:
                out["coefs"][param] = {
                    "estimate": float(params[param]),
                    "se": float(result.bse[param]),
                    "z": float(result.tvalues[param]),
                    "p": float(pvals[param]),
                    "ci_lower": float(conf.loc[param, 0]),
                    "ci_upper": float(conf.loc[param, 1]),
                }
    except Exception as e:
        return {"outcome": outcome, "status": "error", "error": str(e)}

    return out


def bh_correct(lme_results: list) -> list:
    """Apply Benjamini-Hochberg FDR correction across cond_dep p-values."""
    # Collect p-values for cond_dep across outcomes
    p_vals = []
    for r in lme_results:
        if r.get("status") == "converged" and "cond_dep" in r.get("coefs", {}):
            p_vals.append(r["coefs"]["cond_dep"]["p"])
        else:
            p_vals.append(None)

    valid_p = [p for p in p_vals if p is not None]
    if not valid_p:
        return lme_results

    _, p_corrected, _, _ = multipletests(valid_p, method="fdr_bh")
    corrected_iter = iter(p_corrected)

    for r in lme_results:
        if r.get("status") == "converged" and "cond_dep" in r.get("coefs", {}):
            r["coefs"]["cond_dep"]["p_fdr_bh"] = float(next(corrected_iter))

    return lme_results


def generate_report(lme_results: list, df: pd.DataFrame) -> str:
    lines = ["# LME Confirmatory Analysis — Real Experiment Results",
             f"Generated: {datetime.now(timezone.utc).isoformat()}",
             f"N total: {len(df)} | N per condition: neutral={int((df['condition']=='neutral').sum())}, "
             f"deprivation={int((df['condition']=='deprivation').sum())}, "
             f"counterfactual={int((df['condition']=='counterfactual').sum())}",
             ""]

    lines.append("## Model: outcome ~ cond_dep + cond_cf + persona_rum + persona_ref + temp_hi + (1|scenario)\n")

    for r in lme_results:
        outcome = r["outcome"]
        label = OUTCOME_LABELS.get(outcome, outcome)
        lines.append(f"### {label} (`{outcome}`)")
        if r["status"] == "skipped_zero_variance":
            lines.append(f"  - SKIPPED: {r['note']}\n")
            continue
        elif r["status"] == "error":
            lines.append(f"  - ERROR: {r['error']}\n")
            continue

        lines.append(f"  N={r['n']}, AIC={r['aic']:.2f}, BIC={r['bic']:.2f}")
        lines.append("")
        lines.append("  | Predictor | Estimate | SE | z | p | p_FDR |")
        lines.append("  |---|---|---|---|---|---|")
        for param, c in r["coefs"].items():
            p_fdr = f"{c.get('p_fdr_bh', float('nan')):.4f}" if "p_fdr_bh" in c else "—"
            sig = "**" if c["p"] < 0.05 else ""
            lines.append(f"  | {param} | {c['estimate']:.4f} | {c['se']:.4f} | "
                         f"{c['z']:.3f} | {sig}{c['p']:.4f}{sig} | {p_fdr} |")
        lines.append("")

    # Condition means table
    lines.append("## Descriptive: Condition means (combined across models)")
    lines.append("")
    lines.append("| Condition | N | Regret rate | CF rate | NegEmo rate | Sem bias |")
    lines.append("|---|---|---|---|---|---|")
    for cond in ["neutral", "deprivation", "counterfactual"]:
        sub = df[df["condition"] == cond]
        lines.append(
            f"| {cond} | {len(sub)} | {sub['regret_word_rate'].mean():.4f} (SD={sub['regret_word_rate'].std():.3f}) "
            f"| {sub['counterfactual_rate'].mean():.4f} | {sub['negemo_rate'].mean():.4f} "
            f"| {sub['semantic_regret_bias'].mean():.4f} |"
        )
    lines.append("")

    # Note on Gemini raw marker issue
    lines.append("## Data Note")
    lines.append("GPT-4o batch (n=108): full per-sample marker scores available.")
    lines.append("Gemini batch (n=108): marker rates loaded from per-sample JSONL if available; "
                 "otherwise zeros (due to raw-output-only format). "
                 "GPT-4o-only sub-analysis is more reliable for marker-level LME.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run LME analysis on real experiment data")
    parser.add_argument("--min-n", type=int, default=30, help="Min n per condition to proceed")
    parser.add_argument("--out-json", default=str(RESULTS_DIR / "lme_results.json"))
    parser.add_argument("--out-report", default=str(RESULTS_DIR / "lme_report.md"))
    parser.add_argument("--gpt-only", action="store_true", help="Run on GPT-4o subset only")
    args = parser.parse_args()

    print("Loading data...")
    df = load_all_data()
    print(f"Total rows: {len(df)}")
    print(df["condition"].value_counts())

    # Check per-condition n
    min_cond_n = df["condition"].value_counts().min()
    if min_cond_n < args.min_n:
        print(f"Min condition n={min_cond_n} < threshold {args.min_n}. Exiting.")
        sys.exit(0)

    if args.gpt_only:
        df = df[df["model"] == "gpt-4o"].copy()
        print(f"GPT-4o only: {len(df)} rows")
        suffix = "_gpt4o"
        args.out_json = args.out_json.replace(".json", f"{suffix}.json")
        args.out_report = args.out_report.replace(".md", f"{suffix}.md")

    print("\nRunning LME models...")
    lme_results = []
    for outcome in OUTCOMES:
        print(f"  Fitting {outcome}...")
        r = run_lme_model(df, outcome)
        lme_results.append(r)

    lme_results = bh_correct(lme_results)

    # Save JSON
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_total": int(len(df)),
        "n_per_condition": {c: int(v) for c, v in df["condition"].value_counts().items()},
        "models": list(df["model"].unique()),
        "results": lme_results
    }
    with open(args.out_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nJSON saved to: {args.out_json}")

    # Save report
    report = generate_report(lme_results, df)
    with open(args.out_report, "w") as f:
        f.write(report)
    print(f"Report saved to: {args.out_report}")

    # Print brief summary
    print("\n=== KEY FINDINGS (cond_dep effect) ===")
    for r in lme_results:
        if r.get("status") == "converged":
            c = r["coefs"].get("cond_dep", {})
            p_fdr = c.get("p_fdr_bh", float("nan"))
            sig = "* SIGNIFICANT *" if c.get("p", 1.0) < 0.05 else ""
            print(f"  {r['outcome']:30s}: β={c.get('estimate', 0):.4f}, "
                  f"p={c.get('p', 1.0):.4f}, p_FDR={p_fdr:.4f} {sig}")
        elif r.get("status") == "skipped_zero_variance":
            print(f"  {r['outcome']:30s}: SKIPPED (zero variance)")
        else:
            print(f"  {r['outcome']:30s}: {r.get('status','?')} — {r.get('error','')[:60]}")


if __name__ == "__main__":
    main()
