# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-26 (authoritative run on full N=6072 dataset — 39 batches, 27 models)
N total: 6072 | N per condition: deprivation=2014, counterfactual=2044, neutral=2014
Data sources (39 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v3_expand.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (27): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=6072, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0615 | 0.005 | -12.32 | <0.001*** |
  | cond_D | 0.1617 | 0.0049 | 32.989 | <0.001*** |
  | cond_C | 0.2097 | 0.0052 | 40.598 | <0.001*** |
  | pers_rfl | 0.018 | 0.002 | 9.068 | <0.001*** |
  | pers_rum | 0.0374 | 0.002 | 18.581 | <0.001*** |
  | temp_z | -0.0022 | 0.0009 | -2.402 | 0.0163* |

### Regret-word rate (`regret_rate`)
  N=6072, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0263 | 0.0722 | 0.364 | 0.7158 n.s. |
  | cond_D | 0.3352 | 0.072 | 4.654 | <0.001*** |
  | cond_C | 0.4026 | 0.0752 | 5.353 | <0.001*** |
  | pers_rfl | -0.0016 | 0.0296 | -0.056 | 0.9556 n.s. |
  | pers_rum | 0.2799 | 0.03 | 9.331 | <0.001*** |
  | temp_z | -0.0095 | 0.0136 | -0.699 | 0.4844 n.s. |

### Counterfactual rate (`cf_rate`)
  N=6072

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.3068 | 0.128 | 2.397 | 0.0165* |
  | cond_D | 0.3396 | 0.0992 | 3.422 | <0.001*** |
  | cond_C | 1.1256 | 0.1051 | 10.706 | <0.001*** |
  | pers_rfl | 0.0166 | 0.037 | 0.449 | 0.6534 n.s. |
  | pers_rum | 0.3118 | 0.0376 | 8.301 | <0.001*** |
  | temp_z | -0.0325 | 0.0171 | -1.905 | 0.0567 (borderline) |

### Negative emotion rate (`negemo_rate`)
  N=6072

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0573 | 0.0224 | 2.552 | 0.0107* |
  | cond_D | 0.153 | 0.0269 | 5.692 | <0.001*** |
  | cond_C | 0.0938 | 0.0276 | 3.394 | <0.001*** |
  | pers_rfl | -0.0073 | 0.016 | -0.454 | 0.6501 n.s. |
  | pers_rum | -0.0012 | 0.0162 | -0.076 | 0.9397 n.s. |
  | temp_z | -0.0094 | 0.0071 | -1.323 | 0.1858 n.s. |

## Descriptive: Condition means (N=6072)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2014 | — | — | — | — |
| deprivation | 2014 | t=16.416, p<0.001 | 0.517 | t=60.333, p<0.001 | 1.901 |
| counterfactual | 2044 | t=8.833, p<0.001 | 0.276 | t=70.858, p<0.001 | 2.226 |

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
| gpt-3.5-turbo | 60 | 0.2291 | -0.0363 | 1.778 |
| gpt-4.1 | 108 | 0.1413 | -0.0243 | 1.440 |
| gpt-4.1-mini | 72 | 0.1430 | -0.0446 | 1.597 |
| gpt-4o | 198 | 0.1008 | -0.0525 | 1.662 |
| gpt-4o-mini | 122 | 0.1530 | -0.0065 | 1.493 |
| gpt-5.4-mini | 54 | 0.1075 | 0.0775 | 0.419 |
| gpt-5.4-nano | 54 | 0.0710 | 0.0372 | 0.491 |
| compound | 52 | 0.1337 | -0.0574 | 1.796 |
| compound-mini | 35 | 0.1261 | -0.0644 | 1.851 |
| llama-3.1-8b-instant | 51 | 0.1435 | -0.0264 | 1.728 |
| llama-3.3-70b-versatile | 72 | 0.1675 | 0.0661 | 1.168 |
| llama-4-scout-17b-16e-instruct | 72 | 0.1103 | 0.0432 | 0.779 |
| kimi-k2-instruct | 54 | 0.0702 | -0.0256 | 1.417 |
| kimi-k2-instruct-0905 | 54 | 0.0736 | -0.0223 | 1.412 |
| o4-mini | 34 | 0.0700 | -0.0160 | 1.184 |
| gpt-oss-120b | 38 | 0.1128 | -0.0568 | 1.772 |
| gpt-oss-20b | 40 | 0.1167 | -0.0447 | 1.629 |
| gpt-oss-safeguard-20b | 54 | 0.1091 | -0.0575 | 1.627 |
| qwen3-32b | 72 | 0.1032 | 0.0160 | 1.420 |

All 27 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=0.00062, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=32.989, p<0.001) and C (z=40.598, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=18.581, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 27 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.2097, z=40.598, p<0.001) comparably to deprivation (beta=0.1617, z=32.989, p<0.001). CF rate (deprivation): p=0.00062. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=6072)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
