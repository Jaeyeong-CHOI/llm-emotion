# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality now reports **alias/개념군 커버리지 진단**: `alias_coverage`, `required_group_coverage`, `alias_gap_candidates`, `manual_qc_queue_risk_reason_summary`가 리포트/감사 산출물에 추가되어 왜 놓쳤는지와 어떤 축을 보강해야 하는지 바로 추적할 수 있습니다.
- Prompt bank expanded to `v3.0` with four additional scenarios (`screening_bridge_signal_miss`, `screening_query_drift_false_negative`, `prompt_bank_anchor_overfit`, `runner_preflight_evidence_freeze`) and two personas (`retrieval_gap_mapper`, `preflight_evidence_curator`) for retrieval-gap auditing and preflight evidence-freeze discipline.
- Experiment runner reproducibility now auto-emits `preflight.json` and `preflight.csv`, records `prompt_bank_version`, and summarizes minimum design breadth in manifest `preflight_summary` alongside existing preflight gates.

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
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v30_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v30.json --selection-csv results/selection_report_smoke_v30.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 8 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v30"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v24 --include-run-id screening_alias_preflight_v24 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --require-min-total-samples 1000
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
- `results/experiments/<label>/preflight.json` and `preflight.csv` capture selection/preflight diagnostics for review before or after execution
