# Experiment Plan v0.6

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v2.6`, adding four scenarios (`label_leakage_annotation_regret`, `metric_shift_false_reassurance`, `consent_scope_assumption_error`, `reproduction_env_mismatch`) focused on annotation leakage, metric drift, ethics scope, and env reproducibility failures.
- Persona bank now also includes `evidence_triage_operator` and `reproducibility_steward` to probe triage prioritization and reproducibility-first reasoning styles.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix keeps dedicated `repro_stress_v21` cells alongside baseline/counterfactual/social/research-process/calibration/audit lanes, with new per-run sample-floor validation (`--require-min-planned-samples-per-run`) in planning stage.

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
- Enforce minimum planned cell volume via `--require-min-run-cells`, per-run condition-matrix breadth via `--require-min-condition-cells`, and per-run sample floor via `--require-min-planned-samples-per-run` to catch over-filtered or underpowered subsets early
- Archive `manifest.json` + `manifest.md` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --list-run-ids
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v26_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v26.json --selection-csv results/selection_report_smoke_v26.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-temperature-count 2 --require-min-condition-cells 48 --require-min-run-cells 10 --require-min-run-ids 4 --require-min-total-samples 6000 --require-min-planned-samples-per-run 1100 --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v26"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v22_exec --include-run-id handoff_drift_v22 --fail-on-missing-run-id --manifest-markdown --max-runs 1
```

Observed results:
- `--list-run-ids` returns 11 ids including `handoff_drift_v22`
- `smoke_v26_plan`: planned 22 cells with per-run selection summaries plus JSON/CSV selection artifacts
- stricter floor test (`--require-min-planned-samples-per-run 1200`) fails as expected on 4 narrow runs at 1152 samples
- `smoke_v22_exec`: executes a bounded single cell under run cap and produces dataset + metrics + manifest (`manifest.json` + `manifest.md`)
