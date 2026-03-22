# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality now emits explicit QC diagnostics (`--audit-out`) with borderline include/review candidates and high-score-but-non-LLM excludes for fast manual triage.
- Prompt bank expanded to `v2.1` with four new reproducibility-risk scenarios (`model_spec_drift_blindspot`, `retraction_risk_signal_ignored`, `stakeholder_harm_latency`, `benchmark_shortcut_normalization`) and two personas (`failure_mode_cartographer`, `replication_guardian`).
- Experiment runner reproducibility upgraded with stricter planning guards via `--require-min-run-cells` plus existing run-selection checks/artifacts (`--require-min-scenarios`, `--require-min-personas`, `--fail-on-missing-run-id`, `--selection-csv`, `--manifest-markdown`).

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

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v21 --plan-only --print-selection --selection-report results/selection_report_smoke_v21.json --selection-csv results/selection_report_smoke_v21.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-run-cells 10 --manifest-note "preflight"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v21 --include-run-id repro_stress_v21 --fail-on-missing-run-id --manifest-markdown --max-runs 1
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
