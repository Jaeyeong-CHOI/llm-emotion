# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-27 (authoritative run on full N=8110 dataset — 63 batches, 39 models)
N total: 8110 | N per condition: deprivation=2677, counterfactual=2662, neutral=2664
Data sources (63 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v27_o3mini.emb, batch_v28_new_openai.emb, batch_v29_stability_fill.emb, batch_v30_stability_fill2.emb, batch_v31_gpt54full.emb, batch_v32_o1_o3.emb, batch_v33_o1_o3_neutral_fill.emb, batch_v34_gpt5_family.emb, batch_v35_gpt51_gpt52.emb, batch_v36_stability_fill.emb, batch_v36b_final_fill.emb, batch_v36c_gpt5_dep.emb, batch_v37_groq_balance.emb, batch_v38_explicit_instruction.emb, batch_v39_new_models.emb, batch_v3_expand.emb, batch_v40_gpt5pro_fill.emb, batch_v41_dep_balance.emb, batch_v42_cf_neutral_balance.emb, batch_v43_gpt5pro_stabilize.emb, batch_v44_nano_o3mini_stabilize.emb, batch_v45_stabilize_final.emb, batch_v46_gpt5pro_cf_fill.emb, batch_v47_stability_fill.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (39): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-pro, gpt-5.1, gpt-5.2, gpt-5.3-chat-latest, gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o1, o3, o3-mini, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=8110, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.071 | 0.0038 | -18.495 | <0.001*** |
  | cond_D | 0.1737 | 0.0031 | 55.196 | <0.001*** |
  | cond_C | 0.2283 | 0.0032 | 70.436 | <0.001*** |
  | pers_rfl | 0.0178 | 0.0018 | 9.776 | <0.001*** |
  | pers_rum | 0.0346 | 0.0019 | 18.677 | <0.001*** |
  | temp_z | 0.001 | 0.0008 | 1.165 | 0.2439 n.s. |

### Regret-word rate (`regret_rate`)
  N=8110, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.1035 | 0.0508 | 2.038 | 0.0415* |
  | cond_D | 0.2345 | 0.0409 | 5.728 | <0.001*** |
  | cond_C | 0.2081 | 0.0418 | 4.976 | <0.001*** |
  | pers_rfl | 0.008 | 0.0239 | 0.335 | 0.7377 n.s. |
  | pers_rum | 0.2543 | 0.0242 | 10.5 | <0.001*** |
  | temp_z | -0.0267 | 0.0108 | -2.476 | 0.0133* |

### Counterfactual rate (`cf_rate`)
  N=8110

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.4135 | 0.0978 | 4.23 | <0.001*** |
  | cond_D | 0.222 | 0.0559 | 3.969 | <0.001*** |
  | cond_C | 0.6642 | 0.0573 | 11.587 | <0.001*** |
  | pers_rfl | 0.0348 | 0.0313 | 1.112 | 0.2659 n.s. |
  | pers_rum | 0.2976 | 0.0317 | 9.378 | <0.001*** |
  | temp_z | -0.0538 | 0.0142 | -3.801 | <0.001*** |

### Negative emotion rate (`negemo_rate`)
  N=8110

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.061 | 0.0167 | 3.641 | <0.001*** |
  | cond_D | 0.1151 | 0.0186 | 6.196 | <0.001*** |
  | cond_C | 0.0729 | 0.0189 | 3.864 | <0.001*** |
  | pers_rfl | 0.0018 | 0.013 | 0.136 | 0.8917 n.s. |
  | pers_rum | 0.0135 | 0.0131 | 1.03 | 0.3029 n.s. |
  | temp_z | -0.0101 | 0.0058 | -1.736 | 0.0825 (borderline) |

## Descriptive: Condition means (N=8110)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2664 | — | — | — | — |
| deprivation | 2677 | t=18.003, p<0.001 | 0.492 | t=74.466, p<0.001 | 2.038 |
| counterfactual | 2662 | t=9.838, p<0.001 | 0.27 | t=87.148, p<0.001 | 2.388 |

## Cross-model: Embedding Regret Bias by Model (D condition)

| Model | n_D | D_bias | N_bias | d(D-N) |
|---|---|---|---|---|
| allam-2-7b | 50 | 0.1174 | -0.0092 | 1.507 |
| gemini-2.5-flash | 437 | 0.0833 | -0.0562 | 1.301 |
| gemini-2.5-flash-lite | 72 | 0.1123 | 0.0164 | 1.114 |
| gemini-2.5-pro | 71 | 0.0976 | 0.0095 | 1.344 |
| gemini-3-flash-preview | 54 | 0.1145 | -0.0150 | 1.515 |
| gemini-3-pro-preview | 40 | 0.0605 | -0.0321 | 1.227 |
| gemini-3.1-flash-lite-preview | 36 | 0.1378 | -0.0133 | 1.692 |
| gemini-3.1-pro-preview | 56 | 0.0509 | -0.0410 | 1.053 |
| gpt-3.5-turbo | 72 | 0.2278 | -0.0354 | 1.755 |
| gpt-4.1 | 108 | 0.1413 | -0.0299 | 1.474 |
| gpt-4.1-mini | 72 | 0.1430 | -0.0446 | 1.597 |
| gpt-4.1-nano | 42 | 0.1944 | -0.0931 | 1.850 |
| gpt-4o | 298 | 0.1115 | -0.0525 | 1.672 |
| gpt-4o-mini | 122 | 0.1530 | -0.0132 | 1.516 |
| gpt-5 | 30 | 0.0970 | -0.0268 | 1.675 |
| gpt-5-mini | 33 | 0.1427 | -0.0459 | 1.840 |
| gpt-5-nano | 36 | 0.1443 | -0.0626 | 1.854 |
| gpt-5-pro | 40 | -0.0010 | -0.0034 | 0.247 |
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
| o3-mini | 42 | 0.1450 | -0.0685 | 1.807 |
| o4-mini | 36 | 0.0730 | -0.0169 | 1.221 |
| gpt-oss-120b | 52 | 0.1154 | -0.0568 | 1.776 |
| gpt-oss-20b | 54 | 0.1207 | -0.0447 | 1.634 |
| gpt-oss-safeguard-20b | 62 | 0.1028 | -0.0532 | 1.557 |
| qwen3-32b | 72 | 0.1032 | -0.0126 | 1.501 |

All 39 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=7e-05, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=55.196, p<0.001) and C (z=70.436, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=18.677, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 39 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.2283, z=70.436, p<0.001) comparably to deprivation (beta=0.1737, z=55.196, p<0.001). CF rate (deprivation): p=7e-05. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=8110)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
