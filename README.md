# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality tightened with a new sentence-level bridge signal (`bridge_sentence_hits`) that rewards abstracts explicitly connecting LLM terms and target affect/counterfactual concepts in the same sentence; include gating now also requires either title hits or bridge evidence.
- Prompt bank expanded to `v1.8` with six new research-process/repair scenarios (advisor feedback ignored, deadline compression error, collaboration boundary blur, premature conclusion lock-in, participant-burden oversight, missed recovery window) and two personas (`calibration_seeking`, `constraint_aware_planner`).
- Experiment runner reproducibility upgraded with: run-id listing (`--list-run-ids`), optional selection reports (`--selection-report`) containing scenario/persona counts and prompt-bank fingerprints, plus per-row fingerprint export in `runs.csv`.

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

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v18 --plan-only --selection-report results/selection_report_smoke_v18.json --manifest-note "preflight"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v18 --include-run-id calibration_repair_v18 --max-runs 1
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
