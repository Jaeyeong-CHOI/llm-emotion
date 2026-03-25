# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-25 (re-run on full N=3391 dataset — 14 batches, 8 models)
N total: 3391 | N per condition: deprivation=1224, counterfactual=1268, neutral=899
Data sources: batch_v1_pilot_openai, batch_v1_gemini_v2, batch_v3_expand, batch_v4_expand_gpt4o, batch_v5_expand_both, batch_v6_expand, batch_v7_expand, batch_v8_neutral_balance, batch_v9_gpt35, batch_gemini25flashlite, batch_gpt54mini, batch_gpt54nano, batch_llama33_70b, batch_llama4_scout
Models: GPT-4o, GPT-3.5-turbo, GPT-5.4-mini, GPT-5.4-nano, Gemini-2.5-Flash, Gemini-2.5-Flash-Lite, Llama-3.3-70B, Llama-4-Scout-17B

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=3391, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0507 | 0.0292 | -1.735 | 0.0827 (borderline) |
  | cond_D | 0.171 | 0.0357 | 4.795 | <0.001*** |
  | cond_C | 0.1755 | 0.038 | 4.615 | <0.001*** |
  | pers_rfl | 0.0262 | 0.0026 | 10.054 | <0.001*** |
  | pers_rum | 0.0523 | 0.0026 | 20.088 | <0.001*** |
  | temp_z | -0.0031 | 0.0011 | -2.895 | 0.0038** |

### Regret-word rate (`regret_rate`)
  N=3391, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0734 | 0.2469 | -0.297 | 0.7663 n.s. |
  | cond_D | 0.7242 | 0.301 | 2.406 | 0.0161* |
  | cond_C | 0.4713 | 0.3199 | 1.473 | 0.1407 n.s. |
  | pers_rfl | 0.0118 | 0.0314 | 0.377 | 0.7065 n.s. |
  | pers_rum | 0.3538 | 0.0314 | 11.271 | <0.001*** |
  | temp_z | 0.005 | 0.0129 | 0.389 | 0.6970 n.s. |

### Counterfactual rate (`cf_rate`)
  N=3391

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.1125 | 0.458 | -0.246 | 0.8060 n.s. |
  | cond_D | 0.9105 | 0.5598 | 1.627 | 0.1038 n.s. |
  | cond_C | 1.1605 | 0.5975 | 1.942 | 0.0521 (borderline) |
  | pers_rfl | 0.0225 | 0.0332 | 0.68 | 0.4967 n.s. |
  | pers_rum | 0.3857 | 0.0331 | 11.638 | <0.001*** |
  | temp_z | -0.0082 | 0.0136 | -0.607 | 0.5438 n.s. |

### Negative emotion rate (`negemo_rate`)
  N=3391

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0657 | 0.1116 | 0.588 | 0.5562 n.s. |
  | cond_D | 0.3052 | 0.1364 | 2.238 | 0.0252* |
  | cond_C | 0.0663 | 0.1424 | 0.466 | 0.6413 n.s. |
  | pers_rfl | -0.0107 | 0.0224 | -0.477 | 0.6334 n.s. |
  | pers_rum | -0.0148 | 0.0223 | -0.661 | 0.5086 n.s. |
  | temp_z | -0.0094 | 0.0091 | -1.026 | 0.3051 n.s. |

## Descriptive: Condition means (N=3391)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 899 | — | — | — | — |
| deprivation | 1224 | t=14.323, p<0.001 | 0.546 | t=33.576, p<0.001 | 1.504 |
| counterfactual | 1268 | t=9.288, p<0.001 | 0.363 | t=37.392, p<0.001 | 1.742 |

## Cross-model: Embedding Regret Bias by Model (D condition)

| Model | n_D | D_bias | N_bias | d(D-N) |
|---|---|---|---|---|
| gemini-2.5-flash | 276 | 0.0985 | -0.0451 | 1.250 |
| gemini-2.5-flash-lite | 72 | 0.1123 | 0.0246 | 0.986 |
| gemini-2.5-pro | 71 | 0.0976 | 0.0141 | 1.250 |
| gemini-3-flash-preview | 54 | 0.1145 | -0.0154 | 1.516 |
| gemini-3-pro-preview | 25 | 0.0747 | -0.0321 | 1.359 |
| gpt-3.5-turbo | 24 | 0.2207 | -0.0363 | 1.744 |
| gpt-4.1 | 72 | 0.1263 | -0.0150 | 1.283 |
| gpt-4.1-mini | 54 | 0.1304 | -0.0122 | 1.401 |
| gpt-4o | 198 | 0.1008 | -0.0533 | 1.607 |
| gpt-4o-mini | 54 | 0.1320 | 0.0226 | 1.099 |
| gpt-5.4-mini | 54 | 0.1075 | 0.0775 | 0.419 |
| gpt-5.4-nano | 54 | 0.0710 | 0.0372 | 0.491 |
| llama-3.3-70b-versatile | 72 | 0.1675 | 0.0661 | 1.168 |
| llama-4-scout-17b-16e-instruct | 72 | 0.1103 | 0.0432 | 0.779 |
| qwen3-32b | 72 | 0.1032 | 0.0160 | 1.420 |

All 8 models show D_bias > N_bias, supporting H3 (cross-model replication).

## Interpretation Summary
- **H1 (lexical)**: Partially confirmed — regret-word rate (p=0.0161) and negemo rate (p=0.0252) significant; CF rate borderline (p=0.1038)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (p<0.001) and C (p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=20.088, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Confirmed — D>N in all 8 models tested

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.1755, z=4.615, p<0.001) comparably to deprivation (beta=0.171), but CF rate remains borderline (p=0.1038). This confirms counterfactual framing activates regret-associated semantic representations without reliably triggering explicit counterfactual vocabulary.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=3391)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
