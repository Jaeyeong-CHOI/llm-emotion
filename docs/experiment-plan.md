# Experiment Plan v0.8

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v3.8`, adding recall/runner-safety scenarios (`screening_keyword_semantic_shadow`, `prompt_bank_recall_counterweight_injection`, `runner_preflight_success_floor_tripwire`) on top of prior multilingual/drift/recovery sets.
- Persona bank now also includes `retrieval_recall_mapper` and `success_floor_operator` to probe retrieval-gap recall safeguards and successful-cell floor operations in batch execution.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes `screening_prompt_runner_autonomy_v39`, while runner supports aggregate batch-coverage gates (`--require-min-selected-scenarios`, `--require-min-selected-personas`, `--require-min-selected-scenario-tags`, `--require-min-selected-persona-style-tags`) plus `--continue-on-error`, `--max-failed-cells`, `--max-failure-streak`, `--require-min-successful-cells`, retry controls, JSONL command logs, and `--resume-verify-hashes`.

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
- When long batches should not abort on first error, use `--continue-on-error` with `--max-failed-cells` so partial progress and explicit stop-threshold state are captured in manifest
- Enforce minimum planned cell volume via `--require-min-run-cells`, per-run condition-matrix breadth via `--require-min-condition-cells`, per-run sample floor via `--require-min-planned-samples-per-run`, repeat robustness via `--require-min-repeats`, temperature exploration spread via `--require-min-temperature-span`, scenario-tag breadth via `--require-min-unique-scenario-tags`, persona-style breadth via `--require-min-unique-persona-style-tags`
- Archive `manifest.json` + `manifest.md` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation (v37 hardening loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v36 --min-balanced-include-rows 2 --max-top-risk-reason-share 0.55
printf '%s\n' screening_precision_rebalance_v35 prompt_runner_resilience_v35 screening_prompt_replay_v36 screening_prompt_runner_hardening_v37 > /tmp/llm_emotion_run_ids_v37.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v37_plan --plan-only --run-id-file /tmp/llm_emotion_run_ids_v37.txt --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v37.json --selection-csv results/selection_report_smoke_v37.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 8 --require-min-run-ids 4 --require-min-total-samples 5600 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 16 --require-min-selected-personas 12 --require-prompt-bank-version v3.6 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v37"
```

Observed results:
- `screening_qc_v36`: `status=review`, `quality_score=85.0`, fail gate=`top_risk_reason_share_ceiling` (편향 위험은 탐지되었고 보고서/markdown 동시 갱신됨)
- `smoke_v37_plan`: 선택 run 4개 preflight 통과(`selected_run_cells=8`, `selected_total_samples=5760`), 신규 v37 run 포함 selection report(JSON/CSV) 및 manifest 생성 확인
- preflight summary에 `unique_selected_scenarios`/`unique_selected_personas`가 기록되어 배치 단위 coverage 검증 재현성 확보

## Smoke validation from this iteration
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v34
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v34_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v34.json --selection-csv results/selection_report_smoke_v34.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --require-prompt-bank-version v3.4 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v34"
printf '%s\n' screening_qc_runner_stress_v34 prompt_bank_balance_v34 > /tmp/llm_emotion_run_ids.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v34_exec --run-id-file /tmp/llm_emotion_run_ids.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --retry-backoff-seconds 1 --continue-on-error --max-failed-cells 1 --execution-log-jsonl results/experiments/smoke_v34_exec/command_log.jsonl --require-min-total-samples 1000
```

Observed results:
- `screening_qc_v34`: quality gate 전체 통과(`status=pass`, `quality_score=100.0`) 및 확장 게이트(균형 bin/dominance/query drift ceiling) 계산 확인
- `smoke_v34_plan`: 18개 run id 기준 plan-only preflight가 통과했고(`selected_run_cells=36`, `selected_total_samples=323056`), 신규 v34 run 포함 selection JSON/CSV가 생성됨
- `smoke_v34_exec`: `run-id-file` 기반 subset에서 1/4 run cell 실행이 통과했고(`selected_total_samples=2880`), `command_log.jsonl`과 manifest markdown 생성 확인
- 실행 manifest에는 기존 재현성 필드와 함께 `failed_cells`, `continue_on_error`, `max_failed_cells`, `stopped_early`가 기록되어 실패 허용 배치의 해석 가능성이 강화됨


## Smoke validation (v39 autonomy loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v38 --min-balanced-min-per-label 2
printf '%s
' screening_precision_rebalance_v35 prompt_runner_resilience_v35 screening_prompt_replay_v36 screening_prompt_runner_hardening_v37 screening_prompt_runner_resilience_v38 screening_prompt_runner_autonomy_v39 > /tmp/llm_emotion_run_ids_v39.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v39_plan --plan-only --run-id-file /tmp/llm_emotion_run_ids_v39.txt --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v39.json --selection-csv results/selection_report_smoke_v39.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 6 --require-min-total-samples 8600 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 22 --require-min-selected-personas 17 --require-prompt-bank-version v3.8 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v39"
```

Observed results (v39):
- `screening_qc_v38`: `status=pass`, `quality_score=100.0`, 신규 `balanced_min_per_label_floor` 게이트 포함 보고서 생성 확인
- `smoke_v39_plan`: 6개 run id preflight 통과(`selected_run_cells=12`, `selected_total_samples=8640`), prompt bank `v3.8` 고정 및 selection report(JSON/CSV) 생성
- `smoke_v39_exec`: subset 실행에서 1개 run cell 성공(`successful_cells=1`)으로 `--require-min-successful-cells` 가드레일 동작 검증
