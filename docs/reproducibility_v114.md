# Reproducibility v11.4 (2026-03-23)

## 변경 요약
- Screening quality gate 확장:
  - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top5-share`
  - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top5-over-global-group-top5-ratio`
- Prompt bank `v11.4` 확장:
  - `screening_unknown_year_group_top5_ratio_guard_v114`
  - `prompt_bank_unknown_year_group_top5_counterbalance_v114`
  - `runner_temperature_top13_uniformity_tripwire_v114`
  - persona: `temperature_top13_uniformity_guard_v114`
- Experiment runner preflight 확장:
  - `--max-planned-sample-temperature-top13-share`
  - `--max-planned-sample-temperature-top13-over-uniform-ratio`

## 재현 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v114.json \
  --out-md results/screening_quality_report_v114.md \
  --run-label screening_qc_v114 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top5-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top5-over-global-group-top5-ratio 1.03

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v114_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top5_temperature_top13_v114 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v114.json \
  --selection-csv results/selection_report_smoke_v114.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.4 \
  --max-planned-sample-temperature-top13-share 1.0 \
  --max-planned-sample-temperature-top13-over-uniform-ratio 1.0 \
  --manifest-note "preflight v114 unknown-year group top5 + temperature top13 uniformity guard"
```

## 산출물
- `results/screening_quality_report_v114.json`
- `results/screening_quality_report_v114.md`
- `results/selection_report_smoke_v114.json`
- `results/selection_report_smoke_v114.csv`
- `results/experiments/smoke_v114_plan/manifest.json`
