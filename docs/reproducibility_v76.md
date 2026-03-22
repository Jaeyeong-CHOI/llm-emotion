# Reproducibility Note v76

## Summary
- prompt bank version: `v7.6`
- focus: screening duplicate/weak-evidence QC + metadata-aware prompt/runner selection
- new run id: `screening_prompt_runner_metadata_balance_v76`

## Commands
```bash
python3 -m py_compile scripts/generate_dataset.py scripts/run_experiments.py scripts/check_screening_quality.py
python3 scripts/generate_dataset.py --out /tmp/llm_emotion_v76_metadata.jsonl --prompt-bank prompts/prompt_bank_ko.json --scenario-domains research_ops --scenario-emotion-axes regret --scenario-difficulties hard --persona-ids duplicate_provenance_auditor,domain_axis_balance_curator --temperatures 0.2,0.8 --n 2
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v76 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-review-counterexample-traceability-share 0.55 --min-review-bridge-counterexample-coupled-share 0.18 --min-review-bridge-counterexample-traceable-share 0.12 --min-review-bridge-counterexample-traceability-given-coupled-share 0.55 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-review-query-entropy 0.45 --min-manual-qc-review-traceable-known-query-share 0.55 --max-manual-qc-review-traceable-unknown-query-share 0.15 --min-manual-qc-review-query-traceability-share 0.75 --min-manual-qc-review-traceable-known-query-entropy 0.45 --max-manual-qc-review-traceable-known-query-top-share 0.70 --min-manual-qc-review-traceable-known-query-group-entropy 0.45 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-manual-qc-dedup-label-conflict-share 0.20 --min-dedup-score-range-alert 1.0 --max-manual-qc-dedup-score-range-alert-share 0.20 --max-manual-qc-duplicate-title-share 0.20 --max-review-weak-evidence-share 0.40 --max-empty-screening-reason-share 0.10 --max-review-counterexample-without-bridge-share 0.35
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v76_plan --plan-only --include-run-id screening_prompt_runner_metadata_balance_v76 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v76.json --selection-csv results/selection_report_smoke_v76.csv --preflight-markdown --require-min-scenarios 3 --require-min-personas 4 --require-min-temperature-count 3 --require-min-condition-cells 27 --require-min-total-samples 800 --require-min-planned-samples-per-run 800 --require-min-unique-scenario-labels 3 --require-min-unique-scenario-tags 10 --require-min-unique-scenario-domains 4 --require-min-unique-scenario-emotion-axes 6 --require-min-unique-scenario-difficulties 1 --require-min-unique-persona-style-tags 12 --require-prompt-bank-version v7.6 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v76 metadata balance"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v76_exec --include-run-id screening_prompt_runner_metadata_balance_v76 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --require-min-total-samples 400 --execution-log-jsonl results/experiments/smoke_v76_exec/command_log.jsonl --budget-report-json results/experiments/smoke_v76_exec/budget_report.json --budget-report-md results/experiments/smoke_v76_exec/budget_report.md
```

## Observed Results
- `py_compile`: passed
- metadata dataset smoke: `24` rows written to `/tmp/llm_emotion_v76_metadata.jsonl`
- screening QC: `status=review`, `quality_score=0.0`, `fail_count=8`
- preflight: `selected_run_cells=1`, `selected_total_samples=864`
- execution smoke: `successful_cells=1`, `success_rate=1.0`

## Artifacts
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v76.json`
- `results/selection_report_smoke_v76.csv`
- `results/experiments/smoke_v76_plan/preflight.json`
- `results/experiments/smoke_v76_plan/preflight.md`
- `results/experiments/smoke_v76_exec/manifest.json`
- `results/experiments/smoke_v76_exec/manifest.md`
- `results/experiments/smoke_v76_exec/budget_report.json`
- `results/experiments/smoke_v76_exec/budget_report.md`
