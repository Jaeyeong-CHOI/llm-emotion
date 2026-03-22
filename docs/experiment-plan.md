# Experiment Plan v0.4

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v1.8`, adding six new calibration/repair-oriented scenarios (advisor-feedback ignored, deadline compression error, collaboration boundary blur, premature conclusion lock-in, participant-burden oversight, missed recovery window).
- Persona bank now includes `calibration_seeking` and `constraint_aware_planner` to separate uncertainty calibration vs constraint-aware action planning.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes dedicated `calibration_repair_v18` cells in addition to legacy baseline/counterfactual/social/research-process lanes.

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
- Optionally emit `--selection-report` JSON to log scenario/persona counts and prompt-bank fingerprints for each selected run id
- Archive `manifest.json` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --list-run-ids
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v18_plan --plan-only --selection-report results/selection_report_smoke_v18.json
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v18_exec --include-run-id calibration_repair_v18 --max-runs 1
```

Observed results:
- `--list-run-ids` now returns 7 ids including `calibration_repair_v18`
- `smoke_v18_plan`: planned 14 run cells and emitted `results/selection_report_smoke_v18.json`
- `smoke_v18_exec`: executed 1/2 selected cells under the run cap and produced dataset + metrics + manifest
