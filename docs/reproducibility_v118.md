# Reproducibility v11.8 (2026-03-23)

## 변경 요약
- screening quality: unknown-year query-group **top9 share/ratio** gate 추가
- prompt bank: `prompts/prompt_bank_ko.json` 버전 `v11.8` (scenario 3 + persona 3 추가)
- runner preflight: planned-sample temperature **top17 share / top17-over-uniform ratio** guard 추가
- matrix run: `screening_prompt_runner_unknown_year_group_top9_temperature_top17_v118`

## 1) Screening quality gate 스모크
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v118 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top8-share 0.98 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top8-over-global-group-top8-ratio 1.02 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top9-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top9-over-global-group-top9-ratio 1.00
```

## 2) Runner preflight(plan-only) 스모크
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v118_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top9_temperature_top17_v118 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v118.json \
  --selection-csv results/selection_report_smoke_v118.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.8 \
  --max-planned-sample-temperature-top16-share 1.00 \
  --max-planned-sample-temperature-top17-share 1.00 \
  --max-planned-sample-temperature-top16-over-uniform-ratio 1.00 \
  --max-planned-sample-temperature-top17-over-uniform-ratio 1.00 \
  --manifest-note "preflight v118 unknown-year group top9 + temperature top17 guard"
```

## 3) 정적 검증
```bash
python3 -m py_compile scripts/check_screening_quality.py scripts/run_experiments.py
```
