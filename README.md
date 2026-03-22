# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality gate에 **review traceable known-query year top1 집중 가드**(`--max-manual-qc-review-traceable-known-query-year-top1-share`)를 추가해, year top2/tail/entropy 조건을 우회하는 단일 연도 과점을 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.5` with **year-tail+unknown-query coupling 복구 / countervoice temperature band rebalance / selected-temperature span guardrail** scenarios plus new personas (`year_query_tail_recovery_operator_v85`, `countervoice_temperature_calibrator_v85`, `temperature_span_tripwire_auditor_v85`).
- Experiment runner now supports **aggregate selected-temperature span guardrail** (`--require-min-selected-temperature-span`) so batch-level preflight에서 temperature 개수는 충분해도 span이 지나치게 좁은 실행을 사전에 차단할 수 있습니다.
- Literature screening quality gate에 **review traceable known-query year entropy/coverage 가드**(`--min-manual-qc-review-traceable-known-query-year-entropy`, `--min-manual-qc-review-traceable-known-query-year-coverage`)를 추가해, year top2/tail 비율이 통과하더라도 실질적인 연도 분산이 무너진 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.4` with **year-tail counterexample rebalance / unknown-query bridge rescue / countervoice year-grid patch / selected-temperature floor audit** scenarios plus new personas (`review_year_tail_recovery_curator_v84`, `unknown_query_traceability_operator_v84`, `countervoice_year_grid_curator_v84`, `selected_temperature_floor_guard_v84`).
- Experiment runner now supports **aggregate selected-temperature floor guardrail** (`--require-min-selected-temperatures`) so batch-level preflight에서 scenario/persona coverage는 충분해도 temperature 축이 과도하게 좁은 실행을 사전에 차단할 수 있습니다.
- Literature screening quality gate에 **review known-query source-group tail-share floor 가드**(`--min-manual-qc-review-traceable-known-query-group-tail-share`)를 추가해, source-group 상위 집중(top2) 완화 없이 겉보기 traceability만 상승하는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.0` with **source-group tail recovery drill / batch metadata floor audit** scenarios plus new personas (`group_tail_coverage_steward_v80`, `batch_metadata_floor_guard_v80`).
- Experiment runner now supports **batch-level aggregate metadata floor guardrails** (`--require-min-selected-scenario-domains`, `--require-min-selected-scenario-emotion-axes`, `--require-min-selected-scenario-difficulties`) to fail-fast when selected run-id 묶음이 전체 domain/axis/difficulty 커버리지를 충분히 확보하지 못할 때 실행을 중단합니다.
- Literature screening quality gate에 **review known-query source-group JS divergence 가드**(`--max-manual-qc-review-traceable-known-query-group-js-divergence`)를 추가해, review traceable 분포가 전체 manual QC source-group 분포에서 과도하게 벗어나는 경우를 fail-fast로 차단합니다.
- Prompt bank expanded to `v7.9` with **tail-query recovery tabletop / timeout budget rebalance postmortem** scenarios plus new personas (`query_tail_recovery_planner_v79`, `timeout_budget_foreman_v79`).
- Experiment runner now supports **timeout failure pressure guardrail** (`--max-timeout-failure-over-selection-ratio-per-run-id`) in addition to timeout share ceiling (`--max-timeout-failure-share-per-run-id`) to catch run-id-level timeout concentration against selected-cell share.
- Literature screening quality gate에 **duplicate-title / weak-evidence 가드**(`--max-manual-qc-duplicate-title-share`, `--max-review-weak-evidence-share`)를 추가해, manual QC 큐의 중복 잔존과 review 근거 희석을 기존 dedup/risk 지표와 분리해서 감시할 수 있습니다.
- Prompt bank expanded to `v7.7` with **tail-query / countervoice intensity-grid / metadata-tripwire prompts** (`screening_query_tail_cluster_leak`, `prompt_bank_countervoice_domain_intensity_grid`, `runner_resume_metadata_axis_tripwire`) plus new personas (`tail_query_recall_engineer`, `metadata_axis_safety_operator`).
- Experiment runner now supports **scenario domain/emotion entropy guardrails** (`--require-min-scenario-domain-entropy`, `--require-min-scenario-emotion-axis-entropy`) in addition to label entropy; experiment matrix now includes `screening_prompt_runner_metadata_entropy_v77`.
- Literature screening quality gate에 **review known-query group top2 과점 가드**(`--max-manual-qc-review-traceable-known-query-group-top2-share`)를 추가해, source group 분포가 1~2개 그룹에 몰리면서 query 다양성 복구가 지연되는 패턴을 fail-fast로 차단할 수 있습니다.
- Literature screening quality gate에 **review known-query 하단 분포 가드**(`--min-manual-qc-review-traceable-known-query-bottom2-share`)를 추가해 top query 쏠림만 보는 것이 아니라 tail 복구 여지를 수치로 점검할 수 있습니다.
- Literature screening quality gate now supports **review bridge-query coupling gates** (`--min-review-bridge-traceable-known-query-share`, `--max-review-bridge-traceable-unknown-query-share`) to catch cases where bridge evidence exists but query provenance remains weak.
- Literature screening quality gate expanded with **review known-query concentration checks** (`--min-manual-qc-review-traceable-known-query-entropy`, `--max-manual-qc-review-traceable-known-query-top-share`) to catch review queues that look traceable but still overfit to a narrow query slice.
- Prompt bank expanded to `v7.5` with **review bridge unknown-query 복구 / countervoice 회전 공백 패치 / label entropy tripwire** additions (`screening_review_bridge_unknown_query_repair`, `prompt_bank_countervoice_rotation_gap_patch`, `runner_scenario_label_entropy_tripwire`) plus new personas (`review_query_traceability_triager`, `countervoice_rotation_architect`, `label_entropy_tripwire_operator`). Experiment matrix now includes `screening_prompt_runner_entropy_bridge_v75`.
- Prompt bank expanded to `v7.4` with **tail-query rescue / countervoice gap backfill / stage quota recovery** additions (`screening_tail_query_rescue_drill`, `prompt_bank_countervoice_gap_backfill_sprint`, `runner_stage_budget_quota_recovery`) plus new personas (`tail_query_balance_warden`, `countervoice_gap_repairer`, `stage_quota_rebalancer`). Experiment matrix now includes `screening_prompt_runner_tail_quota_v74`.
- Experiment runner now supports **scenario label entropy floor guardrail** (`--require-min-scenario-label-entropy`) in addition to label dominance guardrail (`--require-max-scenario-label-dominance`), so preflight can fail-fast when label count는 충분해도 분포가 실질적으로 편중된 배치가 선택됩니다.
- Experiment runner continues to support **live run-id attempt share tripwires** (`--max-live-generation-attempt-share-per-run-id`, `--max-live-analysis-attempt-share-per-run-id`, `--max-live-combined-attempt-share-per-run-id`) plus post-run budget pressure reports.
- Screening quality gate continues to track **review evidence-link decay share** (`--max-manual-qc-review-evidence-link-decay-share`) to fail fast when review 근거의 문장-링크 연결이 약화됩니다.

