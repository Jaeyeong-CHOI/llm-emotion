LME report written: 5836 samples, 38 batches, 28 models
# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-26 (authoritative run on full N=5836 dataset — 38 batches, 28 models)
N total: 5836 | N per condition: deprivation=1908, counterfactual=1967, neutral=1961

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### cf_rate (`cf_rate`) 
  N=5836, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.1626 | -- | 1.255 | 0.2095 n.s. |
  | cond_D | 0.4634 | -- | 3.96 | <0.001*** |
  | cond_C | 1.4538 | -- | 11.928 | <0.001*** |
  | pers_rfl | 0.0158 | -- | 0.413 | 0.6794 n.s. |
  | pers_rum | 0.3189 | -- | 8.209 | <0.001*** |
  | temp_z | -0.0412 | -- | -2.324 | 0.0201 * |

### regret_rate (`regret_rate`) 
  N=5836, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0393 | -- | -0.522 | 0.6014 n.s. |
  | cond_D | 0.4378 | -- | 5.29 | <0.001*** |
  | cond_C | 0.5005 | -- | 5.871 | <0.001*** |
  | pers_rfl | -0.0018 | -- | -0.06 | 0.9525 n.s. |
  | pers_rum | 0.2885 | -- | 9.268 | <0.001*** |
  | temp_z | -0.0147 | -- | -1.036 | 0.3000 n.s. |

### negemo_rate (`negemo_rate`) 
  N=5836, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0 | -- | -0.0 | 1.0000 n.s. |
  | cond_D | 0.1788 | -- | 10.253 | <0.001*** |
  | cond_C | 0.1186 | -- | 6.76 | <0.001*** |
  | pers_rfl | -0.0103 | -- | -0.608 | 0.5434 n.s. |
  | pers_rum | -0.0041 | -- | -0.237 | 0.8124 n.s. |
  | temp_z | -0.0077 | -- | -1.086 | 0.2777 n.s. |

### semantic_regret_bias (`semantic_regret_bias`) 
  N=5836, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.2848 | -- | -21.079 | <0.001*** |
  | cond_D | 0.3012 | -- | 20.896 | <0.001*** |
  | cond_C | 0.3038 | -- | 20.442 | <0.001*** |
  | pers_rfl | 0.0044 | -- | 0.847 | 0.3969 n.s. |
  | pers_rum | 0.0104 | -- | 1.98 | 0.0477 * |
  | temp_z | -0.0038 | -- | -1.57 | 0.1163 n.s. |

### embedding_regret_bias (`embedding_regret_bias`) — PRIMARY OUTCOME
  N=5836, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0541 | -- | -10.505 | <0.001*** |
  | cond_D | 0.1492 | -- | 26.98 | <0.001*** |
  | cond_C | 0.1995 | -- | 34.89 | <0.001*** |
  | pers_rfl | 0.0174 | -- | 8.706 | <0.001*** |
  | pers_rum | 0.0379 | -- | 18.717 | <0.001*** |
  | temp_z | -0.0019 | -- | -2.026 | 0.0428 * |
