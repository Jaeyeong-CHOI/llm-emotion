# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-26 (authoritative run on full N=6126 dataset — 40 batches, 28 models)
N total: 6126 | N per condition: deprivation=2032, counterfactual=2062, neutral=2032
Data sources (40 batches): batch_gemini25flashlite.emb, batch_gemini25pro.emb, batch_gemini31pro.emb, batch_gemini3flash.emb, batch_gemini3pro.emb, batch_gpt41.emb, batch_gpt41mini.emb, batch_gpt4omini.emb, batch_gpt54mini.emb, batch_gpt54nano.emb, batch_llama33_70b.emb, batch_llama4_scout.emb, batch_qwen3_32b.emb, batch_v10_neutral_expand.emb, batch_v11_neutral_balance2.emb, batch_v12_gemini3pro_cf.emb, batch_v13_openai_balance.emb, batch_v14_balance.emb, batch_v15_new_models.emb, batch_v16_oss_small.emb, batch_v17_groq_compound.emb, batch_v18_new_groq.emb, batch_v19_groq_fill.emb, batch_v1_gemini_v2.emb, batch_v1_pilot_openai.emb, batch_v20_safeguard.emb, batch_v21_gemini_new.emb, batch_v22_cf_fill.emb, batch_v23_new_openai.emb, batch_v24_fill_cells.emb, batch_v25_groq_compound_balance.emb, batch_v26_lowcount_fill.emb, batch_v27_o3mini.emb, batch_v3_expand.emb, batch_v4_expand_gpt4o.emb, batch_v5_expand_both.emb, batch_v6_expand.emb, batch_v7_expand.emb, batch_v8_neutral_balance.emb, batch_v9_gpt35.emb
Models (28): allam-2-7b, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-5.4-mini, gpt-5.4-nano, groq/compound, groq/compound-mini, llama-3.1-8b-instant, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, moonshotai/kimi-k2-instruct, moonshotai/kimi-k2-instruct-0905, o3-mini, o4-mini, openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=6126, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0639 | 0.005 | -12.815 | <0.001*** |
  | cond_D | 0.1645 | 0.0048 | 34.314 | <0.001*** |
  | cond_C | 0.2151 | 0.0051 | 42.492 | <0.001*** |
  | pers_rfl | 0.0179 | 0.002 | 9.061 | <0.001*** |
  | pers_rum | 0.0371 | 0.002 | 18.487 | <0.001*** |
  | temp_z | -0.0022 | 0.0009 | -2.44 | 0.0147* |

### Regret-word rate (`regret_rate`)
  N=6126, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0127 | 0.0714 | 0.178 | 0.8587 n.s. |
  | cond_D | 0.3637 | 0.0701 | 5.191 | <0.001*** |
  | cond_C | 0.4158 | 0.073 | 5.696 | <0.001*** |
  | pers_rfl | -0.0004 | 0.0294 | -0.013 | 0.9896 n.s. |
  | pers_rum | 0.2787 | 0.0298 | 9.359 | <0.001*** |
  | temp_z | -0.0099 | 0.0135 | -0.734 | 0.4627 n.s. |

### Counterfactual rate (`cf_rate`)
  N=6126

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.2805 | 0.1266 | 2.216 | 0.0267* |
  | cond_D | 0.3733 | 0.096 | 3.889 | <0.001*** |
  | cond_C | 1.1701 | 0.1012 | 11.558 | <0.001*** |
  | pers_rfl | 0.0192 | 0.0368 | 0.522 | 0.6014 n.s. |
  | pers_rum | 0.3123 | 0.0373 | 8.369 | <0.001*** |
  | temp_z | -0.0328 | 0.0169 | -1.939 | 0.0526 (borderline) |

### Negative emotion rate (`negemo_rate`)
  N=6126

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0573 | 0.0223 | 2.577 | 0.0100** |
  | cond_D | 0.1535 | 0.0265 | 5.791 | <0.001*** |
  | cond_C | 0.0923 | 0.0272 | 3.389 | <0.001*** |
  | pers_rfl | -0.0071 | 0.0159 | -0.448 | 0.6540 n.s. |
  | pers_rum | -0.0013 | 0.0161 | -0.081 | 0.9355 n.s. |
  | temp_z | -0.0087 | 0.0071 | -1.228 | 0.2194 n.s. |

## Descriptive: Condition means (N=6126)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 2032 | — | — | — | — |
| deprivation | 2032 | t=16.704, p<0.001 | 0.524 | t=60.963, p<0.001 | 1.913 |
| counterfactual | 2062 | t=9.012, p<0.001 | 0.28 | t=71.583, p<0.001 | 2.238 |

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
| o3-mini | 18 | 0.1554 | -0.0616 | 1.812 |
| o4-mini | 34 | 0.0700 | -0.0160 | 1.184 |
| gpt-oss-120b | 38 | 0.1128 | -0.0568 | 1.772 |
| gpt-oss-20b | 40 | 0.1167 | -0.0447 | 1.629 |
| gpt-oss-safeguard-20b | 54 | 0.1091 | -0.0575 | 1.627 |
| qwen3-32b | 72 | 0.1032 | 0.0160 | 1.420 |

All 28 models: D_bias > N_bias direction checked; supports H3 (cross-model replication).

## Interpretation Summary
- **H1a (lexical)**: Confirmed — regret-word rate (p=0.0000), negemo rate (p=0.0000), CF rate (p=0.0001, sig)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (z=34.314, p<0.001) and C (z=42.492, p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=18.487, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Supported — D>N directionally across all 28 models with embedding data

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.2151, z=42.492, p<0.001) comparably to deprivation (beta=0.1645, z=34.314, p<0.001). CF rate (deprivation): p=0.0001. This confirms counterfactual framing activates regret-associated semantic representations at the embedding layer.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=6126)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
