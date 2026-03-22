# Experiment Plan v0.8

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v4.2`, adding temporal-holdout / antithetic-pair / stage-budget starvation scenarios (`screening_temporal_holdout_blindspot`, `prompt_bank_antithetic_pair_gap`, `runner_stage_budget_starvation`) on top of prior recall/drift/recovery sets.
- Persona bank now also includes `screening_recall_triager`, `prompt_antithesis_designer`, and `stage_budget_orchestrator` to probe screening 재현율 우선순위, 반대축 prompt 설계, 단계별 예산 운영 전략.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes `screening_prompt_runner_governance_v43`, while runner supports aggregate batch-coverage gates (`--require-min-selected-scenarios`, `--require-min-selected-personas`, `--require-min-selected-scenario-tags`, `--require-min-selected-persona-style-tags`) plus `--continue-on-error`, `--max-failed-cells`, `--max-failure-streak`, `--require-min-successful-cells`, `--require-min-success-rate`, `--require-min-run-id-success-rate`, stage-specific retry controls (`--max-generation-retries`, `--max-analysis-retries`), stage timeout controls (`--generation-timeout-seconds`, `--analysis-timeout-seconds`), stage success floors (`--require-min-generation-success-rate`, `--require-min-analysis-success-rate`), JSONL command logs, and `--resume-verify-hashes`.

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
- For unstable or expensive runs, use `--max-retries` plus `--retry-backoff-seconds`; when failure modes differ by stage, split retry budgets via `--max-generation-retries` and `--max-analysis-retries`
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

## Smoke validation (v40 reliability loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v40 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75
printf '%s\n' screening_precision_rebalance_v35 prompt_runner_resilience_v35 screening_prompt_replay_v36 screening_prompt_runner_hardening_v37 screening_prompt_runner_resilience_v38 screening_prompt_runner_autonomy_v39 screening_prompt_runner_reliability_v40 > /tmp/llm_emotion_run_ids_v40.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v40_plan --plan-only --run-id-file /tmp/llm_emotion_run_ids_v40.txt --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v40.json --selection-csv results/selection_report_smoke_v40.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 14 --require-min-run-ids 7 --require-min-total-samples 10000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 24 --require-min-selected-personas 19 --require-min-selected-scenario-tags 16 --require-min-selected-persona-style-tags 17 --require-prompt-bank-version v3.9 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v40"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v40_exec --run-id-file /tmp/llm_emotion_run_ids_v40.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --retry-backoff-seconds 1 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.07 --execution-log-jsonl results/experiments/smoke_v40_exec/command_log.jsonl --require-min-total-samples 1000
```

Observed results (v40):
- `screening_qc_v40`: `status=pass`, `quality_score=100.0`, 신규 수동 QC 게이트(`manual_qc_include_rows_floor`, `manual_qc_label_dominance_ceiling`) 계산/보고 확인
- `smoke_v40_plan`: 7개 run id preflight 통과(`selected_run_cells=14`, `selected_total_samples=10080`), 신규 `screening_prompt_runner_reliability_v40` 포함 selection report(JSON/CSV) 생성
- `smoke_v40_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.0714`로 `--require-min-success-rate` 가드레일 동작 검증

