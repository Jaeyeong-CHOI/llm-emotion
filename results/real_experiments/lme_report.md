# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-26 (authoritative run on full N=7440 dataset — 53 batches, 37 models)
N total: 7440 | N per condition: deprivation=2436, counterfactual=2514, neutral=2490
Data sources (53 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v27_o3mini.emb, batch_v28_new_openai.emb, batch_v29_stability_fill.emb, batch_v30_stability_fill2.emb, batch_v31_gpt54full.emb, batch_v32_o1_o3.emb, batch_v33_o1_o3_neutral_fill.emb, batch_v34_gpt5_family.emb, batch_v35_gpt51_gpt52.emb, batch_v36_stability_fill.emb, batch_v36b_final_fill.emb, batch_v36c_gpt5_dep.emb, batch_v37_groq_balance.emb, batch_v3_expand.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (37): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, gpt-5, gpt-5-mini, gpt-5-nano, gpt-5.1, gpt-5.2, gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o1, o3, o3-mini, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=7440, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0773 | 0.0044 | -17.42 | <0.001*** |
  | cond_D | 0.1787 | 0.0034 | 52.214 | <0.001*** |
  | cond_C | 0.243 | 0.0035 | 70.168 | <0.001*** |
  | pers_rfl | 0.019 | 0.0018 | 10.378 | <0.001*** |
  | pers_rum | 0.0361 | 0.0019 | 19.423 | <0.001*** |
  | temp_z | 0.0006 | 0.0008 | 0.714 | 0.4752 n.s. |

### Regret-word rate (`regret_rate`)
  N=7440, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.1269 | 0.0576 | 2.202 | 0.0277* |
  | cond_D | 0.2201 | 0.0459 | 4.801 | <0.001*** |
  | cond_C | 0.2324 | 0.0458 | 5.078 | <0.001*** |
  | pers_rfl | 0.0103 | 0.0248 | 0.417 | 0.6765 n.s. |
  | pers_rum | 0.2624 | 0.0251 | 10.445 | <0.001*** |
  | temp_z | -0.0246 | 0.0114 | -2.17 | 0.0300* |

### Counterfactual rate (`cf_rate`)
  N=7440

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.4789 | 0.1109 | 4.317 | <0.001*** |
  | cond_D | 0.2358 | 0.0605 | 3.898 | <0.001*** |
  | cond_C | 0.6558 | 0.0606 | 10.829 | <0.001*** |
  | pers_rfl | 0.0423 | 0.0314 | 1.348 | 0.1778 n.s. |
  | pers_rum | 0.3096 | 0.0318 | 9.724 | <0.001*** |
  | temp_z | -0.0568 | 0.0144 | -3.936 | <0.001*** |

### Negative emotion rate (`negemo_rate`)
  N=7440

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0666 | 0.0178 | 3.737 | <0.001*** |
  | cond_D | 0.115 | 0.0201 | 5.716 | <0.001*** |
  | cond_C | 0.0732 | 0.0201 | 3.647 | <0.001*** |
  | pers_rfl | 0.0019 | 0.0133 | 0.14 | 0.8888 n.s. |
  | pers_rum | 0.0082 | 0.0135 | 0.61 | 0.5418 n.s. |
  | temp_z | -0.0112 | 0.006 | -1.874 | 0.0609 (borderline) |

## Descriptive: Condition means (N=7440)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2490 | — | — | — | — |
| deprivation | 2436 | t=17.114, p<0.001 | 0.491 | t=71.272, p<0.001 | 2.032 |
| counterfactual | 2514 | t=9.555, p<0.001 | 0.269 | t=84.943, p<0.001 | 2.401 |

## Cross-model: Embedding Regret Bias by Model (D condition)

| Model | n_D | D_bias | N_bias | d(D-N) |
|---|---|---|---|---|
| allam-2-7b | 50 | 0.1174 | -0.0092 | 1.507 |
| gemini-2.5-flash | 387 | 0.0844 | -0.0562 | 1.299 |
| gemini-2.5-flash-lite | 72 | 0.1123 | 0.0246 | 0.986 |
| gemini-2.5-pro | 71 | 0.0976 | 0.0141 | 1.250 |
| gemini-3-flash-preview | 54 | 0.1145 | -0.0154 | 1.516 |
| gemini-3-pro-preview | 40 | 0.0605 | -0.0321 | 1.227 |
| gemini-3.1-flash-lite-preview | 36 | 0.1378 | -0.0133 | 1.692 |
| gemini-3.1-pro-preview | 56 | 0.0509 | -0.0410 | 1.053 |
| gpt-3.5-turbo | 72 | 0.2278 | -0.0354 | 1.755 |
| gpt-4.1 | 108 | 0.1413 | -0.0243 | 1.440 |
| gpt-4.1-mini | 72 | 0.1430 | -0.0446 | 1.597 |
| gpt-4.1-nano | 30 | 0.1963 | -0.0958 | 1.841 |
| gpt-4o | 198 | 0.1008 | -0.0525 | 1.662 |
| gpt-4o-mini | 122 | 0.1530 | -0.0065 | 1.493 |
| gpt-5 | 30 | 0.0970 | -0.0268 | 1.675 |
| gpt-5-mini | 33 | 0.1427 | -0.0459 | 1.840 |
| gpt-5-nano | 36 | 0.1443 | -0.0626 | 1.854 |
| gpt-5.1 | 30 | 0.1184 | -0.0265 | 1.739 |
| gpt-5.2 | 30 | 0.1436 | -0.0136 | 1.591 |
| gpt-5.4 | 30 | 0.1498 | -0.0979 | 1.859 |
| gpt-5.4-mini | 54 | 0.1075 | 0.0775 | 0.419 |
| gpt-5.4-nano | 54 | 0.0710 | 0.0372 | 0.491 |
| compound | 52 | 0.1337 | -0.0634 | 1.794 |
| compound-mini | 50 | 0.1230 | -0.0671 | 1.856 |
| llama-3.1-8b-instant | 51 | 0.1435 | -0.0264 | 1.728 |
| llama-3.3-70b-versatile | 72 | 0.1675 | 0.0306 | 1.327 |
| llama-4-scout-17b-16e-instruct | 72 | 0.1103 | 0.0119 | 1.038 |
| kimi-k2-instruct | 54 | 0.0702 | -0.0256 | 1.417 |
| kimi-k2-instruct-0905 | 54 | 0.0736 | -0.0223 | 1.412 |
| o1 | 30 | 0.1033 | -0.1042 | 1.806 |
| o3 | 30 | 0.0685 | -0.0957 | 1.858 |
| o3-mini | 30 | 0.1359 | -0.0654 | 1.777 |
| o4-mini | 36 | 0.0730 | -0.0169 | 1.221 |
| gpt-oss-120b | 52 | 0.1154 | -0.0568 | 1.776 |
| gpt-oss-20b | 54 | 0.1207 | -0.0447 | 1.634 |
| gpt-oss-safeguard-20b | 62 | 0.1028 | -0.0532 | 1.557 |
| qwen3-32b | 72 | 0.1032 | -0.0126 | 1.501 |

All 37 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=0.0001, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=52.214, p<0.001) and C (z=70.168, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=19.423, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 37 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.243, z=70.168, p<0.001) comparably to deprivation (beta=0.1787, z=52.214, p<0.001). CF rate (deprivation): p=0.0001. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=7440)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