## Repository structure
- `docs/`: review protocol, screening rubric, experiment plan, ops notes, reproducibility playbooks (`docs/reproducibility_v80.md`)
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-min-per-label 2 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v82 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-review-counterexample-traceability-share 0.55 --min-review-bridge-counterexample-coupled-share 0.18 --min-review-bridge-counterexample-traceable-share 0.12 --min-review-bridge-counterexample-traceability-given-coupled-share 0.55 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-review-query-entropy 0.45 --min-manual-qc-review-traceable-known-query-share 0.55 --max-manual-qc-review-traceable-unknown-query-share 0.15 --min-manual-qc-review-query-traceability-share 0.75 --min-manual-qc-review-traceable-known-query-entropy 0.45 --max-manual-qc-review-traceable-known-query-top-share 0.70 --min-manual-qc-review-traceable-known-query-group-entropy 0.45 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-manual-qc-dedup-label-conflict-share 0.20 --min-dedup-score-range-alert 1.0 --max-manual-qc-dedup-score-range-alert-share 0.20 --max-manual-qc-duplicate-title-share 0.20 --max-review-weak-evidence-share 0.40 --max-empty-screening-reason-share 0.10 --max-review-counterexample-without-bridge-share 0.35
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v82_plan --plan-only --include-run-id screening_prompt_runner_entropy_tail_v81 --include-run-id screening_prompt_runner_year_budget_v82 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v82.json --selection-csv results/selection_report_smoke_v82.csv --preflight-markdown --require-min-scenarios 3 --require-min-personas 4 --require-min-temperature-count 3 --require-min-condition-cells 27 --require-min-total-samples 1600 --require-min-planned-samples-per-run 800 --require-min-unique-scenario-labels 2 --require-min-unique-scenario-tags 10 --require-min-unique-scenario-domains 3 --require-min-unique-scenario-emotion-axes 3 --require-min-unique-scenario-difficulties 1 --require-min-unique-persona-style-tags 12 --require-prompt-bank-version v8.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.20 --manifest-note "preflight v82 year-drift + planned-sample-share guard"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v82_exec --include-run-id screening_prompt_runner_year_budget_v82 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --execution-log-jsonl results/experiments/smoke_v82_exec/command_log.jsonl --budget-report-json results/experiments/smoke_v82_exec/budget_report.json --budget-report-md results/experiments/smoke_v82_exec/budget_report.md --require-min-total-samples 400
```

## Prompt-bank filtering
`scripts/generate_dataset.py` supports reproducible subset selection:

```bash
python3 scripts/generate_dataset.py \
  --out /tmp/mock.jsonl \
  --prompt-bank prompts/prompt_bank_ko.json \
  --scenario-domains research_ops \
  --scenario-emotion-axes regret \
  --scenario-difficulties hard \
  --persona-ids regretful,self_compassionate
