# Experiment Plan v0.8

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v3.3`, adding multilingual/calibration scenarios (`cross_lingual_annotation_drift`, `fine_grained_emotion_boundary_case`, `manual_qc_escalation_handoff`, `batch_resume_after_partial_failure`) on top of the prior drift/alias/hash coverage set.
- Persona bank now also includes `cross_lingual_calibrator`, `emotion_taxonomy_auditor`, `manual_qc_triage_lead`, and `batch_recovery_planner` to probe cross-lingual calibration, fine-grained emotion coding, QC handoff, and partial-failure recovery styles.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes `multilingual_screening_calibration_v33` and `batch_recovery_runner_v33`, while runner supports `--run-id-file`, `--max-retries`, `--retry-backoff-seconds`, and JSONL command logs in addition to `--resume-verify-hashes`.

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
- Use `--run-id-file` when a subset must be frozen as a handoff artifact rather than reconstructed from shell history
- Use `--print-selection` for immediate terminal-side sanity checks of selected scenario/persona counts
- Enforce minimum design breadth via `--require-min-scenarios` and `--require-min-personas`
- Use `--fail-on-missing-run-id` when selecting subsets to prevent silent typos
- Optionally emit `--selection-report` JSON and `--selection-csv` to log scenario/persona counts and prompt-bank fingerprints for each selected run id
- Always inspect generated `preflight.json` / `preflight.csv` to confirm `prompt_bank_version`, tag breadth, temperature span, and planned sample floor before full execution
- When resuming, use `--resume-verify-hashes` to verify `dataset_sha256`/`metrics_sha256` integrity before skipping completed cells
- For unstable or expensive runs, use `--max-retries` plus `--retry-backoff-seconds` and archive `command_log.jsonl` with the manifest
- Enforce minimum planned cell volume via `--require-min-run-cells`, per-run condition-matrix breadth via `--require-min-condition-cells`, per-run sample floor via `--require-min-planned-samples-per-run`, repeat robustness via `--require-min-repeats`, temperature exploration spread via `--require-min-temperature-span`, scenario-tag breadth via `--require-min-unique-scenario-tags`, persona-style breadth via `--require-min-unique-persona-style-tags`
- Archive `manifest.json` + `manifest.md` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v33_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v33.json --selection-csv results/selection_report_smoke_v33.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --require-prompt-bank-version v3.3 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v33"
printf '%s\n' multilingual_screening_calibration_v33 batch_recovery_runner_v33 > /tmp/llm_emotion_run_ids.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v33_exec --run-id-file /tmp/llm_emotion_run_ids.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --retry-backoff-seconds 1 --execution-log-jsonl results/experiments/smoke_v33_exec/command_log.jsonl --require-min-total-samples 1000
```

Observed results:
- `smoke_v33_plan`: 16개 run id 기준 plan-only preflight가 통과했고(`selected_run_cells=32`, `selected_total_samples=288832`), 신규 v33 run 포함 selection JSON/CSV가 생성됨
- `smoke_v33_exec`: `run-id-file` 기반 subset에서 1/4 run cell 실행이 통과했고(`selected_total_samples=2880`), `command_log.jsonl`과 manifest markdown 생성 확인
- 실행 manifest에는 `run_id_file`, retry 설정, `execution_log_jsonl`, `dataset_sha256`/`metrics_sha256`가 함께 기록되어 부분 실패 복구와 resume 무결성 검증 기반이 확장됨
