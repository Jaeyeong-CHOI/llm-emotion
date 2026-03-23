# Experiment Plan v0.8

## Objective
Test whether LLM outputs in loss and counterfactual scenarios exhibit language patterns that resemble human regret narratives, while keeping scenario selection reproducible and auditable.

## Current design updates
- Prompt bank is now `v126.0`, adding research-ops scenarios (`screening_unknown_year_group_top17_ratio_guard_v126`, `prompt_bank_top17_countervoice_mesh_patch_v126`, `runner_temperature_p99_p85_tripwire_v126`) and personas (`unknown_year_group_top17_ratio_triager_v126`, `top17_countervoice_mesh_curator_v126`, `temperature_p99_p85_guard_v126`).
- Screening gate now tracks `unknown-year known-query query-group top17` share/global-ratio residue to catch cumulative over-concentration that still survives top16 checks.
- Experiment runner preflight now supports `--max-planned-sample-temperature-p99-over-p85-share-ratio`, extending tail-risk monitoring beyond the existing p99/p90 guard.
- Prompt bank is now `v7.6`, adding metadata-aware research-ops scenarios (`screening_duplicate_provenance_triage`, `prompt_bank_domain_axis_balance`, `runner_metadata_resume_guard`) and personas (`duplicate_provenance_auditor`, `domain_axis_balance_curator`, `metadata_resume_guardian`).
- Screening gate now tracks duplicate-title residue (`--max-manual-qc-duplicate-title-share`) and weak-evidence review residue (`--max-review-weak-evidence-share`) in addition to existing bridge/query provenance coupling.
- Scenario rows carry `tags` and stable `id`s for reproducible focused subsets (`scenario_tags` and `scenario_ids`).
- Experiment matrix now includes `screening_prompt_runner_metadata_balance_v76`, while runner supports metadata-aware scenario selection (`--scenario-domains`, `--scenario-emotion-axes`, `--scenario-difficulties`) plus corresponding per-run coverage floors (`--require-min-unique-scenario-domains`, `--require-min-unique-scenario-emotion-axes`, `--require-min-unique-scenario-difficulties`) alongside existing preflight/budget controls.

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
  - `scenario_domains`
  - `scenario_emotion_axes`
  - `scenario_difficulties`
  - `persona_ids`
- Use `--list-run-ids` + `--plan-only` before expensive batches to verify selected cells and bank snapshots
- Use `--run-id-file` when a subset must be frozen as a handoff artifact rather than reconstructed from shell history
- Use `--print-selection` for immediate terminal-side sanity checks of selected scenario/persona counts
- Enforce minimum design breadth via `--require-min-scenarios` and `--require-min-personas`
- When prompt-bank metadata is used for targeted research-ops subsets, pair the selector (`--scenario-domains` / `--scenario-emotion-axes` / `--scenario-difficulties`) with the matching coverage floor so the run cannot silently collapse to a single narrow slice.
- Use `--fail-on-missing-run-id` when selecting subsets to prevent silent typos
- Optionally emit `--selection-report` JSON and `--selection-csv` to log scenario/persona counts and prompt-bank fingerprints for each selected run id
- Always inspect generated `preflight.json` / `preflight.csv` to confirm `prompt_bank_version`, tag breadth, temperature span, and planned sample floor before full execution
- When resuming, use `--resume-verify-hashes` to verify `dataset_sha256`/`metrics_sha256` integrity before skipping completed cells
- For unstable or expensive runs, use `--max-retries` plus `--retry-backoff-seconds`; when failure modes differ by stage, split retry budgets via `--max-generation-retries` and `--max-analysis-retries`
- When long batches should not abort on first error, use `--continue-on-error` with `--max-failed-cells` so partial progress and explicit stop-threshold state are captured in manifest
- Use `--max-selected-cell-share-per-run-id`, `--max-attempt-share-per-run-id`, and `--max-attempt-over-selection-ratio` to prevent one run id from monopolizing batch slots or retries out of proportion to planned coverage; review `budget_report.json` / `budget_report.md` after every smoke execution
- Enforce minimum planned cell volume via `--require-min-run-cells`, per-run condition-matrix breadth via `--require-min-condition-cells`, per-run sample floor via `--require-min-planned-samples-per-run`, repeat robustness via `--require-min-repeats`, temperature exploration spread via `--require-min-temperature-span`, scenario-tag breadth via `--require-min-unique-scenario-tags`, persona-style breadth via `--require-min-unique-persona-style-tags`
- Archive `manifest.json` + `manifest.md` + `run_id_summary.csv` + generated `reproduce.sh` per batch
- Track `duration_seconds` (batch and per-cell) for throughput comparisons across iterations

