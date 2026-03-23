# Reproducibility v134

## 변경 요약
- 스크리닝 품질: `scripts/check_screening_quality.py`에 unknown-year query-group **top24 절대/글로벌 비율 backstop**(`--max-manual-qc-review-traceable-known-query-unknown-year-group-top24-share`, `--max-manual-qc-review-traceable-known-query-unknown-year-group-top24-over-global-group-top24-ratio`) 추가
- 프롬프트 뱅크: `v134.0`으로 갱신하고 top24 backstop / methodology countervoice / p99-p45 tripwire 시나리오와 대응 페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p45 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p45-share-ratio`) 추가

## 검증 커맨드

```bash
python3 -m py_compile scripts/check_screening_quality.py scripts/run_experiments.py

python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v134.json \
  --out-md results/screening_quality_report_v134.md \
  --run-label screening_qc_v134 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-share 0.995 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-over-global-group-top24-ratio 1.0

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v134_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top24_backstop_temperature_p99_p45_v134 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v134.json \
  --selection-csv results/selection_report_smoke_v134.csv \
  --preflight-markdown \
  --require-prompt-bank-version v134.0 \
  --max-planned-sample-temperature-p99-over-p45-share-ratio 1.25 \
  --manifest-note "preflight v134 unknown-year group top24 backstop + temperature p99/p45 guard"
```

## 기대 산출물
- `results/screening_quality_report_v134.json`
- `results/screening_quality_report_v134.md`
- `results/selection_report_smoke_v134.json`
- `results/selection_report_smoke_v134.csv`
- `results/experiments/smoke_v134_plan/preflight.json`
- `results/experiments/smoke_v134_plan/preflight.md`
- `results/experiments/smoke_v134_plan/manifest.json`
