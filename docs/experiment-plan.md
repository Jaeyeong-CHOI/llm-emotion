# Experiment Plan v0.3

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v1.7`, adding research-process regret situations (replication shortcut pressure, peer-review misread, late bug discovery, credit-allocation regret, expectation overfit).
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Persona bank now includes `methodical_skeptic` and `repair_committed` to separate evidence-checking vs action-oriented repair styles.
- Experiment matrix now includes dedicated `research_process_v17` cells in addition to legacy baseline/counterfactual/social lanes.

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
- Use `--plan-only` before expensive batches to verify selected cells and bank snapshots
- Archive `manifest.json` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22T07:06:35Z`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v14_plan --plan-only
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v14_exec --include-run-id counterfactual_focus_v14 --max-runs 1
```

Observed results:
- `smoke_v14_plan`: planned 6 run cells, wrote manifest and prompt-bank snapshots
- `smoke_v14_exec`: executed 1/2 selected cells under the run cap and produced dataset + metrics + manifest