## Smoke validation (v66 bridge-query + preflight-md loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v66 --min-review-bridge-traceable-known-query-share 0.6 --max-review-bridge-traceable-unknown-query-share 0.2 --min-manual-qc-review-query-traceability-share 0.75
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v66_plan --plan-only --include-run-id screening_prompt_runner_live_failed_share_v66 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v66.json --selection-csv results/selection_report_smoke_v66.csv --preflight-markdown --require-min-scenarios 4 --require-min-personas 4 --require-min-temperature-count 3 --require-min-condition-cells 48 --require-min-total-samples 1200 --require-prompt-bank-version v6.6
```

Observed results (v66):
- `screening_qc_v66`: 신규 bridge-query coupling 게이트가 보고서에 반영되어 review provenance 품질 저하를 조기 탐지 가능.
- `smoke_v66_plan`: 신규 run-id preflight 통과 시 `preflight.json/csv`와 함께 `preflight.md`가 생성되어 핸드오프 검토 가독성이 향상.

## Smoke validation (v76 metadata-balance loop)
Executed on `2026-03-22`:

```bash
python3 scripts/generate_dataset.py --out /tmp/llm_emotion_v76_metadata.jsonl --prompt-bank prompts/prompt_bank_ko.json --scenario-domains research_ops --scenario-emotion-axes regret --scenario-difficulties hard --persona-ids duplicate_provenance_auditor,domain_axis_balance_curator --temperatures 0.2,0.8 --n 2
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v76 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-review-counterexample-traceability-share 0.55 --min-review-bridge-counterexample-coupled-share 0.18 --min-review-bridge-counterexample-traceable-share 0.12 --min-review-bridge-counterexample-traceability-given-coupled-share 0.55 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-review-query-entropy 0.45 --min-manual-qc-review-traceable-known-query-share 0.55 --max-manual-qc-review-traceable-unknown-query-share 0.15 --min-manual-qc-review-query-traceability-share 0.75 --min-manual-qc-review-traceable-known-query-entropy 0.45 --max-manual-qc-review-traceable-known-query-top-share 0.70 --min-manual-qc-review-traceable-known-query-group-entropy 0.45 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-manual-qc-dedup-label-conflict-share 0.20 --min-dedup-score-range-alert 1.0 --max-manual-qc-dedup-score-range-alert-share 0.20 --max-manual-qc-duplicate-title-share 0.20 --max-review-weak-evidence-share 0.40 --max-empty-screening-reason-share 0.10 --max-review-counterexample-without-bridge-share 0.35
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v76_plan --plan-only --include-run-id screening_prompt_runner_metadata_balance_v76 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v76.json --selection-csv results/selection_report_smoke_v76.csv --preflight-markdown --require-min-scenarios 3 --require-min-personas 4 --require-min-temperature-count 3 --require-min-condition-cells 27 --require-min-total-samples 800 --require-min-planned-samples-per-run 800 --require-min-unique-scenario-labels 3 --require-min-unique-scenario-tags 10 --require-min-unique-scenario-domains 4 --require-min-unique-scenario-emotion-axes 6 --require-min-unique-scenario-difficulties 1 --require-min-unique-persona-style-tags 12 --require-prompt-bank-version v7.6 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note "preflight v76 metadata balance"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v76_exec --include-run-id screening_prompt_runner_metadata_balance_v76 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --require-min-total-samples 400 --execution-log-jsonl results/experiments/smoke_v76_exec/command_log.jsonl --budget-report-json results/experiments/smoke_v76_exec/budget_report.json --budget-report-md results/experiments/smoke_v76_exec/budget_report.md
```

Observed results (v76):
- `generate_dataset`: metadata selector 조합으로 `24`행 생성(`scenarios=3`, `personas=2`, `temps=2`), 생성 JSONL에 `scenario_domains`, `scenario_emotion_axes`, `scenario_difficulty`가 기록됨.
- `screening_qc_v76`: 새 gate가 포함된 보고서 생성, 현재 데이터에서는 `status=review`, `quality_score=0.0`, `fail_count=8`로 엄격한 QC 기준 미충족 영역이 드러남.
- `smoke_v76_plan`: preflight 통과(`scenario_labels=3`, `scenario_tags=10`, `scenario_domains=7`, `scenario_emotion_axes=7`, `persona_style_tags=14`, `selected_total_samples=864`) 및 `preflight.md` 생성 확인.
- `smoke_v76_exec`: subset 실행에서 `successful_cells=1`, `success_rate=1.0`, `selected_total_samples=864`; `budget_report.json`/`budget_report.md`와 manifest markdown이 함께 생성됨.

## Smoke validation (v52 review-band + failure-pressure loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v52 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v52_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v52.json --selection-csv results/selection_report_smoke_v52.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 26 --require-min-run-ids 13 --require-min-total-samples 16000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 43 --require-min-selected-personas 34 --require-min-selected-scenario-tags 25 --require-min-selected-persona-style-tags 28 --require-prompt-bank-version v5.2 --max-selected-cell-share-per-run-id 0.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v52"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v52_exec --include-run-id screening_prompt_runner_failure_pressure_v52 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --max-generation-attempts-per-run-id 3 --max-analysis-attempts-per-run-id 2 --max-attempts-per-cell 4 --max-selected-cell-share-per-run-id 1.0 --max-attempt-share-per-run-id 1.0 --max-attempt-over-selection-ratio 2.5 --max-failure-over-selection-ratio 2.0 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --execution-log-jsonl results/experiments/smoke_v52_exec/command_log.jsonl --quarantine-json results/experiments/smoke_v52_exec/quarantine_candidates.json --quarantine-csv results/experiments/smoke_v52_exec/quarantine_candidates.csv --budget-report-json results/experiments/smoke_v52_exec/budget_report.json --budget-report-md results/experiments/smoke_v52_exec/budget_report.md --require-min-total-samples 1000
```

