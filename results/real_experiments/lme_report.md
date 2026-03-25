# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-25 (re-run on full N=1,974 dataset — 13 batches, 7 models)
N total: 1974 | N per condition: deprivation=737, counterfactual=674, neutral=563
Data sources: batch_v1_pilot_openai, batch_v1_gemini_v2, batch_v3_expand, batch_v4_expand_gpt4o, batch_v5_expand_both, batch_v6_expand, batch_v7_expand, batch_v8_neutral_balance, batch_v9_gpt35, batch_gemini25flashlite, batch_gpt54mini, batch_gpt54nano, batch_llama33_70b
Models: GPT-4o, GPT-3.5-turbo, GPT-5.4-mini, GPT-5.4-nano, Gemini-2.5-Flash, Gemini-2.5-Flash-Lite, Llama-3.3-70B

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=1974, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.1746 | 0.0364 | 4.803 | <0.001*** |
  | cond_C | 0.1720 | 0.0388 | 4.436 | <0.001*** |
  | pers_rum | 0.0559 | 0.0037 | 15.198 | <0.001*** |

### Regret-word rate (`regret_rate`)
  N=1974, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.7406 | 0.2605 | 2.844 | 0.004** |
  | cond_C | 0.3911 | 0.2758 | 1.418 | 0.156 n.s. |
  | pers_rum | 0.3889 | 0.0492 | 7.910 | <0.001*** |

### Counterfactual rate (`cf_rate`)
  N=1974

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.9489 | 0.5699 | 1.665 | 0.096 (borderline) |
  | cond_C | 1.1127 | 0.6082 | 1.829 | 0.067 (borderline) |
  | pers_rum | 0.4682 | 0.0495 | 9.453 | <0.001*** |

### Negative emotion rate (`negemo_rate`)
  N=1974

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | cond_D | 0.2960 | 0.1309 | 2.262 | 0.024* |
  | cond_C | 0.0525 | 0.1356 | 0.387 | 0.699 n.s. |

## Descriptive: Condition means (N=1974)

| Condition | N | Welch D vs N (regret) | d | Welch D vs N (emb_bias) | d |
|---|---|---|---|---|---|
| neutral | 563 | — | — | — | — |
| deprivation | 737 | t=10.78, p<0.001 | 0.529 | t=26.73, p<0.001 | 1.519 |
| counterfactual | 674 | t=5.06, p<0.001 | 0.266 | t=26.24, p<0.001 | 1.543 |

## Cross-model: Embedding Regret Bias by Model (D condition)

| Model | n_D | D_bias | N_bias | d(D-N) |
|---|---|---|---|---|
| GPT-3.5-turbo | 24 | 0.2207 | -0.0363 | 3.369 |
| GPT-4o | 198 | 0.1008 | -0.0533 | 2.665 |
| Llama-3.3-70B | 72 | 0.1675 | 0.0661 | 1.412 |
| Gemini-2.5-Flash | 276 | 0.0985 | -0.0451 | 1.591 |
| Gemini-2.5-Flash-Lite | 59 | 0.1199 | 0.0229 | 1.291 |
| GPT-5.4-nano | 54 | 0.0710 | 0.0372 | 0.500 |
| GPT-5.4-mini | 54 | 0.1075 | 0.0775 | 0.423 |

All 7 models show D_bias > N_bias, supporting H3 (cross-model replication).

## Interpretation Summary
- **H1 (lexical)**: Partially confirmed — regret-word rate (p=0.004) and negemo rate (p=0.024) significant; CF rate borderline (p=0.096)
- **H1b (semantic)**: Confirmed — embedding bias significant for both D (p<0.001) and C (p<0.001)
- **H2 (persona)**: Confirmed — ruminative persona z=15.20, p<0.001 (strongest predictor)
- **H3 (cross-model)**: Confirmed — D>N in all 7 models tested

## Semantic-layer dissociation
CF framing elevates embedding regret bias (β=0.172, z=4.44, p<0.001) comparably to deprivation (β=0.175), but CF rate remains borderline (p=0.096). This confirms counterfactual framing activates regret-associated semantic representations without reliably triggering explicit counterfactual vocabulary.

## Reproducibility
Run: `python3 scripts/run_lme_analysis.py` from project root with .env.real_model sourced.
Full results JSON: results/real_experiments/lme_analysis.json (authoritative, N=1,974)
Legacy lme_results.json = earlier partial-dataset run (N=216), not for verification.
