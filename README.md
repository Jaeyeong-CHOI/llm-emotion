# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality now emits explicit QC diagnostics (`--audit-out`) with a ranked `manual_qc_queue` and `triage_risk` counters for uncertain include/review/exclude boundary cases, in addition to borderline and gate-failure alerts.
- Prompt bank expanded to `v2.3` with three additional process-risk scenarios (`rollback_decision_paralysis`, `evaluation_data_contamination_regret`, `handover_checklist_omission`) and two personas (`drift_sentinel`, `handoff_reliability_engineer`) to probe drift detection and handoff reliability behavior.
- Experiment runner reproducibility upgraded with dataset-scale planning guards via `--require-min-total-samples`, plus per-run `planned_samples` tracking in selection outputs and manifests, alongside existing checks/artifacts (`--require-min-scenarios`, `--require-min-personas`, `--require-min-condition-cells`, `--require-min-run-cells`, `--fail-on-missing-run-id`, `--selection-csv`, `--manifest-markdown`).

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
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v22 --plan-only --print-selection --selection-report results/selection_report_smoke_v22.json --selection-csv results/selection_report_smoke_v22.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-condition-cells 48 --require-min-run-cells 10 --require-min-total-samples 6000 --manifest-note "preflight"
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
