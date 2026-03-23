# Reproducibility v11.7 (2026-03-23)

## 변경 요약
- Screening quality gate 확장:
  - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top8-share`
  - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top8-over-global-group-top8-ratio`
- Prompt bank `v11.7` 확장:
  - `screening_unknown_year_group_top8_ratio_guard_v117`
  - `prompt_bank_unknown_year_group_top8_counterbalance_patch_v117`
  - `runner_temperature_top16_uniformity_tripwire_v117`
  - persona: `unknown_year_group_top8_ratio_triager_v117`, `temperature_top16_uniformity_guard_v117`
- Experiment runner preflight 확장:
  - `--max-planned-sample-temperature-top16-share`
  - `--max-planned-sample-temperature-top16-over-uniform-ratio`

## 재현 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v117.json \
  --out-md results/screening_quality_report_v117.md \
  --run-label screening_qc_v117 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top8-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top8-over-global-group-top8-ratio 1.01

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v117_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top8_temperature_top16_v117 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v117.json \
  --selection-csv results/selection_report_smoke_v117.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.7 \
  --max-planned-sample-temperature-top16-share 1.01 \
  --max-planned-sample-temperature-top16-over-uniform-ratio 1.01 \
  --manifest-note "preflight v117 unknown-year group top8 + temperature top16 uniformity guard"
```

## 산출물
- `results/screening_quality_report_v117.json`
- `results/screening_quality_report_v117.md`
- `results/selection_report_smoke_v117.json`
- `results/selection_report_smoke_v117.csv`
- `results/experiments/smoke_v117_plan/manifest.json`
