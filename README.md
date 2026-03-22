# llm-emotion

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening upgraded with an additional include-guard (`include_margin_min`, `max_penalty_for_include`) so borderline high-penalty hits are downgraded to `review` instead of auto-included
- Prompt bank expanded to `v1.6` with new distributed-responsibility / evidence-warning / value-drift / failed-repair scenarios plus `counterfactual_minimizer` and `accountability_balancer` personas
- Experiment runner now writes per-run-id aggregates (`run_id_summary` in manifest + `run_id_summary.csv`) and SHA-256 hashes for config/prompt snapshots for reproducible provenance auditing

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

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v15 --plan-only --manifest-note "preflight"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v15 --include-run-id method_signal_v15 --strict-clean
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
