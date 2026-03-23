# Reproducibility v11.6 (2026-03-23)

## 변경 요약
- Screening quality gate 확장:
  - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top7-share`
  - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top7-over-global-group-top7-ratio`
- Prompt bank `v11.6` 확장:
  - `screening_unknown_year_group_top7_ratio_guard_v116`
  - `prompt_bank_unknown_year_group_top7_counterbalance_patch_v116`
  - `runner_temperature_top15_uniformity_tripwire_v116`
  - persona: `unknown_year_group_top7_ratio_triager_v116`, `temperature_top15_uniformity_guard_v116`
- Experiment runner preflight 확장:
  - `--max-planned-sample-temperature-top15-share`
  - `--max-planned-sample-temperature-top15-over-uniform-ratio`

## 재현 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v116.json \
  --out-md results/screening_quality_report_v116.md \
  --run-label screening_qc_v116 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top7-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top7-over-global-group-top7-ratio 1.01

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v116_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top7_temperature_top15_v116 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v116.json \
  --selection-csv results/selection_report_smoke_v116.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.6 \
  --max-planned-sample-temperature-top15-share 1.01 \
  --max-planned-sample-temperature-top15-over-uniform-ratio 1.01 \
  --manifest-note "preflight v116 unknown-year group top7 + temperature top15 uniformity guard"
```

## 산출물
- `results/screening_quality_report_v116.json`
- `results/screening_quality_report_v116.md`
- `results/selection_report_smoke_v116.json`
- `results/selection_report_smoke_v116.csv`
- `results/experiments/smoke_v116_plan/manifest.json`