```

## Experiment reproducibility
- Run definitions live in `ops/experiment_matrix.json`

### v8.5 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v85 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v85_plan --plan-only --include-run-id screening_prompt_runner_year_unknown_temp_v84 --include-run-id screening_prompt_runner_year_query_temp_span_v85 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v85.json --selection-csv results/selection_report_smoke_v85.csv --preflight-markdown --require-prompt-bank-version v8.5 --require-min-selected-temperatures 3 --require-min-selected-temperature-span 0.7 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v85 year-top1 + selected-temperature-span guard"
```

### v8.4 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v84 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v84_plan --plan-only --include-run-id screening_prompt_runner_year_tail_pressure_v83 --include-run-id screening_prompt_runner_year_unknown_temp_v84 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v84.json --selection-csv results/selection_report_smoke_v84.csv --preflight-markdown --require-prompt-bank-version v8.4 --require-min-selected-temperatures 3 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v84 year-entropy + unknown-query + temperature-floor guard"
```

### v8.3 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v83 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v83_plan --plan-only --include-run-id screening_prompt_runner_year_budget_v82 --include-run-id screening_prompt_runner_year_tail_pressure_v83 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v83.json --selection-csv results/selection_report_smoke_v83.csv --preflight-markdown --require-prompt-bank-version v8.3 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.20 --max-planned-sample-over-selection-ratio-per-run-id 1.20 --manifest-note "preflight v83 year-tail + planned-sample-pressure guard"
```

### v8.2 스모크 프리플라이트 (2026-03-22)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v82 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v82_plan --plan-only --include-run-id screening_prompt_runner_entropy_tail_v81 --include-run-id screening_prompt_runner_year_budget_v82 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v82.json --selection-csv results/selection_report_smoke_v82.csv --preflight-markdown --require-prompt-bank-version v8.2 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.20 --manifest-note "preflight v82 year-budget"
```
- `results/experiments/<label>/manifest.json` records environment and cell status
- `results/experiments/<label>/snapshots/` stores the config and prompt-bank snapshots used for the batch
- `results/experiments/<label>/preflight.json` and `preflight.csv` capture selection/preflight diagnostics for review before or after execution
- `results/experiments/<label>/command_log.jsonl` records each command attempt with timestamps, return code, stdout, and stderr when execution occurs
- `results/experiments/<label>/budget_report.json` and `budget_report.md` summarize selected-cell share, generation/analysis attempt share, attempt-pressure ratio, and failed-cell concentration by run id
- `results/experiments/<label>/budget_violations.json` stores machine-readable threshold violations (rule, threshold, violating run ids) for reproducible audits
- `--require-prompt-bank-version`으로 실행 전 prompt bank 버전 고정, `--require-freeze-artifact`로 필수 근거 파일 존재 여부를 강제해 evidence-freeze 누락을 fail-fast로 차단할 수 있습니다.
- `--scenario-domains`, `--scenario-emotion-axes`, `--scenario-difficulties`로 prompt bank 메타데이터 축을 선택 조건에 넣고, 동일 축이 생성 데이터셋/selection/preflight 산출물에도 함께 기록됩니다.
- `--require-min-selected-scenarios`, `--require-min-selected-personas`, `--require-min-selected-scenario-labels`로 배치 전체의 aggregate coverage floor를 강제해, scenario 수는 많아도 label 축이 편향된 실험 묶음이 통과하지 못하게 할 수 있습니다.
- `--max-planned-sample-share-per-run-id`, `--max-planned-sample-share-gap-per-run-id`로 run-id별 `n × condition_cells × repeats` 예산 편중을 preflight에서 차단해, selected cell 수는 비슷하지만 실제 샘플 예산이 한 run id에 몰리는 배치를 막을 수 있습니다.
- `--run-id-file`로 배치 실행 대상을 파일 기반으로 고정하고, `--max-retries`/`--retry-backoff-seconds`로 부분 실패 복구 정책을 명시적으로 재현할 수 있습니다.
- `--max-selected-cell-share-per-run-id`, `--max-attempt-share-per-run-id`, `--max-attempt-over-selection-ratio`로 특정 run id가 selection 대비 과도한 retry budget을 소비할 때 즉시 중단할 수 있습니다.
