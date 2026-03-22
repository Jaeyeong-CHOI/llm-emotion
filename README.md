# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality now supports calibrated manual-triage controls: configurable `--manual-qc-limit`, balanced `manual_qc_queue_by_label` buckets, `label_gate_conflicts` diagnostics, and optional ranked triage export via `--manual-qc-csv` for reviewer handoff.
- Prompt bank expanded to `v2.5` with three additional scenarios (`annotation_disagreement_escalation`, `pilot_result_overgeneralization`, `documentation_lag_regret`) and two personas (`triage_historian`, `counterexample_hunter`) to strengthen disagreement handling, over-generalization checks, and process-memory failures.
- Experiment runner reproducibility upgraded with run-breadth controls via `--require-min-run-ids` and `--require-min-temperature-count`, plus `--manifest-note-file`/`cli_invocation` persistence in `manifest.json` for stronger replay/auditability.

## Repository structure
- `docs/`: review protocol, screening rubric, experiment plan, ops notes
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v25 --plan-only --print-selection --selection-report results/selection_report_smoke_v25.json --selection-csv results/selection_report_smoke_v25.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-temperature-count 4 --require-min-condition-cells 48 --require-min-run-cells 10 --require-min-run-ids 4 --require-min-total-samples 6000 --manifest-note-file docs/experiment-plan.md --manifest-note "preflight"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v22 --include-run-id handoff_drift_v22 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --require-min-total-samples 1000
```

## Prompt-bank filtering
`scripts/generate_dataset.py` supports reproducible subset selection:

```bash
python3 scripts/generate_dataset.py \
  --out /tmp/mock.jsonl \
  --prompt-bank prompts/prompt_bank_ko.json \
  --scenario-tags counterfactual \
  --persona-ids regretful,self_compassionate
```

## Experiment reproducibility
- Run definitions live in `ops/experiment_matrix.json`
- `results/experiments/<label>/manifest.json` records environment and cell status
- `results/experiments/<label>/snapshots/` stores the config and prompt-bank snapshots used for the batch
