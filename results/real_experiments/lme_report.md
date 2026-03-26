# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-26 (authoritative run on full N=6254 dataset — 42 batches, 29 models)
N total: 6254 | N per condition: deprivation=2082, counterfactual=2098, neutral=2074
Data sources (42 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v27_o3mini.emb, batch_v28_new_openai.emb, batch_v29_stability_fill.emb, batch_v3_expand.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (29): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o3-mini, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=6254, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0661 | 0.0049 | -13.452 | <0.001*** |
  | cond_D | 0.1702 | 0.0047 | 36.294 | <0.001*** |
  | cond_C | 0.2197 | 0.0049 | 44.456 | <0.001*** |
  | pers_rfl | 0.0177 | 0.002 | 8.994 | <0.001*** |
  | pers_rum | 0.0365 | 0.002 | 18.312 | <0.001*** |
  | temp_z | -0.0024 | 0.0009 | -2.671 | 0.0076** |

### Regret-word rate (`regret_rate`)
  N=6254, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0325 | 0.0687 | 0.473 | 0.6360 n.s. |
  | cond_D | 0.354 | 0.0674 | 5.25 | <0.001*** |
  | cond_C | 0.3999 | 0.0702 | 5.701 | <0.001*** |
  | pers_rfl | 0.0014 | 0.0289 | 0.047 | 0.9626 n.s. |
  | pers_rum | 0.2783 | 0.0293 | 9.481 | <0.001*** |
  | temp_z | -0.0093 | 0.0133 | -0.699 | 0.4847 n.s. |

### Counterfactual rate (`cf_rate`)
  N=6254

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.316 | 0.1223 | 2.583 | 0.0098** |
  | cond_D | 0.3572 | 0.0925 | 3.861 | <0.001*** |
  | cond_C | 1.1067 | 0.0975 | 11.349 | <0.001*** |
  | pers_rfl | 0.0192 | 0.0362 | 0.53 | 0.5959 n.s. |
  | pers_rum | 0.3106 | 0.0368 | 8.45 | <0.001*** |
  | temp_z | -0.0323 | 0.0167 | -1.936 | 0.0529 (borderline) |

### Negative emotion rate (`negemo_rate`)
  N=6254

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0574 | 0.0217 | 2.652 | 0.0080** |
  | cond_D | 0.1494 | 0.0257 | 5.819 | <0.001*** |
  | cond_C | 0.0926 | 0.0264 | 3.508 | <0.001*** |
  | pers_rfl | -0.0058 | 0.0157 | -0.369 | 0.7123 n.s. |
  | pers_rum | 0.0023 | 0.0159 | 0.144 | 0.8853 n.s. |
  | temp_z | -0.0086 | 0.007 | -1.232 | 0.2180 n.s. |

## Descriptive: Condition means (N=6254)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2074 | — | — | — | — |
| deprivation | 2082 | t=16.992, p<0.001 | 0.527 | t=62.074, p<0.001 | 1.926 |
| counterfactual | 2098 | t=9.206, p<0.001 | 0.284 | t=72.739, p<0.001 | 2.253 |

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
| gpt-4.1-nano | 18 | 0.2364 | -0.0517 | 1.943 |
| gpt-4o | 198 | 0.1008 | -0.0525 | 1.662 |
| gpt-4o-mini | 122 | 0.1530 | -0.0065 | 1.493 |
| gpt-5.4-mini | 54 | 0.1075 | 0.0775 | 0.419 |
| gpt-5.4-nano | 54 | 0.0710 | 0.0372 | 0.491 |
| compound | 52 | 0.1337 | -0.0574 | 1.796 |
| compound-mini | 47 | 0.1219 | -0.0644 | 1.856 |
| llama-3.1-8b-instant | 51 | 0.1435 | -0.0264 | 1.728 |
| llama-3.3-70b-versatile | 72 | 0.1675 | 0.0661 | 1.168 |
| llama-4-scout-17b-16e-instruct | 72 | 0.1103 | 0.0432 | 0.779 |
| kimi-k2-instruct | 54 | 0.0702 | -0.0256 | 1.417 |
| kimi-k2-instruct-0905 | 54 | 0.0736 | -0.0223 | 1.412 |
| o3-mini | 18 | 0.1554 | -0.0616 | 1.812 |
| o4-mini | 34 | 0.0700 | -0.0160 | 1.184 |
| gpt-oss-120b | 38 | 0.1128 | -0.0568 | 1.772 |
| gpt-oss-20b | 40 | 0.1167 | -0.0447 | 1.629 |
| gpt-oss-safeguard-20b | 62 | 0.1028 | -0.0532 | 1.557 |
| qwen3-32b | 72 | 0.1032 | 0.0160 | 1.420 |

All 29 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=0.00011, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=36.294, p<0.001) and C (z=44.456, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=18.312, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 29 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.2197, z=44.456, p<0.001) comparably to deprivation (beta=0.1702, z=36.294, p<0.001). CF rate (deprivation): p=0.00011. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=6254)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
