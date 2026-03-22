# Reproducibility Note v77

## Summary
- prompt bank version: `v7.7`
- focus: screening long-tail query 쏠림 억제 + countervoice 도메인/강도 균형 + runner metadata entropy guard
- new run id: `screening_prompt_runner_metadata_entropy_v77`

## Commands
```bash
python3 -m py_compile scripts/generate_dataset.py scripts/run_experiments.py scripts/check_screening_quality.py
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v77_plan --plan-only --include-run-id screening_prompt_runner_metadata_entropy_v77 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v77.json --selection-csv results/selection_report_smoke_v77.csv --preflight-markdown --require-min-scenarios 4 --require-min-personas 4 --require-min-temperature-count 3 --require-min-condition-cells 36 --require-min-total-samples 800 --require-min-planned-samples-per-run 800 --require-min-unique-scenario-labels 3 --require-min-unique-scenario-tags 10 --require-min-unique-scenario-domains 3 --require-min-unique-scenario-emotion-axes 3 --require-min-unique-scenario-difficulties 1 --require-min-unique-persona-style-tags 12 --require-min-scenario-label-entropy 0.75 --require-min-scenario-domain-entropy 0.70 --require-min-scenario-emotion-axis-entropy 0.70 --require-prompt-bank-version v7.7 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v77 metadata entropy guard"
python3 scripts/check_screening_quality.py --run-label screening_qc_v77 --max-manual-qc-review-traceable-known-query-top3-share 0.95
```

## Observed Results
- `py_compile`: passed
- plan-only preflight: `selected_run_cells=1`, `condition_cells=48`, `selected_total_samples=1152`
- screening QC: `status=review`, `quality_score=10.0`, `fail_count=6`

## Artifacts
- `results/selection_report_smoke_v77.json`
- `results/selection_report_smoke_v77.csv`
- `results/experiments/smoke_v77_plan/preflight.json`
- `results/experiments/smoke_v77_plan/preflight.md`
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
