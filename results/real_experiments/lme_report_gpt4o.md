# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-24T10:03:40.982903+00:00
N total: 108 | N per condition: neutral=36, deprivation=36, counterfactual=36

## Model: outcome ~ cond_dep + cond_cf + persona_rum + persona_ref + temp_hi + (1|scenario)

### Regret-word rate (`regret_word_rate`)
  N=108, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 0.6048 | 0.5045 | 1.199 | 0.2306 | 0.3041 |
  | cond_cf | 0.1558 | 0.5045 | 0.309 | 0.7574 | — |
  | persona_rum | 0.0881 | 0.0544 | 1.619 | 0.1055 | — |
  | persona_ref | -0.0734 | 0.0544 | -1.350 | 0.1769 | — |
  | temp_hi | 0.0098 | 0.0444 | 0.221 | 0.8249 | — |

### Counterfactual rate (`counterfactual_rate`)
  N=108, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 0.8759 | 0.7194 | 1.217 | 0.2234 | 0.3041 |
  | cond_cf | 0.0968 | 0.7194 | 0.135 | 0.8930 | — |
  | persona_rum | 0.0502 | 0.0598 | 0.840 | 0.4010 | — |
  | persona_ref | 0.0095 | 0.0598 | 0.159 | 0.8739 | — |
  | temp_hi | -0.1403 | 0.0488 | -2.873 | **0.0041** | — |

### Negative emotion rate (`negemo_rate`)
  N=108, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 0.2368 | 0.2304 | 1.028 | 0.3041 | 0.3041 |
  | cond_cf | 0.0848 | 0.2304 | 0.368 | 0.7127 | — |
  | persona_rum | 0.0215 | 0.0677 | 0.318 | 0.7507 | — |
  | persona_ref | 0.0672 | 0.0677 | 0.993 | 0.3208 | — |
  | temp_hi | 0.0288 | 0.0553 | 0.521 | 0.6022 | — |

### Semantic regret bias (`semantic_regret_bias`)
  N=108, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 0.8102 | 0.1641 | 4.937 | **0.0000** | 0.0000 |
  | cond_cf | 0.7975 | 0.1641 | 4.859 | **0.0000** | — |
  | persona_rum | -0.0278 | 0.0291 | -0.955 | 0.3394 | — |
  | persona_ref | -0.0278 | 0.0291 | -0.955 | 0.3394 | — |
  | temp_hi | 0.0147 | 0.0237 | 0.618 | 0.5369 | — |

## Descriptive: Condition means (combined across models)

| Condition | N | Regret rate | CF rate | NegEmo rate | Sem bias |
|---|---|---|---|---|---|
| neutral | 36 | 0.0000 (SD=0.000) | 0.0000 | 0.0361 | -0.7778 |
| deprivation | 36 | 0.6048 (SD=0.670) | 0.8759 | 0.2728 | 0.0324 |
| counterfactual | 36 | 0.1558 (SD=0.328) | 0.0968 | 0.1209 | 0.0197 |

## Data Note
GPT-4o batch (n=108): full per-sample marker scores available.
Gemini batch (n=108): marker rates loaded from per-sample JSONL if available; otherwise zeros (due to raw-output-only format). GPT-4o-only sub-analysis is more reliable for marker-level LME.
