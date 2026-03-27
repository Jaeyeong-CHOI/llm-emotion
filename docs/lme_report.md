# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-27 (authoritative run on full N=7649 dataset — 56 batches, 39 models)
N total: 7649 | N per condition: deprivation=2469, counterfactual=2547, neutral=2526
Data sources (56 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v27_o3mini.emb, batch_v28_new_openai.emb, batch_v29_stability_fill.emb, batch_v30_stability_fill2.emb, batch_v31_gpt54full.emb, batch_v32_o1_o3.emb, batch_v33_o1_o3_neutral_fill.emb, batch_v34_gpt5_family.emb, batch_v35_gpt51_gpt52.emb, batch_v36_stability_fill.emb, batch_v36b_final_fill.emb, batch_v36c_gpt5_dep.emb, batch_v37_groq_balance.emb, batch_v38_explicit_instruction.emb, batch_v39_new_models.emb, batch_v3_expand.emb, batch_v40_gpt5pro_fill.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (39): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-pro, gpt-5.1, gpt-5.2, gpt-5.3-chat-latest, gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o1, o3, o3-mini, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=7649, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0755 | 0.0044 | -17.256 | <0.001*** |
  | cond_D | 0.1772 | 0.0033 | 53.042 | <0.001*** |
  | cond_C | 0.2401 | 0.0034 | 71.095 | <0.001*** |
  | pers_rfl | 0.0186 | 0.0018 | 10.191 | <0.001*** |
  | pers_rum | 0.0355 | 0.0018 | 19.183 | <0.001*** |
  | temp_z | 0.0003 | 0.0008 | 0.407 | 0.6837 n.s. |

### Regret-word rate (`regret_rate`)
  N=7649, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.1358 | 0.0574 | 2.367 | 0.0179* |
  | cond_D | 0.2097 | 0.0446 | 4.707 | <0.001*** |
  | cond_C | 0.2213 | 0.0445 | 4.976 | <0.001*** |
  | pers_rfl | 0.0097 | 0.0244 | 0.396 | 0.6920 n.s. |
  | pers_rum | 0.2579 | 0.0248 | 10.411 | <0.001*** |
  | temp_z | -0.0267 | 0.0113 | -2.366 | 0.0180* |

### Counterfactual rate (`cf_rate`)
  N=7649

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.4956 | 0.1111 | 4.462 | <0.001*** |
  | cond_D | 0.2237 | 0.0586 | 3.816 | <0.001*** |
  | cond_C | 0.6228 | 0.0587 | 10.611 | <0.001*** |
  | pers_rfl | 0.0408 | 0.0309 | 1.318 | 0.1873 n.s. |
  | pers_rum | 0.3039 | 0.0314 | 9.678 | <0.001*** |
  | temp_z | -0.06 | 0.0143 | -4.194 | <0.001*** |

### Negative emotion rate (`negemo_rate`)
  N=7649

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0685 | 0.0176 | 3.889 | <0.001*** |
  | cond_D | 0.1114 | 0.0197 | 5.638 | <0.001*** |
  | cond_C | 0.0709 | 0.0197 | 3.604 | <0.001*** |
  | pers_rfl | 0.0016 | 0.0131 | 0.125 | 0.9003 n.s. |
  | pers_rum | 0.0079 | 0.0133 | 0.593 | 0.5535 n.s. |
  | temp_z | -0.0118 | 0.006 | -1.981 | 0.0476* |

## Descriptive: Condition means (N=7649)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2526 | — | — | — | — |
| deprivation | 2469 | t=17.101, p<0.001 | 0.488 | t=71.965, p<0.001 | 2.038 |
| counterfactual | 2547 | t=9.556, p<0.001 | 0.268 | t=85.715, p<0.001 | 2.406 |

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
| gpt-5-pro | 6 | 0.0000 | -0.0140 | 0.679 |
| gpt-5.1 | 30 | 0.1184 | -0.0265 | 1.739 |
| gpt-5.2 | 30 | 0.1436 | -0.0136 | 1.591 |
| gpt-5.3-chat-latest | 27 | 0.1414 | -0.0400 | 1.785 |
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

All 39 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=0.00014, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=53.042, p<0.001) and C (z=71.095, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=19.183, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 39 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.2401, z=71.095, p<0.001) comparably to deprivation (beta=0.1772, z=53.042, p<0.001). CF rate (deprivation): p=0.00014. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=7649)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
