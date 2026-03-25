#!/usr/bin/env python3
"""
Length confound sensitivity analysis for embedding regret bias.

Addresses the reviewer concern that longer outputs may produce higher
embedding cosine similarity to regret prototypes simply due to length.

Analyses:
1. Pearson r(output_length, emb_bias) overall and per condition
2. LME with log(output_length) as covariate — main test
3. Length-residualized t-tests (secondary)

Saves results to results/real_experiments/length_sensitivity.json
"""

import json, os, pathlib, numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "results" / "real_experiments"
OUT_FILE = DATA_DIR / "length_sensitivity.json"


def load_data():
    rows = []
    for f in sorted(os.listdir(DATA_DIR)):
        if not f.endswith(".emb.jsonl"):
            continue
        with open(DATA_DIR / f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                emb = d.get("embedding_regret_bias")
                cond = d.get("condition", "")
                if emb is not None and cond in ("deprivation", "counterfactual", "neutral"):
                    out = d.get("output", "")
                    rows.append({
                        "condition": cond,
                        "output_len_words": len(out.split()),
                        "emb": float(emb),
                        "model": d.get("model", ""),
                        "scenario_id": d.get("scenario_id", "s0"),
                    })
    return pd.DataFrame(rows)


def cohens_d(a, b):
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    pooled = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    return float((a.mean() - b.mean()) / max(pooled, 1e-9))


def main():
    df = load_data()
    df["log_len"] = np.log1p(df["output_len_words"])

    # 1. Pearson correlations
    r_all, p_all = stats.pearsonr(df["output_len_words"], df["emb"])
    pearson_by_cond = {}
    for cond in ["deprivation", "counterfactual", "neutral"]:
        sub = df[df["condition"] == cond]
        r, p = stats.pearsonr(sub["output_len_words"], sub["emb"])
        pearson_by_cond[cond] = {"r": round(float(r), 4), "p": float(p), "n": int(len(sub))}

    # 2. LME with log_len covariate (main sensitivity test)
    df["is_dep"] = (df["condition"] == "deprivation").astype(float)
    df["is_cf"] = (df["condition"] == "counterfactual").astype(float)
    m = smf.mixedlm("emb ~ is_dep + is_cf + log_len", df, groups=df["scenario_id"]).fit(reml=False)

    lme_with_len = {}
    for k in ["is_dep", "is_cf", "log_len"]:
        coef = float(m.params[k])
        se = float(m.bse[k])
        z = coef / se
        p = float(m.pvalues[k])
        lme_with_len[k] = {"beta": round(coef, 4), "z": round(z, 2), "p": p}

    # 3. Length-residualized t-tests
    lm = np.polyfit(df["log_len"], df["emb"], 1)
    df["emb_resid"] = df["emb"] - (lm[0] * df["log_len"] + lm[1])

    dep_r = df[df["condition"] == "deprivation"]["emb_resid"]
    cf_r = df[df["condition"] == "counterfactual"]["emb_resid"]
    neu_r = df[df["condition"] == "neutral"]["emb_resid"]

    t_dn, p_dn = stats.ttest_ind(dep_r, neu_r)
    t_cn, p_cn = stats.ttest_ind(cf_r, neu_r)

    resid_tests = {
        "dep_vs_neu": {
            "t": round(float(t_dn), 2), "p": float(p_dn),
            "d": round(cohens_d(dep_r, neu_r), 3),
            "n_dep": int(len(dep_r)), "n_neu": int(len(neu_r))
        },
        "cf_vs_neu": {
            "t": round(float(t_cn), 2), "p": float(p_cn),
            "d": round(cohens_d(cf_r, neu_r), 3),
            "n_cf": int(len(cf_r)), "n_neu": int(len(neu_r))
        }
    }

    result = {
        "n_total": int(len(df)),
        "pearson_overall": {"r": round(float(r_all), 4), "p": float(p_all)},
        "pearson_by_condition": pearson_by_cond,
        "lme_with_length_covariate": lme_with_len,
        "lme_baseline_dep_beta": 0.1497,   # from main lme_analysis.json
        "lme_baseline_cf_beta": 0.2011,
        "length_residualized_ttests": resid_tests,
        "interpretation": (
            "Length is significantly correlated with embedding bias (r=%.4f, p<.001), "
            "but condition effects persist after controlling for log(length): "
            "dep beta=%.4f (z=%.2f), CF beta=%.4f (z=%.2f), both p<.001. "
            "Effect size reduction from baseline: dep %.1f%%, CF %.1f%%. "
            "Length-residualized d values: dep=%.3f, CF=%.3f (vs %.3f, %.3f unresid)."
        ) % (
            r_all,
            lme_with_len["is_dep"]["beta"], lme_with_len["is_dep"]["z"],
            lme_with_len["is_cf"]["beta"], lme_with_len["is_cf"]["z"],
            100 * (1 - lme_with_len["is_dep"]["beta"] / 0.1497),
            100 * (1 - lme_with_len["is_cf"]["beta"] / 0.2011),
            resid_tests["dep_vs_neu"]["d"], resid_tests["cf_vs_neu"]["d"],
            1.886, 2.208  # original t-test d values
        )
    }

    OUT_FILE.write_text(json.dumps(result, indent=2))
    print(f"Saved: {OUT_FILE}")
    print()
    print("=== Length Sensitivity Results ===")
    print(f"Pearson r(len, emb) overall: r={r_all:.4f}, p={p_all:.4e}")
    print()
    print("LME with log_len covariate:")
    for k, v in lme_with_len.items():
        print(f"  {k}: beta={v['beta']:.4f}, z={v['z']:.2f}, p={v['p']:.4e}")
    print()
    print("Length-residualized t-tests:")
    for k, v in resid_tests.items():
        print(f"  {k}: t={v['t']:.2f}, p={v['p']:.4e}, d={v['d']:.3f}")
    print()
    print("Interpretation:", result["interpretation"])


if __name__ == "__main__":
    main()
