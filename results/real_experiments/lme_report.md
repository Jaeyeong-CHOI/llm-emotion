# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-25 (re-run on full N=1084 dataset)
N total: 1084 | N per condition: neutral=299, deprivation=378, counterfactual=407
Data sources: batch_v1_pilot_openai, batch_v1_gemini_v2, batch_v4_expand_gpt4o, batch_v5_expand_both, batch_v6_expand, batch_v7_expand

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_hi + (1|scenario)

Note: Previous lme_report.md (N=216) was from an earlier partial run. This file reports the full-dataset LME results that match the paper's reported statistics.

### Regret-word rate (`regret_rate`)
  N=1084, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.5878 | 0.5099 | 1.153 | 0.249 |
  | cond_C | 0.1186 | 0.5371 | 0.221 | 0.825 |
  | pers_rum | 0.5134 | 0.0739 | 6.954 | <0.001*** |
  | pers_rfl | — | — | — | — |
  | temp_hi | — | — | — | — |

### Counterfactual rate (`cf_rate`)
  N=1084

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.6382 | 0.5482 | 1.164 | 0.244 |
  | cond_C | 0.1679 | 0.5780 | 0.290 | 0.771 |
  | pers_rum | 0.5655 | 0.0722 | 7.826 | <0.001*** |

### Negative emotion rate (`negemo_rate`)
  N=1084

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.2102 | 0.1507 | 1.395 | 0.163 |
  | cond_C | 0.0409 | 0.1549 | 0.264 | 0.792 |

### Semantic regret bias (`semantic_regret_bias`)
  N=1084

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.4999 | 0.0443 | 11.283 | <0.001*** |
  | cond_C | 0.4809 | 0.0461 | 10.434 | <0.001*** |
  | pers_rum | 0.0006 | 0.0120 | 0.050 | 0.960 |

## Descriptive: Condition means (N=1084)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (sem_bias) | d |
|---|---|---|---|---|---|
| neutral | 299 | — | — | — | — |
| deprivation | 378 | t=7.07, p<0.001 | 0.486 (pooled-SD Cohen's d) | t=27.17, p<0.001 | 2.306 |
| counterfactual | 407 | t=2.86, p=0.004 | 0.187 | t=28.03, p<0.001 | 2.470 |

## Data Note
Per-sample marker extraction run via `analyze_real_results.analyze()` on raw output text from all 6 batch files.
The bag-of-words semantic_regret_bias metric computes sim(output, regret_tokens) - sim(output, neutral_tokens).
This metric is sensitive to lexical overlap and the Gemini/GPT-4o response length difference (~19 vs ~125 tokens) explains part of the magnitude difference across models.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json

**Note on lme_results.json vs lme_analysis.json:**
`lme_results.json` is a legacy file from an earlier partial-dataset run (N=216, balanced 72/72/72).
`lme_analysis.json` is the current authoritative file (N=1084, full 6-batch corpus).
The paper's reported statistics (β=0.500, z=11.28 for semantic_regret_bias) are sourced from lme_analysis.json.
The legacy lme_results.json should be treated as a historical artifact only.

**Cohen's d computation:** All d-values in this report use the standard pooled-variance formula: 
d = (mean_A − mean_B) / sqrt(((n_A−1)·var_A + (n_B−1)·var_B) / (n_A+n_B−2)).
Earlier runs used population SD of the combined sample (pstdev), which underestimates d; the paper values use the correct pooled-SD formula.
