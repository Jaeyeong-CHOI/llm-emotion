#!/usr/bin/env python3
"""
Run LME with crossed random effects: (1|scenario) + (1|model).
Compares Model A (scenario only, current) vs Model B (crossed) for embedding_regret_bias.
Addresses Critique Cycle 21 concern about z-stat inflation.
"""
import json
import pathlib
import sys
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_real_results import analyze  # noqa

BATCH_LIST = [
    "batch_v1_pilot_openai","batch_v1_gemini","batch_v1_gemini_v2","batch_v3_expand",
    "batch_v4_expand_gpt4o","batch_v5_expand_both","batch_v6_expand","batch_v7_expand",
    "batch_v8_neutral_balance","batch_v9_gpt35","batch_gemini25flashlite","batch_gpt54mini",
    "batch_gpt54nano","batch_llama33_70b","batch_llama4_scout","batch_qwen3_32b",
    "batch_gpt41","batch_gpt41mini","batch_gpt4omini","batch_gemini3flash","batch_gemini25pro",
    "batch_gemini3pro","batch_gemini31pro","batch_v10_neutral_expand","batch_v11_neutral_balance2",
    "batch_v12_gemini3pro_cf","batch_v13_openai_balance","batch_v14_balance","batch_v15_new_models",
    "batch_v16_oss_small","batch_v17_groq_compound","batch_v18_new_groq","batch_v19_groq_fill",
    "batch_v20_safeguard","batch_v21_gemini_new","batch_v22_cf_fill","batch_v23_new_openai",
    "batch_v24_fill_cells","batch_v25_groq_compound_balance","batch_v26_lowcount_fill",
    "batch_v27_o3mini","batch_v28_new_openai","batch_v29_stability_fill","batch_v30_stability_fill2",
    "batch_v31_gpt54full","batch_v32_o1_o3","batch_v33_o1_o3_neutral_fill","batch_v34_gpt5_family",
    "batch_v35_gpt51_gpt52","batch_v36_stability_fill","batch_v36b_final_fill","batch_v36c_gpt5_dep",
    "batch_v37_groq_balance",
]

def load_data(data_dir: pathlib.Path) -> pd.DataFrame:
    rows = []
    for fname in BATCH_LIST:
        src = data_dir / f"{fname}.emb.jsonl"
        if not src.exists():
            src = data_dir / f"{fname}.jsonl"
        if not src.exists():
            continue
        for line in src.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            m = analyze(r.get("output", ""))
            row = {
                "condition": r.get("condition", "unknown"),
                "persona": r.get("persona", "none"),
                "temperature": float(r.get("temperature") or 0.2),
                "model": r.get("model", "unknown"),
                "scenario": r.get("scenario_id", r.get("scenario", "s0")),
                "cf_rate": m["cf_rate"],
                "regret_rate": m["regret_rate"],
                "negemo_rate": m["negemo_rate"],
            }
            if "embedding_regret_bias" in r:
                row["embedding_regret_bias"] = float(r["embedding_regret_bias"])
            rows.append(row)
    df = pd.DataFrame(rows)
    df["cond_D"] = (df["condition"] == "deprivation").astype(float)
    df["cond_C"] = (df["condition"] == "counterfactual").astype(float)
    df["pers_rfl"] = (df["persona"] == "reflective").astype(float)
    df["pers_rum"] = (df["persona"] == "ruminative").astype(float)
    df["temp_z"] = (df["temperature"] - df["temperature"].mean()) / df["temperature"].std()
    return df


def fit_model(formula, df, groups, vc_formula=None, label=""):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if vc_formula:
            m = smf.mixedlm(formula, df, groups=df[groups], vc_formula=vc_formula)
        else:
            m = smf.mixedlm(formula, df, groups=df[groups])
        fit = m.fit(method="lbfgs", reml=True, disp=False)
    params = {}
    for k in ["Intercept", "cond_D", "cond_C", "pers_rfl", "pers_rum", "temp_z"]:
        if k in fit.params:
            params[k] = {
                "beta": round(float(fit.params[k]), 4),
                "se": round(float(fit.bse[k]), 4),
                "z": round(float(fit.tvalues[k]), 3),
                "p": round(float(fit.pvalues[k]), 5),
            }
    print(f"\n  {label}:")
    for k in ["cond_D", "cond_C"]:
        if k in params:
            p = params[k]
            print(f"    {k}: β={p['beta']}, SE={p['se']}, z={p['z']}, p={p['p']}")
    return params


def main():
    data_dir = ROOT / "results" / "real_experiments"
    out_path = data_dir / "lme_crossed_re.json"

    print("Loading data...")
    df = load_data(data_dir)
    print(f"Total N={len(df)}, conditions={df.condition.value_counts().to_dict()}")
    print(f"Models: {df.model.nunique()}, Scenarios: {df.scenario.nunique()}")

    df_emb = df.dropna(subset=["embedding_regret_bias"])
    print(f"Embedding subset N={len(df_emb)} (has embedding_regret_bias)")

    formula = "embedding_regret_bias ~ cond_D + cond_C + pers_rfl + pers_rum + temp_z"

    print("\n--- Model comparison: embedding_regret_bias ---")
    paramsA = fit_model(
        formula, df_emb, groups="scenario",
        label="Model A: (1|scenario) [current]"
    )
    paramsB = fit_model(
        formula, df_emb, groups="scenario",
        vc_formula={"model": "0+C(model)"},
        label="Model B: (1|scenario) + (1|model) [crossed RE]"
    )

    # Also run all markers with Model B for reporting
    all_markers = {}
    for marker in ["regret_rate", "negemo_rate", "cf_rate"]:
        f2 = f"{marker} ~ cond_D + cond_C + pers_rfl + pers_rum + temp_z"
        p = fit_model(f2, df, groups="scenario",
                      vc_formula={"model": "0+C(model)"},
                      label=f"{marker} (crossed RE)")
        all_markers[marker] = p
    all_markers["embedding_regret_bias"] = paramsB

    output = {
        "description": "LME with crossed RE: (1|scenario) + (1|model)",
        "n_embedding_subset": len(df_emb),
        "n_total": len(df),
        "n_models": int(df.model.nunique()),
        "n_scenarios": int(df.scenario.nunique()),
        "embedding_regret_bias": {
            "model_A_scenario_only": paramsA,
            "model_B_crossed_re": paramsB,
        },
        "all_markers_crossed_re": all_markers,
    }
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved → {out_path}")


if __name__ == "__main__":
    main()
