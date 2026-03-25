# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-25 (re-run on full N=2251 dataset — 14 batches, 8 models)
N total: 2251 | N per condition: deprivation=822, counterfactual=818, neutral=611
Data sources: batch_v1_pilot_openai, batch_v1_gemini_v2, batch_v3_expand, batch_v4_expand_gpt4o, batch_v5_expand_both, batch_v6_expand, batch_v7_expand, batch_v8_neutral_balance, batch_v9_gpt35, batch_gemini25flashlite, batch_gpt54mini, batch_gpt54nano, batch_llama33_70b, batch_llama4_scout
Models: GPT-4o, GPT-3.5-turbo, GPT-5.4-mini, GPT-5.4-nano, Gemini-2.5-Flash, Gemini-2.5-Flash-Lite, Llama-3.3-70B, Llama-4-Scout-17B

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=2251, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0537 | 0.0296 | -1.811 | 0.0701 (borderline) |
  | cond_D | 0.1721 | 0.0362 | 4.757 | <0.001*** |
  | cond_C | 0.1726 | 0.0386 | 4.475 | <0.001*** |
  | pers_rfl | 0.0266 | 0.0034 | 7.777 | <0.001*** |
  | pers_rum | 0.0564 | 0.0034 | 16.527 | <0.001*** |
  | temp_z | -0.0038 | 0.0014 | -2.693 | 0.0071** |

### Regret-word rate (`regret_rate`)
  N=2251, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0901 | 0.2512 | -0.359 | 0.7198 n.s. |
  | cond_D | 0.7357 | 0.3054 | 2.409 | 0.0160* |
  | cond_C | 0.4243 | 0.3244 | 1.308 | 0.1908 n.s. |
  | pers_rfl | 0.0062 | 0.0443 | 0.14 | 0.8884 n.s. |
  | pers_rum | 0.4096 | 0.0442 | 9.26 | <0.001*** |
  | temp_z | 0.0008 | 0.0182 | 0.046 | 0.9630 n.s. |

### Counterfactual rate (`cf_rate`)
  N=2251

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.1433 | 0.4643 | -0.309 | 0.7576 n.s. |
  | cond_D | 0.9379 | 0.5669 | 1.654 | 0.0981 (borderline) |
  | cond_C | 1.1173 | 0.6051 | 1.847 | 0.0648 (borderline) |
  | pers_rfl | 0.0243 | 0.0452 | 0.536 | 0.5917 n.s. |
  | pers_rum | 0.4849 | 0.0452 | 10.738 | <0.001*** |
  | temp_z | -0.0104 | 0.0185 | -0.56 | 0.5754 n.s. |

### Negative emotion rate (`negemo_rate`)
  N=2251

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0765 | 0.1072 | 0.713 | 0.4756 n.s. |
  | cond_D | 0.2952 | 0.1303 | 2.266 | 0.0235* |
  | cond_C | 0.0562 | 0.1351 | 0.416 | 0.6772 n.s. |
  | pers_rfl | -0.0383 | 0.0313 | -1.221 | 0.2221 n.s. |
  | pers_rum | -0.0504 | 0.0313 | -1.613 | 0.1068 n.s. |
  | temp_z | -0.0073 | 0.0128 | -0.565 | 0.5718 n.s. |

## Descriptive: Condition means (N=2251)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 611 | — | — | — | — |
| deprivation | 822 | t=10.784, p<0.001 | 0.502 | t=26.408, p<0.001 | 1.447 |
| counterfactual | 818 | t=4.896, p<0.001 | 0.239 | t=27.345, p<0.001 | 1.546 |

## Cross-model: Embedding Regret Bias by Model (D condition)

| Model | n_D | D_bias | N_bias | d(D-N) |
|---|---|---|---|---|
| gemini-2.5-flash | 276 | 0.0985 | -0.0451 | 1.250 |
| gemini-2.5-flash-lite | 72 | 0.1123 | 0.0246 | 0.986 |
| gpt-3.5-turbo | 24 | 0.2207 | -0.0363 | 1.744 |
| gpt-4.1-mini | 54 | 0.1304 | -0.0122 | 1.401 |
| gpt-4o | 198 | 0.1008 | -0.0533 | 1.607 |
| gpt-4o-mini | 54 | 0.1320 | 0.0226 | 1.099 |
| gpt-5.4-mini | 54 | 0.1075 | 0.0775 | 0.419 |
| gpt-5.4-nano | 54 | 0.0710 | 0.0372 | 0.491 |
| llama-3.3-70b-versatile | 72 | 0.1675 | 0.0661 | 1.168 |
| llama-4-scout-17b-16e-instruct | 72 | 0.1103 | 0.0432 | 0.779 |

All 8 models show D_bias > N_bias, supporting H3 (cross-model replication).

## Interpretation Summary
- **H1 (lexical)**: Partially confirmed — regret-word rate (p=0.0160) and negemo rate (p=0.0235) significant; CF rate borderline (p=0.0981)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (p<0.001) and C (p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=16.527, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Confirmed — D>N in all 8 models tested

## Semantic-layer dissociation
CF framing elevates embedding regret bias (beta=0.1726, z=4.475, p<0.001) comparably to deprivation (beta=0.1721), but CF rate remains borderline (p=0.0981). This confirms counterfactual framing activates regret-associated semantic representations without reliably triggering explicit counterfactual vocabulary.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=2251)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
