# Reproducibility v119

## 1) Screening quality gate (unknown-year query-group top10)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v119.json \
  --out-md results/screening_quality_report_v119.md \
  --run-label screening_qc_v119 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top10-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top10-over-global-group-top10-ratio 1.0 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share 0.08
```

## 2) Experiment preflight (temperature top18 uniformity)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v119_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top10_temperature_top18_v119 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v119.json \
  --selection-csv results/selection_report_smoke_v119.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.9 \
  --max-planned-sample-temperature-top18-share 1.0 \
  --max-planned-sample-temperature-top18-over-uniform-ratio 1.0 \
  --manifest-note "preflight v119 unknown-year group top10 + temperature top18 uniformity guard"
```
