# Experiment Plan v0.5

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v1.9`, extending calibration/repair coverage with four risk-sensitive scenarios (`ethics_review_bypass_regret`, `data_split_leakage_realization`, `stakeholder_signal_dismissed`, `overconfident_ablation_skip`).
- Persona bank adds `risk_calibrated_repairer` on top of the existing calibration personas.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes dedicated `risk_calibration_v19` cells in addition to legacy baseline/counterfactual/social/research-process/calibration lanes.

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
- Optionally emit `--selection-report` JSON to log scenario/persona counts and prompt-bank fingerprints for each selected run id
- Archive `manifest.json` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --list-run-ids
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v19_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v19.json
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v19_exec --include-run-id risk_calibration_v19 --max-runs 1
```

Observed results:
- `--list-run-ids` now returns 8 ids including `risk_calibration_v19`
- `smoke_v19_plan`: planned 16 run cells, printed per-run selection summaries, and emitted `results/selection_report_smoke_v19.json`
- `smoke_v19_exec`: executed 1/2 selected cells under the run cap and produced dataset + metrics + manifest
