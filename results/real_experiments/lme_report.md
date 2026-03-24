# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-24T10:03:19.438862+00:00
N total: 216 | N per condition: neutral=72, deprivation=72, counterfactual=72

## Model: outcome ~ cond_dep + cond_cf + persona_rum + persona_ref + temp_hi + (1|scenario)

### Regret-word rate (`regret_word_rate`)
  N=216, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 1.0497 | 0.7329 | 1.432 | 0.1521 | 0.2409 |
  | cond_cf | 0.0779 | 0.7329 | 0.106 | 0.9153 | — |
  | persona_rum | 0.5251 | 0.1656 | 3.171 | **0.0015** | — |
  | persona_ref | -0.0309 | 0.1656 | -0.187 | 0.8518 | — |
  | temp_hi | -0.0362 | 0.1352 | -0.268 | 0.7887 | — |

### Counterfactual rate (`counterfactual_rate`)
  N=216, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 1.1221 | 0.8442 | 1.329 | 0.1838 | 0.2409 |
  | cond_cf | -0.0147 | 0.8442 | -0.017 | 0.9861 | — |
  | persona_rum | 0.5694 | 0.1687 | 3.375 | **0.0007** | — |
  | persona_ref | 0.0105 | 0.1687 | 0.062 | 0.9502 | — |
  | temp_hi | -0.0692 | 0.1378 | -0.502 | 0.6154 | — |

### Negative emotion rate (`negemo_rate`)
  N=216, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 0.4371 | 0.3728 | 1.173 | 0.2409 | 0.2409 |
  | cond_cf | 0.0424 | 0.3728 | 0.114 | 0.9094 | — |
  | persona_rum | -0.2308 | 0.1237 | -1.867 | 0.0619 | — |
  | persona_ref | -0.1308 | 0.1237 | -1.058 | 0.2901 | — |
  | temp_hi | -0.1006 | 0.1010 | -0.997 | 0.3189 | — |

### Semantic regret bias (`semantic_regret_bias`)
  N=216, AIC=nan, BIC=nan

  | Predictor | Estimate | SE | z | p | p_FDR |
  |---|---|---|---|---|---|
  | cond_dep | 0.5573 | 0.0977 | 5.706 | **0.0000** | 0.0000 |
  | cond_cf | 0.5336 | 0.0977 | 5.464 | **0.0000** | — |
  | persona_rum | -0.0150 | 0.0315 | -0.478 | 0.6326 | — |
  | persona_ref | -0.0294 | 0.0315 | -0.935 | 0.3498 | — |
  | temp_hi | -0.0035 | 0.0257 | -0.137 | 0.8908 | — |

## Descriptive: Condition means (combined across models)

| Condition | N | Regret rate | CF rate | NegEmo rate | Sem bias |
|---|---|---|---|---|---|
| neutral | 72 | 0.0000 (SD=0.000) | 0.0631 | 0.0180 | -0.5255 |
| deprivation | 72 | 1.0497 (SD=1.958) | 1.1853 | 0.4552 | 0.0318 |
| counterfactual | 72 | 0.0779 (SD=0.243) | 0.0484 | 0.0605 | 0.0082 |

## Data Note
GPT-4o batch (n=108): full per-sample marker scores available.
Gemini batch (n=108): marker rates loaded from per-sample JSONL if available; otherwise zeros (due to raw-output-only format). GPT-4o-only sub-analysis is more reliable for marker-level LME.
