# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
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
- `docs/`: review protocol, screening rubric, experiment plan, ops notes, reproducibility playbooks (`docs/reproducibility_v69.md`)
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-min-per-label 2 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v69 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-review-counterexample-traceability-share 0.55 --min-review-bridge-counterexample-coupled-share 0.18 --min-review-bridge-counterexample-traceable-share 0.12 --min-review-bridge-counterexample-traceability-given-coupled-share 0.55 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-review-query-entropy 0.45 --min-manual-qc-review-traceable-known-query-share 0.55 --max-manual-qc-review-traceable-unknown-query-share 0.15 --min-manual-qc-review-query-traceability-share 0.75 --min-manual-qc-review-traceable-known-query-entropy 0.45 --max-manual-qc-review-traceable-known-query-top-share 0.70 --min-manual-qc-review-traceable-known-query-group-entropy 0.45 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-manual-qc-dedup-label-conflict-share 0.20 --min-dedup-score-range-alert 1.0 --max-manual-qc-dedup-score-range-alert-share 0.20 --max-empty-screening-reason-share 0.10 --max-review-counterexample-without-bridge-share 0.35
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v69_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v69.json --selection-csv results/selection_report_smoke_v69.csv --require-min-scenarios 3 --require-min-personas 4 --require-min-unique-scenario-labels 2 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 36 --require-min-run-cells 30 --require-min-run-ids 16 --require-min-total-samples 19000 --require-min-planned-samples-per-run 1080 --require-min-selected-scenarios 53 --require-min-selected-personas 41 --require-min-selected-scenario-labels 8 --require-min-selected-scenario-tags 31 --require-min-selected-persona-style-tags 34 --require-prompt-bank-version v6.9 --max-selected-cell-share-per-run-id 0.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v65"
printf '%s\n' screening_prompt_runner_live_stage_gap_v69 > /tmp/llm_emotion_run_ids_v69_exec.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v69_exec --run-id-file /tmp/llm_emotion_run_ids_v69_exec.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --max-generation-attempts-per-run-id 3 --max-analysis-attempts-per-run-id 2 --max-attempts-per-cell 4 --max-selected-cell-share-per-run-id 1.0 --max-attempt-share-per-run-id 1.0 --max-generation-attempt-share-per-run-id 1.0 --max-analysis-attempt-share-per-run-id 1.0 --max-live-generation-attempt-share-per-run-id 0.9 --max-live-analysis-attempt-share-per-run-id 0.9 --max-live-combined-attempt-share-per-run-id 0.9 --max-live-stage-attempt-share-gap-per-run-id 0.35 --max-attempt-over-selection-ratio 2.5 --max-retry-share-per-run-id 1.0 --max-retry-over-selection-ratio 2.2 --max-failure-over-selection-ratio 2.0 --max-failed-cell-share-per-run-id 0.6 --max-stage-attempt-imbalance-ratio-per-run-id 2.0 --max-stage-total-attempt-imbalance-ratio 1.8 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --max-generation-failure-streak 1 --max-analysis-failure-streak 1 --max-generation-failure-streak-per-run-id 1 --max-analysis-failure-streak-per-run-id 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-successful-cells-per-run-id 1 --max-failure-streak-per-run-id 1 --execution-log-jsonl results/experiments/smoke_v69_exec/command_log.jsonl --quarantine-json results/experiments/smoke_v69_exec/quarantine_candidates.json --quarantine-csv results/experiments/smoke_v69_exec/quarantine_candidates.csv --budget-report-json results/experiments/smoke_v69_exec/budget_report.json --budget-report-md results/experiments/smoke_v69_exec/budget_report.md --budget-violations-json results/experiments/smoke_v69_exec/budget_violations.json --require-min-total-samples 1000
```

## Prompt-bank filtering
`scripts/generate_dataset.py` supports reproducible subset selection:

```bash
python3 scripts/generate_dataset.py \
  --out /tmp/mock.jsonl \
  --prompt-bank prompts/prompt_bank_ko.json \
  --scenario-tags counterfactual \
  --persona-ids regretful,self_compassionate
```

## Experiment reproducibility
- Run definitions live in `ops/experiment_matrix.json`
- `results/experiments/<label>/manifest.json` records environment and cell status
- `results/experiments/<label>/snapshots/` stores the config and prompt-bank snapshots used for the batch
- `results/experiments/<label>/preflight.json` and `preflight.csv` capture selection/preflight diagnostics for review before or after execution
- `results/experiments/<label>/command_log.jsonl` records each command attempt with timestamps, return code, stdout, and stderr when execution occurs
- `results/experiments/<label>/budget_report.json` and `budget_report.md` summarize selected-cell share, generation/analysis attempt share, attempt-pressure ratio, and failed-cell concentration by run id
- `results/experiments/<label>/budget_violations.json` stores machine-readable threshold violations (rule, threshold, violating run ids) for reproducible audits
- `--require-prompt-bank-version`으로 실행 전 prompt bank 버전 고정, `--require-freeze-artifact`로 필수 근거 파일 존재 여부를 강제해 evidence-freeze 누락을 fail-fast로 차단할 수 있습니다.
- `--require-min-selected-scenarios`, `--require-min-selected-personas`, `--require-min-selected-scenario-labels`로 배치 전체의 aggregate coverage floor를 강제해, scenario 수는 많아도 label 축이 편향된 실험 묶음이 통과하지 못하게 할 수 있습니다.
- `--run-id-file`로 배치 실행 대상을 파일 기반으로 고정하고, `--max-retries`/`--retry-backoff-seconds`로 부분 실패 복구 정책을 명시적으로 재현할 수 있습니다.
- `--max-selected-cell-share-per-run-id`, `--max-attempt-share-per-run-id`, `--max-attempt-over-selection-ratio`로 특정 run id가 selection 대비 과도한 retry budget을 소비할 때 즉시 중단할 수 있습니다.
