# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-26 (authoritative run on full N=6,636 dataset — 46 batches, 32 models)
N total: 6,636 | N per condition: deprivation=2,217, counterfactual=2,230, neutral=2,189
Data sources (46 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v27_o3mini.emb, batch_v28_new_openai.emb, batch_v29_stability_fill.emb, batch_v30_stability_fill2.emb, batch_v31_gpt54full.emb, batch_v32_o1_o3.emb, batch_v3_expand.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (32): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o1, o3, o3-mini, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=6,636, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0729 | 0.0049 | -14.992 | <0.001*** |
  | cond_D | 0.1785 | 0.0043 | 41.971 | <0.001*** |
  | cond_C | 0.2298 | 0.0045 | 51.408 | <0.001*** |
  | pers_rfl | 0.0187 | 0.0019 | 9.771 | <0.001*** |
  | pers_rum | 0.0376 | 0.0019 | 19.305 | <0.001*** |
  | temp_z | -0.002 | 0.0009 | -2.249 | 0.0245* |

### Regret-word rate (`regret_rate`)
  N=6,636, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.072 | 0.0666 | 1.081 | 0.2795 n.s. |
  | cond_D | 0.2866 | 0.0601 | 4.767 | <0.001*** |
  | cond_C | 0.3192 | 0.0624 | 5.113 | <0.001*** |
  | pers_rfl | 0.0157 | 0.0277 | 0.567 | 0.5705 n.s. |
  | pers_rum | 0.2927 | 0.0281 | 10.407 | <0.001*** |
  | temp_z | -0.0078 | 0.0126 | -0.621 | 0.5349 n.s. |

### Counterfactual rate (`cf_rate`)
  N=6,636

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.4079 | 0.1228 | 3.323 | <0.001*** |
  | cond_D | 0.2777 | 0.081 | 3.429 | <0.001*** |
  | cond_C | 0.8384 | 0.0851 | 9.856 | <0.001*** |
  | pers_rfl | 0.0507 | 0.0348 | 1.458 | 0.1449 n.s. |
  | pers_rum | 0.3425 | 0.0353 | 9.701 | <0.001*** |
  | temp_z | -0.0287 | 0.0159 | -1.804 | 0.0713 (borderline) |

### Negative emotion rate (`negemo_rate`)
  N=6,636

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0601 | 0.0209 | 2.879 | 0.0040** |
  | cond_D | 0.1331 | 0.0242 | 5.498 | <0.001*** |
  | cond_C | 0.0827 | 0.0248 | 3.34 | <0.001*** |
  | pers_rfl | 0.0021 | 0.015 | 0.14 | 0.8883 n.s. |
  | pers_rum | 0.0102 | 0.0152 | 0.669 | 0.5032 n.s. |
  | temp_z | -0.0075 | 0.0067 | -1.127 | 0.2597 n.s. |

## Descriptive: Condition means (N=6,636)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2153 | — | — | — | — |
| deprivation | 2181 | t=16.885, p<0.001 | 0.511 | t=64.613, p<0.001 | 1.963 |
| counterfactual | 2188 | t=9.184, p<0.001 | 0.277 | t=75.912, p<0.001 | 2.305 |

## Cross-model: Embedding Regret Bias by Model (D condition)

| Model | n_D | D_bias | N_bias | d(D-N) |
|---|---|---|---|---|
| allam-2-7b | 38 | 0.1185 | -0.0092 | 1.525 |
| gemini-2.5-flash | 351 | 0.0941 | -0.0518 | 1.344 |
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
| gpt-5.4 | 30 | 0.1498 | -0.0979 | 1.859 |
| gpt-5.4-mini | 54 | 0.1075 | 0.0775 | 0.419 |
| gpt-5.4-nano | 54 | 0.0710 | 0.0372 | 0.491 |
| compound | 52 | 0.1337 | -0.0574 | 1.796 |
| compound-mini | 47 | 0.1219 | -0.0644 | 1.856 |
| llama-3.1-8b-instant | 51 | 0.1435 | -0.0264 | 1.728 |
| llama-3.3-70b-versatile | 72 | 0.1675 | 0.0661 | 1.168 |
| llama-4-scout-17b-16e-instruct | 72 | 0.1103 | 0.0432 | 0.779 |
| kimi-k2-instruct | 54 | 0.0702 | -0.0256 | 1.417 |
| kimi-k2-instruct-0905 | 54 | 0.0736 | -0.0223 | 1.412 |
| o1 | 24 | 0.0928 | -0.0971 | 1.816 |
| o3 | 19 | 0.0682 | -0.0853 | 1.859 |
| o3-mini | 30 | 0.1359 | -0.0654 | 1.777 |
| o4-mini | 36 | 0.0730 | -0.0169 | 1.221 |
| gpt-oss-120b | 38 | 0.1128 | -0.0568 | 1.772 |
| gpt-oss-20b | 40 | 0.1167 | -0.0447 | 1.629 |
| gpt-oss-safeguard-20b | 62 | 0.1028 | -0.0532 | 1.557 |
| qwen3-32b | 72 | 0.1032 | 0.0160 | 1.420 |

All 32 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=0.0006, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=41.971, p<0.001) and C (z=51.408, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=19.305, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 32 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.2298, z=51.408, p<0.001) comparably to deprivation (beta=0.1785, z=41.971, p<0.001). CF rate (deprivation): p=0.0006. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=6,636)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