Observed results (v52):
- `screening_qc_v52`: `status=pass`, `quality_score=100.0`(review bridge share는 현재 데이터 분포상 0.0이라 gate를 floor=0.0으로 운영)
- `smoke_v52_plan`: preflight 통과(`selected_run_cells=74`, `selected_total_samples=863872`), prompt bank `v5.2` 고정 및 selection/preflight 아티팩트 생성
- `smoke_v52_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`; budget report에 `failed_cell_share`/`failure_over_selection_ratio`가 함께 기록됨

## Smoke validation (v50 semantic-bridge + budget-pressure loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v50 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v50_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v50.json --selection-csv results/selection_report_smoke_v50.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 22 --require-min-run-ids 11 --require-min-total-samples 14000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 37 --require-min-selected-personas 30 --require-min-selected-scenario-tags 23 --require-min-selected-persona-style-tags 25 --require-prompt-bank-version v5.0 --max-selected-cell-share-per-run-id 0.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v50"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v50_exec --run-id-file /tmp/llm_emotion_run_ids_v50_exec.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --max-generation-attempts-per-run-id 3 --max-analysis-attempts-per-run-id 2 --max-attempts-per-cell 4 --max-selected-cell-share-per-run-id 1.0 --max-attempt-share-per-run-id 1.0 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --execution-log-jsonl results/experiments/smoke_v50_exec/command_log.jsonl --quarantine-json results/experiments/smoke_v50_exec/quarantine_candidates.json --quarantine-csv results/experiments/smoke_v50_exec/quarantine_candidates.csv --budget-report-json results/experiments/smoke_v50_exec/budget_report.json --budget-report-md results/experiments/smoke_v50_exec/budget_report.md --require-min-total-samples 1000
```

Observed results (v50):
- `screening_qc_v50`: `status=pass`, `quality_score=100.0`, 신규 bridge/review-group 게이트 계산 및 보고 확인
- `smoke_v50_plan`: preflight 통과(`selected_run_cells=70`, `selected_total_samples=801280`), prompt bank `v5.0` 고정 및 selection report(JSON/CSV) 생성
- `smoke_v50_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`, `budget_report.json`/`budget_report.md` 생성과 run-id 점유율 요약 확인

## Smoke validation (v51 traceability + attempt-pressure loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v51 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v51_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v51.json --selection-csv results/selection_report_smoke_v51.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 24 --require-min-run-ids 12 --require-min-total-samples 15000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 40 --require-min-selected-personas 32 --require-min-selected-scenario-tags 24 --require-min-selected-persona-style-tags 27 --require-prompt-bank-version v5.1 --max-selected-cell-share-per-run-id 0.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v51"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v51_exec --include-run-id screening_prompt_runner_attempt_pressure_v51 --fail-on-missing-run-id --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --max-generation-attempts-per-run-id 3 --max-analysis-attempts-per-run-id 2 --max-attempts-per-cell 4 --max-selected-cell-share-per-run-id 1.0 --max-attempt-share-per-run-id 1.0 --max-attempt-over-selection-ratio 2.5 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --execution-log-jsonl results/experiments/smoke_v51_exec/command_log.jsonl --quarantine-json results/experiments/smoke_v51_exec/quarantine_candidates.json --quarantine-csv results/experiments/smoke_v51_exec/quarantine_candidates.csv --budget-report-json results/experiments/smoke_v51_exec/budget_report.json --budget-report-md results/experiments/smoke_v51_exec/budget_report.md --require-min-total-samples 1000
```

