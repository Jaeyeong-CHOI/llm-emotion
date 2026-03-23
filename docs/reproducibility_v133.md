# Reproducibility v133

## 변경 요약
- 스크리닝 품질: `queries/screening_rules.json`에 emotional granularity calibration / regret repair strategy / counterfactual confidence interval / emotion-policy alignment alias 및 multiverse analysis / specification curve / open materials cue 추가
- 프롬프트 뱅크: `v133.0`으로 갱신하고 top24 countervoice mesh 시나리오 및 `temperature_p99_p50_guard_v133` 페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p50 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p50-share-ratio`) 추가

## 재현 커맨드

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v133_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top24_temperature_p99_p50_v133 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v133.json \
  --selection-csv results/selection_report_smoke_v133.csv \
  --preflight-markdown \
  --require-prompt-bank-version v133.0 \
  --max-planned-sample-temperature-p99-over-p50-share-ratio 1.25 \
  --manifest-note "preflight v133 unknown-year group top24 + temperature p99/p50 guard"
```

## 기대 산출물
- `results/selection_report_smoke_v133.json`
- `results/selection_report_smoke_v133.csv`
- `results/experiments/smoke_v133_plan/preflight.json`
- `results/experiments/smoke_v133_plan/preflight.md`
- `results/experiments/smoke_v133_plan/manifest.json`
