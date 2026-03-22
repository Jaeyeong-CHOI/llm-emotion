# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality tightened with an explicit `require_llm_concept` gate for both `include` and `review`, preventing psychology-only hits without direct LLM evidence from being over-promoted.
- Prompt bank expanded to `v2.0` with four new audit/ethics scenarios (`null_result_suppression_regret`, `dataset_shift_ignored`, `mentoring_capacity_tradeoff`, `posthoc_storytelling_bias`) and two personas (`process_auditor`, `ethical_red_teamer`).
- Experiment runner reproducibility upgraded with guardrails and richer artifacts: `--require-min-scenarios`, `--require-min-personas`, `--fail-on-missing-run-id`, `--selection-csv`, and `--manifest-markdown`.

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
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v20 --plan-only --print-selection --selection-report results/selection_report_smoke_v20.json --selection-csv results/selection_report_smoke_v20.csv --require-min-scenarios 4 --require-min-personas 4 --manifest-note "preflight"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v20 --include-run-id audit_ethics_v20 --fail-on-missing-run-id --manifest-markdown --max-runs 1
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
