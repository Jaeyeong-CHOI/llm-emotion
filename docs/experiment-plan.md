# Experiment Plan v0.2

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank `v1.4` expands scenario coverage around social loss, ambiguity, moral tradeoffs, and unfinished identity projects.
- Scenario rows now carry `tags`, allowing focused runs such as `counterfactual`-only or `social`-only subsets.
- Persona rows now carry `style_tags`, supporting more interpretable prompt families.
- Experiment matrix includes:
  - `baseline_v14_seed42`
  - `counterfactual_focus_v14`
  - `social_loss_v14`

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

## Smoke validation from this iteration
Executed on `2026-03-22T07:06:35Z`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v14_plan --plan-only
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v14_exec --include-run-id counterfactual_focus_v14 --max-runs 1
```

Observed results:
- `smoke_v14_plan`: planned 6 run cells, wrote manifest and prompt-bank snapshots
- `smoke_v14_exec`: executed 1/2 selected cells under the run cap and produced dataset + metrics + manifest
