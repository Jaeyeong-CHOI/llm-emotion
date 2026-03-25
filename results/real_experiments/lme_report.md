# LME Confirmatory Analysis — Real Experiment Results
Generated: 2026-03-25 (re-run on full N=3717 dataset — 30 batches, 16 models)
N total: 3717 | N per condition: deprivation=1260, counterfactual=1306, neutral=1151
Data sources: batch_gemini20flash, batch_gemini25flashlite, batch_gemini25pro, batch_gemini31pro, batch_gemini3flash, batch_gemini3pro, batch_gpt41, batch_gpt41mini, batch_gpt4omini, batch_gpt54, batch_gpt54mini, batch_gpt54nano, batch_gpt54pro, batch_llama33_70b, batch_llama4_scout, batch_qwen3_32b, batch_v10_neutral_expand, batch_v11_neutral_balance2, batch_v12_gemini3pro_cf, batch_v13_openai_balance, batch_v1_gemini, batch_v1_gemini_v2, batch_v1_pilot_openai, batch_v3_expand, batch_v4_expand_gpt4o, batch_v5_expand_both, batch_v6_expand, batch_v7_expand, batch_v8_neutral_balance, batch_v9_gpt35
Models: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-pro-preview, gpt-3.5-turbo, gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-5.4-mini, gpt-5.4-nano, llama-3.3-70b-versatile, meta-llama/llama-4-scout-17b-16e-instruct, qwen/qwen3-32b

## Model: outcome ~ cond_D + cond_C + pers_rum + pers_rfl + temp_z + (1|scenario)

### Embedding regret bias (embedding_regret_bias) — PRIMARY OUTCOME
  N=3717, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0627 | 0.0211 | -2.977 | 0.0029** |
  | cond_D | 0.1844 | 0.029 | 6.354 | <0.001*** |
  | cond_C | 0.1999 | 0.0306 | 6.528 | <0.001*** |
  | pers_rfl | 0.0243 | 0.0025 | 9.776 | <0.001*** |
  | pers_rum | 0.0514 | 0.0025 | 20.707 | <0.001*** |
  | temp_z | -0.0022 | 0.001 | -2.18 | 0.0293* |

  Welch t-test (D vs N): t=40.587, d=1.661, p<0.001
  Welch t-test (C vs N): t=45.854, d=1.893, p<0.001

### Regret-word rate (regret_rate)
  N=3717, condition ref=neutral

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.0897 | 0.1608 | -0.558 | 0.5769 n.s. |
  | cond_D | 0.7379 | 0.2215 | 3.331 | <0.001*** |
  | cond_C | 0.5136 | 0.2328 | 2.207 | 0.0273* |
  | pers_rfl | 0.0126 | 0.029 | 0.434 | 0.6644 n.s. |
  | pers_rum | 0.333 | 0.029 | 11.499 | <0.001*** |
  | temp_z | 0.0037 | 0.0119 | 0.311 | 0.7560 n.s. |

  Welch t-test (D vs N): t=14.902, d=0.583, p<0.001
  Welch t-test (C vs N): t=10.372, d=0.403, p<0.001

### Counterfactual rate (cf_rate)
  N=3717

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | -0.1187 | 0.3032 | -0.392 | 0.6954 n.s. |
  | cond_D | 0.9188 | 0.4176 | 2.2 | 0.0278* |
  | cond_C | 1.2486 | 0.4411 | 2.831 | 0.0046** |
  | pers_rfl | 0.0256 | 0.0307 | 0.832 | 0.4052 n.s. |
  | pers_rum | 0.3642 | 0.0307 | 11.861 | <0.001*** |
  | temp_z | -0.0057 | 0.0126 | -0.449 | 0.6532 n.s. |

  Welch t-test (D vs N): t=16.674, d=0.652, p<0.001
  Welch t-test (C vs N): t=11.165, d=0.431, p<0.001

### Negative emotion rate (negemo_rate)
  N=3717

  | Predictor | Estimate | SE | z | p |
  |---|---|---|---|---|
  | Intercept | 0.0593 | 0.078 | 0.761 | 0.4469 n.s. |
  | cond_D | 0.3081 | 0.1076 | 2.863 | 0.0042** |
  | cond_C | 0.1069 | 0.1112 | 0.961 | 0.3366 n.s. |
  | pers_rfl | -0.0113 | 0.0206 | -0.547 | 0.5842 n.s. |
  | pers_rum | -0.0077 | 0.0205 | -0.373 | 0.7095 n.s. |
  | temp_z | -0.008 | 0.0084 | -0.953 | 0.3406 n.s. |

  Welch t-test (D vs N): t=10.9, d=0.427, p<0.001
  Welch t-test (C vs N): t=5.137, d=0.202, p<0.001

## Cross-model embedding bias summary

| Model | N_D | N_N | N_C | M_D | M_N | M_C | d_DN |
|---|---|---|---|---|---|---|---|
| gemini-2.5-flash | 276 | 252 | 276 | 0.0985 | -0.0483 | 0.0773 | 1.272 |
| gemini-2.5-flash-lite | 72 | 48 | 72 | 0.1123 | 0.0246 | 0.1206 | 0.986 |
| gemini-2.5-pro | 71 | 48 | 66 | 0.0976 | 0.0141 | 0.1087 | 1.250 |
| gemini-3-flash-preview | 54 | 36 | 54 | 0.1145 | -0.0154 | 0.1288 | 1.516 |
| gemini-3-pro-preview | 25 | 36 | 2 | 0.0747 | -0.0321 | 0.1422 | 1.359 |
| gemini-3.1-pro-preview | 2 | 4 | 1 | 0.1466 | -0.0226 | 0.1797 | 2.050 |
| gpt-3.5-turbo | 24 | 18 | 18 | 0.2207 | -0.0363 | 0.2214 | 1.744 |
| gpt-4.1 | 72 | 84 | 72 | 0.1263 | -0.0243 | 0.1399 | 1.333 |
| gpt-4.1-mini | 72 | 36 | 109 | 0.1430 | -0.0122 | 0.1400 | 1.481 |
| gpt-4o | 198 | 341 | 227 | 0.1008 | -0.0525 | 0.1108 | 1.662 |
| gpt-4o-mini | 72 | 36 | 113 | 0.1450 | 0.0226 | 0.1499 | 1.221 |
| gpt-5.4-mini | 54 | 36 | 54 | 0.1075 | 0.0775 | 0.0824 | 0.419 |
| gpt-5.4-nano | 54 | 36 | 54 | 0.0710 | 0.0372 | 0.1067 | 0.491 |
| llama-3.3-70b-versatile | 72 | 48 | 45 | 0.1675 | 0.0661 | 0.1516 | 1.168 |
| llama-4-scout-17b-16e-instruct | 72 | 48 | 72 | 0.1103 | 0.0432 | 0.1430 | 0.779 |
| qwen3-32b | 72 | 48 | 72 | 0.1032 | 0.0160 | 0.1006 | 1.420 |

## Key results summary
- PRIMARY: Embedding regret bias cond_D: beta=0.1844, z=6.354, p<0.001***
- PRIMARY: Embedding regret bias cond_C: beta=0.1999, z=6.528, p<0.001***
- Ruminative persona (strongest predictor): z=20.707, p<0.001
- CF rate cond_D: z=2.2, p=0.0278*
- CF rate cond_C: z=2.831, p=0.0046**
- Regret-word rate cond_D: z=3.331, p=<0.001***
- Regret-word rate cond_C: z=2.207, p=0.0273*
- negemo rate cond_D: z=2.863, p=0.0042**
