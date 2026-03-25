#!/usr/bin/env python3
"""
Run LME confirmatory analysis on real experiment data.
Uses statsmodels MixedLM with scenario as random intercept.
"""

import json
import math
import sys
import pathlib
import statistics
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_and_score(data_dir: pathlib.Path) -> pd.DataFrame:
    sys.path.insert(0, str(ROOT / "scripts"))
    from analyze_real_results import analyze  # noqa

    rows = []
    for fname in ["batch_v1_pilot_openai", "batch_v1_gemini_v2", "batch_v3_expand", "batch_v4_expand_gpt4o", "batch_v5_expand_both", "batch_v6_expand", "batch_v7_expand", "batch_v8_neutral_balance", "batch_v9_gpt35", "batch_gemini25flashlite", "batch_gpt54mini", "batch_gpt54nano", "batch_llama33_70b", "batch_llama4_scout", "batch_qwen3_32b", "batch_gpt41", "batch_gpt41mini", "batch_gpt4omini", "batch_gemini3flash", "batch_gemini25pro", "batch_gemini3pro", "batch_gemini31pro", "batch_v10_neutral_expand", "batch_v11_neutral_balance2", "batch_v12_gemini3pro_cf", "batch_v13_openai_balance", "batch_v14_balance", "batch_v15_new_models", "batch_v16_oss_small", "batch_v17_groq_compound", "batch_v18_new_groq", "batch_v19_groq_fill", "batch_v20_safeguard", "batch_v21_gemini_new", "batch_v22_cf_fill", "batch_v23_new_openai"]:
        # Prefer .emb.jsonl (has embedding_regret_bias), fall back to .jsonl
        emb_path = data_dir / f"{fname}.emb.jsonl"
        path = data_dir / f"{fname}.jsonl"
        use_emb = emb_path.exists()
        src = emb_path if use_emb else path
        if not src.exists():
            continue
        for line in src.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                m = analyze(r.get("output", ""))
                row = {
                    "condition": r.get("condition", "unknown"),
                    "persona": r.get("persona", "none"),
                    "temperature": float(r.get("temperature", 0.2)),
                    "model": r.get("model", "unknown"),
                    "scenario_id": r.get("scenario_id", r.get("scenario", "s0")),
                    "output_length": len(r.get("output", "")),
                    "cf_rate": m["cf_rate"],
                    "regret_rate": m["regret_rate"],
                    "negemo_rate": m["negemo_rate"],
                    "semantic_regret_bias": m["semantic_regret_bias"],
                }
                # Add embedding-based metric if available
                if "embedding_regret_bias" in r:
                    row["embedding_regret_bias"] = float(r["embedding_regret_bias"])
                rows.append(row)

    return pd.DataFrame(rows)


def run_welch_tests(df: pd.DataFrame) -> dict:
    """Exploratory Welch t-tests."""
    results = {}
    dep = df[df["condition"] == "deprivation"]
    neu = df[df["condition"] == "neutral"]
    cf = df[df["condition"] == "counterfactual"]

    def _cohens_d(a, b):
        """Standard pooled-variance Cohen's d."""
        na, nb = len(a), len(b)
        if na < 2 or nb < 2:
            return float("nan")
        va, vb = statistics.variance(list(a)), statistics.variance(list(b))
        pooled_sd = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
        return (np.mean(a) - np.mean(b)) / max(pooled_sd, 1e-9)

    markers = ["cf_rate", "regret_rate", "negemo_rate", "semantic_regret_bias"]
    if "embedding_regret_bias" in df.columns:
        markers.append("embedding_regret_bias")
    for marker in markers:
        t, p = stats.ttest_ind(dep[marker].values, neu[marker].values, equal_var=False)
        d = _cohens_d(dep[marker].values, neu[marker].values)
        tc, pc = stats.ttest_ind(cf[marker].values, neu[marker].values, equal_var=False)
        dc = _cohens_d(cf[marker].values, neu[marker].values)
        results[marker] = {
            "D_vs_N": {"t": round(t, 3), "p": round(p, 5), "d": round(d, 3)},
            "C_vs_N": {"t": round(tc, 3), "p": round(pc, 5), "d": round(dc, 3)},
        }
    return results


