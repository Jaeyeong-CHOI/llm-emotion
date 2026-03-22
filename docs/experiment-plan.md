# Experiment Plan v0.8

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v3.2`, adding four scenarios (`query_drift_repair_sprint`, `alias_gap_backfill_protocol`, `resume_hash_mismatch_incident`, `preflight_coverage_floor_enforcement`) focused on query-drift recovery, alias-gap backfill, resume hash mismatch, and preflight coverage-floor enforcement.
- Persona bank now also includes `drift_repair_forecaster` and `hash_integrity_sentinel` to probe drift-repair planning and artifact-integrity-first reasoning styles.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes `screening_drift_hash_guard_v25`, while runner supports `--resume-verify-hashes` to fail-fast when resumed artifacts do not match stored hashes.

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
- Always inspect generated `preflight.json` / `preflight.csv` to confirm `prompt_bank_version`, tag breadth, temperature span, and planned sample floor before full execution
- When resuming, use `--resume-verify-hashes` to verify `dataset_sha256`/`metrics_sha256` integrity before skipping completed cells
- Enforce minimum planned cell volume via `--require-min-run-cells`, per-run condition-matrix breadth via `--require-min-condition-cells`, per-run sample floor via `--require-min-planned-samples-per-run`, repeat robustness via `--require-min-repeats`, temperature exploration spread via `--require-min-temperature-span`, scenario-tag breadth via `--require-min-unique-scenario-tags`, persona-style breadth via `--require-min-unique-persona-style-tags`
- Archive `manifest.json` + `manifest.md` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v32_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v32.json --selection-csv results/selection_report_smoke_v32.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --require-prompt-bank-version v3.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v32"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v25_hash_exec --include-run-id screening_drift_hash_guard_v25 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --require-prompt-bank-version v3.2
```

Observed results:
- `smoke_v32_plan`: 14개 run id 기준 plan-only preflight가 통과했고(`selected_run_cells=28`), 신규 run `screening_drift_hash_guard_v25` 포함 selection JSON/CSV가 생성됨
- stricter persona-style gate test (`--require-min-unique-persona-style-tags 8`)는 기존과 동일하게 좁은 focused run에서 실패함(회귀 확인)
- `smoke_v25_hash_exec`: 신규 v25 run에서 단일 셀 실행 + manifest markdown 생성 확인
- 실행 manifest의 run row에 `dataset_sha256`/`metrics_sha256`가 기록되어 resume 무결성 검증 기반이 마련됨
