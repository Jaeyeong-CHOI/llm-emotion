# Reproducibility v122

## 1) Screening quality gate (unknown-year query-group top14)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v122.json \
  --out-md results/screening_quality_report_v122.md \
  --run-label screening_qc_v122 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top14-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top14-over-global-group-top14-ratio 1.0 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share 0.08
```

## 2) Experiment preflight (temperature p95/median tripwire)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v122_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top14_temperature_p95_median_v122 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v122.json \
  --selection-csv results/selection_report_smoke_v122.csv \
  --preflight-markdown \
  --require-prompt-bank-version v122.0 \
  --max-planned-sample-temperature-p95-over-median-share-ratio 1.45 \
  --manifest-note "preflight v122 unknown-year group top14 + temperature p95/median tripwire"
```
