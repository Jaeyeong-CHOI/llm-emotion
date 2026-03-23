# Reproducibility v121

## 1) Screening quality gate (unknown-year query-group top12)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v121.json \
  --out-md results/screening_quality_report_v121.md \
  --run-label screening_qc_v121 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top11-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top11-over-global-group-top11-ratio 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top12-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top12-over-global-group-top12-ratio 1.0 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share 0.08
```

## 2) Experiment preflight (temperature top20 uniformity)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v121_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top11_temperature_top19_v120 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v121.json \
  --selection-csv results/selection_report_smoke_v121.csv \
  --preflight-markdown \
  --require-prompt-bank-version v12.1 \
  --max-planned-sample-temperature-top19-share 1.0 \
  --max-planned-sample-temperature-top19-over-uniform-ratio 1.0 \
  --max-planned-sample-temperature-top20-share 1.0 \
  --max-planned-sample-temperature-top20-over-uniform-ratio 1.0 \
  --manifest-note "preflight v121 unknown-year group top12 + temperature top20 uniformity guard"
```
