# llm-emotion

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening include quality tightened via additional include gates (`min_concept_diversity`, `min_abstract_tokens_for_include`) plus a `screening_confidence` field to separate high-confidence includes from borderline candidates
- Prompt bank expanded to `v1.7` with research-process regret scenarios (replication shortcuts, peer-review misread, late bug discovery, credit allocation, expectation overfit) and two personas (`methodical_skeptic`, `repair_committed`)
- Experiment runner reproducibility upgraded with per-cell runtime tracking (`duration_seconds`) and an auto-generated `reproduce.sh` script in each run folder, in addition to per-run-id aggregates and snapshot SHA-256 hashes

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
