# Experiment Plan v0.5

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v2.0`, extending audit/ethics pressure coverage with four scenarios (`null_result_suppression_regret`, `dataset_shift_ignored`, `mentoring_capacity_tradeoff`, `posthoc_storytelling_bias`).
- Persona bank adds `process_auditor` and `ethical_red_teamer` to stress-test accountability and risk-sensitive narratives.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes dedicated `audit_ethics_v20` cells in addition to legacy baseline/counterfactual/social/research-process/calibration lanes.

## Experimental factors
- Prompt condition: control, deprivation/loss, counterfactual, social, identity, moral, regulation
- Persona condition: baseline plus reflective, ruminative, self-compassionate, socially-guarded, meaning-making, loss-averse variants
- Temperature: low / medium / high (`0.2`, `0.4`, `0.7`, `1.0` depending on run)
- Models: current mock pipeline plus future real-model adapters

## Dependent variables
### Automated markers
1. Counterfactual phrases
2. Regret lexicon count
3. Condition-level contrasts by scenario/persona/temperature

### Planned manual coding
- Regret intensity
- Identity threat
- Repair orientation
- Social disclosure / masking

## Reproducibility rules
- Use `ops/experiment_matrix.json` as the only run definition source
- Preserve run snapshots under `results/experiments/<label>/snapshots/`
- Keep prompt bank filters in config fields:
  - `scenario_ids`
  - `scenario_tags`
  - `persona_ids`
- Use `--list-run-ids` + `--plan-only` before expensive batches to verify selected cells and bank snapshots
- Use `--print-selection` for immediate terminal-side sanity checks of selected scenario/persona counts
- Enforce minimum design breadth via `--require-min-scenarios` and `--require-min-personas`
- Use `--fail-on-missing-run-id` when selecting subsets to prevent silent typos
- Optionally emit `--selection-report` JSON and `--selection-csv` to log scenario/persona counts and prompt-bank fingerprints for each selected run id
- Archive `manifest.json` + `manifest.md` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --list-run-ids
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v20_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v20.json --selection-csv results/selection_report_smoke_v20.csv --require-min-scenarios 4 --require-min-personas 4
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v20_exec --include-run-id audit_ethics_v20 --fail-on-missing-run-id --manifest-markdown --max-runs 1
```

Observed results:
- `--list-run-ids` now returns 9 ids including `audit_ethics_v20`
- `smoke_v20_plan`: planned cells with per-run selection summaries plus JSON/CSV selection artifacts
- `smoke_v20_exec`: executed 1/2 selected cells under the run cap and produced dataset + metrics + manifest (`manifest.json` + `manifest.md`)