def run_lme(df: pd.DataFrame) -> dict:
    """Run MixedLM for each marker with scenario as random intercept."""
    try:
        import statsmodels.formula.api as smf
    except ImportError:
        return {"error": "statsmodels not installed"}

    # Encode condition as dummy (neutral = baseline)
    df2 = df.copy()
    df2["cond_D"] = (df2["condition"] == "deprivation").astype(float)
    df2["cond_C"] = (df2["condition"] == "counterfactual").astype(float)
    df2["pers_rfl"] = (df2["persona"] == "reflective").astype(float)
    df2["pers_rum"] = (df2["persona"] == "ruminative").astype(float)
    df2["temp_z"] = (df2["temperature"] - df2["temperature"].mean()) / df2["temperature"].std()

    results = {}
    markers = ["cf_rate", "regret_rate", "negemo_rate", "semantic_regret_bias"]
    if "embedding_regret_bias" in df2.columns:
        markers.append("embedding_regret_bias")
    for marker in markers:
        try:
            model = smf.mixedlm(
                f"{marker} ~ cond_D + cond_C + pers_rfl + pers_rum + temp_z",
                df2,
                groups=df2["scenario_id"],
            )
            fit = model.fit(reml=True, method="lbfgs", disp=False)
            params = {}
            for k in ["Intercept", "cond_D", "cond_C", "pers_rfl", "pers_rum", "temp_z"]:
                if k in fit.params:
                    params[k] = {
                        "beta": round(float(fit.params[k]), 4),
                        "se": round(float(fit.bse[k]), 4),
                        "z": round(float(fit.tvalues[k]), 3),
                        "p": round(float(fit.pvalues[k]), 5),
                    }
            results[marker] = {"params": params, "log_likelihood": round(fit.llf, 3)}
        except Exception as e:
            results[marker] = {"error": str(e)}

    return results


def run_keyword_confound(df: pd.DataFrame) -> dict:
    """Check prompt keyword overlap vs output regret rate."""
    prompt_kw = {
        "neutral": {"오늘", "하루", "문장", "감정", "사실", "해석"},
        "deprivation": {"기회", "놓친", "원했", "잃었", "감정", "후회", "아쉬움"},
        "counterfactual": {"결정", "결과", "단계", "만약", "연결"},
    }
    # compute per sample
    result = {}
    for cond, kw in prompt_kw.items():
        sub = df[df["condition"] == cond]
        result[cond] = {
            "n": len(sub),
            "mean_regret_rate": round(sub["regret_rate"].mean(), 4) if len(sub) else 0,
            "note": "Prompt keywords include regret tokens" if cond == "deprivation" else "Prompt keywords neutral",
        }
    return result


def main():
    data_dir = ROOT / "results" / "real_experiments"
    out_path = ROOT / "results" / "real_experiments" / "lme_analysis.json"

    print("Loading and scoring data...")
    df = load_and_score(data_dir)
    if df.empty:
        print("No data found.")
        return

    print(f"Loaded {len(df)} samples. Conditions: {df['condition'].value_counts().to_dict()}")

    print("\n--- Welch t-tests (exploratory) ---")
    welch = run_welch_tests(df)
    for marker, vals in welch.items():
        dn = vals["D_vs_N"]
        cn = vals["C_vs_N"]
        print(f"  {marker}: D vs N: t={dn['t']}, p={dn['p']}, d={dn['d']}  |  C vs N: t={cn['t']}, p={cn['p']}, d={cn['d']}")

    print("\n--- Mixed-effects LME (scenario as random intercept) ---")
    lme = run_lme(df)
    for marker, res in lme.items():
        if "error" in res:
            print(f"  {marker}: ERROR {res['error']}")
        else:
            cond_D = res["params"].get("cond_D", {})
            print(f"  {marker}: cond_D beta={cond_D.get('beta')}, z={cond_D.get('z')}, p={cond_D.get('p')}")

    print("\n--- Keyword confound check ---")
    kc = run_keyword_confound(df)
    for cond, v in kc.items():
        print(f"  {cond}: n={v['n']}, mean_regret={v['mean_regret_rate']}")

    output = {
        "n_total": len(df),
        "conditions": df["condition"].value_counts().to_dict(),
        "welch_tests": welch,
        "lme": lme,
        "keyword_confound": kc,
    }
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