## Smoke validation (v41 stagewise loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v41 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65
printf '%s\n' screening_precision_rebalance_v35 prompt_runner_resilience_v35 screening_prompt_replay_v36 screening_prompt_runner_hardening_v37 screening_prompt_runner_resilience_v38 screening_prompt_runner_autonomy_v39 screening_prompt_runner_reliability_v40 screening_prompt_runner_stagewise_v41 > /tmp/llm_emotion_run_ids_v41.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v41_plan --plan-only --run-id-file /tmp/llm_emotion_run_ids_v41.txt --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v41.json --selection-csv results/selection_report_smoke_v41.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 16 --require-min-run-ids 8 --require-min-total-samples 11000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 28 --require-min-selected-personas 21 --require-min-selected-scenario-tags 17 --require-min-selected-persona-style-tags 18 --require-prompt-bank-version v4.0 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v41"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v41_exec --run-id-file /tmp/llm_emotion_run_ids_v41_exec.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --retry-backoff-seconds 1 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --execution-log-jsonl results/experiments/smoke_v41_exec/command_log.jsonl --require-min-total-samples 1000
```

Observed results (v41):
- `screening_qc_v41`: `status=pass`, `quality_score=100.0`, 신규 근거 분산 게이트(`screening_reason_diversity_floor`, `top_screening_reason_share_ceiling`) 계산/보고 확인
- `smoke_v41_plan`: 8개 run id preflight 통과(`selected_run_cells=16`, `selected_total_samples=11520`), 신규 `screening_prompt_runner_stagewise_v41` 포함 selection report(JSON/CSV) 생성
- `smoke_v41_exec`: v41 run subset 실행에서 `successful_cells=1`, `success_rate=0.5`로 단계별 재시도 옵션 및 run-id success floor(`--require-min-run-id-success-rate`) 동작 검증

## Smoke validation (v42 timeout+entropy loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v42 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-manual-qc-source-groups 3 --max-manual-qc-single-query-share 0.45 --max-empty-screening-reason-share 0.10
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v42_timeout_plan --plan-only --include-run-id screening_prompt_runner_timeout_v42 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v42_timeout.json --selection-csv results/selection_report_smoke_v42_timeout.csv --require-min-scenarios 5 --require-min-personas 4 --require-min-temperature-count 3 --require-min-temperature-span 0.49 --require-min-condition-cells 60 --require-min-run-cells 2 --require-min-run-ids 1 --require-min-total-samples 1400 --require-min-planned-samples-per-run 1400 --require-min-unique-scenario-tags 5 --require-min-unique-persona-style-tags 8 --require-prompt-bank-version v4.1 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-markdown --manifest-note "timeout/entropy/counterpair preflight v42"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v42_timeout_exec --include-run-id screening_prompt_runner_timeout_v42 --fail-on-missing-run-id --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-total-samples 700 --execution-log-jsonl results/experiments/smoke_v42_timeout_exec/command_log.jsonl --manifest-markdown
```

Observed results (v42):
- `screening_qc_v42`: `status=pass`, `quality_score=100.0`, 신규 QC 소스 다변성/집중도 게이트(`manual_qc_source_group_diversity_floor`, `manual_qc_single_query_share_ceiling`, `empty_screening_reason_share_ceiling`) 계산/보고 확인
- `smoke_v42_timeout_plan`: 신규 run preflight 통과(`selected_run_cells=2`, `selected_total_samples=1440`), prompt bank `v4.1` 고정 및 selection report(JSON/CSV) 생성
- `smoke_v42_timeout_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`, stage timeout 옵션(`--generation-timeout-seconds`, `--analysis-timeout-seconds`)과 run-id success floor 동작 검증


## Smoke validation (v43 governance+entropy loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v43 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.5 --min-manual-qc-source-groups 3 --max-manual-qc-single-query-share 0.45 --max-empty-screening-reason-share 0.10
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v43_plan --plan-only --include-run-id screening_prompt_runner_governance_v43 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v43.json --selection-csv results/selection_report_smoke_v43.csv --require-min-scenarios 5 --require-min-personas 4 --require-min-temperature-count 3 --require-min-temperature-span 0.49 --require-min-condition-cells 60 --require-min-run-cells 2 --require-min-run-ids 1 --require-min-total-samples 1400 --require-min-planned-samples-per-run 1400 --require-min-unique-scenario-tags 5 --require-min-unique-persona-style-tags 8 --require-prompt-bank-version v4.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-markdown --manifest-note "governance/entropy/budget preflight v43"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v43_exec --include-run-id screening_prompt_runner_governance_v43 --fail-on-missing-run-id --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --require-min-total-samples 700 --execution-log-jsonl results/experiments/smoke_v43_exec/command_log.jsonl --manifest-markdown
```

Observed results (v43):
- `screening_qc_v43`: `status=pass`, `quality_score=100.0`, 신규 엔트로피 게이트(`screening_reason_entropy_floor`, `manual_qc_query_entropy_floor`) 계산/보고 확인
- `smoke_v43_plan`: 신규 run preflight 통과(`selected_run_cells=2`, `selected_total_samples=1440`), prompt bank `v4.2` 고정 및 selection report(JSON/CSV) 생성
- `smoke_v43_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`, stage success floor(`--require-min-generation-success-rate`, `--require-min-analysis-success-rate`) 동작 검증