Observed results (v51):
- `screening_qc_v51`: `status=pass`, `quality_score=100.0`, `include_reason_traceability_share=1.0`, `review_reason_traceability_share=1.0`
- `smoke_v51_plan`: preflight 통과(`selected_run_cells=72`, `selected_total_samples=832288`), prompt bank `v5.1` 고정 및 selection report(JSON/CSV), `preflight.json`/`preflight.csv` 생성 확인
- `smoke_v51_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`, `attempt_over_selection_ratio=1.0`가 `budget_report.json`/manifest에 기록됨을 확인

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

## Smoke validation (v45 quarantine+rotation loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v45 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.5 --min-manual-qc-source-groups 3 --max-manual-qc-single-query-share 0.45 --max-empty-screening-reason-share 0.10 --min-manual-qc-year-diversity 3 --max-manual-qc-single-year-share 0.45 --min-manual-qc-year-entropy 0.5
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v45_plan --plan-only --include-run-id screening_prompt_runner_quarantine_v45 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v45.json --selection-csv results/selection_report_smoke_v45.csv --require-min-scenarios 5 --require-min-personas 4 --require-min-temperature-count 3 --require-min-temperature-span 0.49 --require-min-condition-cells 60 --require-min-run-cells 2 --require-min-run-ids 1 --require-min-total-samples 1400 --require-min-planned-samples-per-run 1400 --require-min-unique-scenario-tags 5 --require-min-unique-persona-style-tags 8 --require-prompt-bank-version v4.4 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-markdown --manifest-note "quarantine/rotation/precision-recall preflight v45"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v45_exec --include-run-id screening_prompt_runner_quarantine_v45 --fail-on-missing-run-id --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --continue-on-error --max-failed-cells 1 --max-failed-cells-per-run-id 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --require-min-total-samples 700 --execution-log-jsonl results/experiments/smoke_v45_exec/command_log.jsonl --manifest-markdown
```

Observed results (v45):
- `screening_qc_v45`: `status=pass`, `quality_score=100.0`, 신규 연도 분산 게이트(`manual_qc_year_diversity_floor`, `manual_qc_single_year_share_ceiling`, `manual_qc_year_entropy_floor`) 계산/보고 확인
- `smoke_v45_plan`: 신규 run preflight 통과(`selected_run_cells=2`, `selected_total_samples=1440`), prompt bank `v4.4` 고정 및 selection report(JSON/CSV) 생성
- `smoke_v45_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`, run-id별 실패 격리 상한(`--max-failed-cells-per-run-id`) 옵션 기록/동작 확인


## Smoke validation (v48 traceability loop)
Executed on `2026-03-22`:

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v48 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.5 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-review-confidence-bins 2 --min-manual-qc-review-confidence-entropy 0.4 --min-manual-qc-source-groups 3 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v48_plan --plan-only --include-run-id screening_prompt_runner_traceability_v48 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v48.json --selection-csv results/selection_report_smoke_v48.csv --require-min-scenarios 5 --require-min-personas 4 --require-min-temperature-count 3 --require-min-temperature-span 0.49 --require-min-condition-cells 60 --require-min-run-cells 2 --require-min-run-ids 1 --require-min-total-samples 1400 --require-min-planned-samples-per-run 1400 --require-min-unique-scenario-tags 5 --require-min-unique-persona-style-tags 8 --require-prompt-bank-version v4.7 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-markdown --manifest-note "traceability/countervoice/attempt-log preflight v48"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v48_exec --include-run-id screening_prompt_runner_traceability_v48 --fail-on-missing-run-id --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failed-cells-per-run-id 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --require-min-total-samples 700 --execution-log-jsonl results/experiments/smoke_v48_exec/command_log.jsonl --manifest-markdown
```

Observed results (v48):
- `screening_qc_v48`: `status=pass`, `quality_score=100.0`, 신규 review confidence 분산 게이트(`manual_qc_review_confidence_bins_floor`, `manual_qc_review_confidence_entropy_floor`) 계산/보고 확인
- `smoke_v48_plan`: 신규 run preflight 통과(`selected_run_cells=2`, `selected_total_samples=1440`), prompt bank `v4.7` 고정 및 selection report(JSON/CSV) 생성
- `smoke_v48_exec`: subset 실행에서 `successful_cells=1`, `success_rate=0.5`, 셀 단위 wall-clock 상한(`--max-run-seconds`) 옵션 기록/동작 확인
