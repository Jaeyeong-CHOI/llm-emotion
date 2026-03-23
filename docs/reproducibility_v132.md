# Reproducibility v132

## 변경 요약
- 스크리닝 품질: `scripts/check_screening_quality.py`에 unknown-year query-group **top23 절대/글로벌 비율 가드** 추가
- 프롬프트 뱅크: `v132.0`으로 갱신하고 top23 countervoice mesh 시나리오 및 `temperature_p99_p55_guard_v132` 페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p55 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p55-share-ratio`) 추가
- 스크리닝 규칙: `queries/screening_rules.json`에 anticipated counterfactual affect / regret decision model / emotion-cognition interaction / llm-as-judge emotion alias와 registered replication report / measurement validity / causal mediation method cue 추가

## 재현 커맨드

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v132.json \
  --out-md results/screening_quality_report_v132.md \
  --run-label screening_qc_v132 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top23-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top23-over-global-group-top23-ratio 1.0

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v132_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top23_temperature_p99_p55_v132 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v131.json \
  --selection-csv results/selection_report_smoke_v131.csv \
  --preflight-markdown \
  --require-prompt-bank-version v132.0 \
  --max-planned-sample-temperature-p99-over-p55-share-ratio 1.2 \
  --manifest-note "preflight v132 unknown-year group top23 + temperature p99/p55 guard"
```

## 기대 산출물
- `results/screening_quality_report_v132.json`
- `results/screening_quality_report_v132.md`
- `results/selection_report_smoke_v131.json`
- `results/selection_report_smoke_v131.csv`
- `results/experiments/smoke_v132_plan/preflight.json`
- `results/experiments/smoke_v132_plan/preflight.md`
- `results/experiments/smoke_v132_plan/manifest.json`
