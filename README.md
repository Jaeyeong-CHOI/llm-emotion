# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality gate now supports **review bridge+counterexample traceability gap 상한 점검**(`--max-review-bridge-counterexample-traceability-gap-share`)을 추가해, 핵심 반례가 있는데 근거 추적성이 비는 케이스를 조기에 차단합니다.
- Prompt bank expanded to `v5.9` with screening/prompt/runner 연계 시나리오 (`screening_bridge_counterexample_density_repair`, `prompt_bank_countervoice_calibration_grid`, `runner_stage_share_gap_throttle`) and personas (`review_density_auditor`, `stage_share_gap_controller`). Experiment matrix now includes `screening_prompt_runner_gap_v59`.
- Experiment runner now supports **run-id별 stage attempt share gap tripwire** (`--max-stage-attempt-share-gap-per-run-id`) to stop batches when 생성/분석 단계 점유율 격차가 과도하게 벌어집니다.
- Screening quality gate continues to track **review evidence-link decay share** (`--max-manual-qc-review-evidence-link-decay-share`) to fail fast when review 근거의 문장-링크 연결이 약화됩니다.
- Experiment runner budget report now includes **stage별 attempt pressure ratio** and tripwires (`--max-generation-attempt-over-selection-ratio`, `--max-analysis-attempt-over-selection-ratio`) to prevent 생성/분석 단계 예산 과열 편향.

## Repository structure
- `docs/`: review protocol, screening rubric, experiment plan, ops notes, reproducibility playbooks (`docs/reproducibility_v59.md`)
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-min-per-label 2 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v58 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-review-counterexample-traceability-share 0.55 --min-review-bridge-counterexample-coupled-share 0.18 --min-review-bridge-counterexample-traceable-share 0.12 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v58_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v58.json --selection-csv results/selection_report_smoke_v58.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 28 --require-min-run-ids 14 --require-min-total-samples 17000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 48 --require-min-selected-personas 36 --require-min-selected-scenario-tags 28 --require-min-selected-persona-style-tags 30 --require-prompt-bank-version v5.8 --max-selected-cell-share-per-run-id 0.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v58"
printf '%s\n' screening_prompt_runner_temporal_v58 > /tmp/llm_emotion_run_ids_v58_exec.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v58_exec --run-id-file /tmp/llm_emotion_run_ids_v58_exec.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --max-generation-attempts-per-run-id 3 --max-analysis-attempts-per-run-id 2 --max-attempts-per-cell 4 --max-selected-cell-share-per-run-id 1.0 --max-attempt-share-per-run-id 1.0 --max-attempt-over-selection-ratio 2.5 --max-failure-over-selection-ratio 2.0 --max-failed-cell-share-per-run-id 0.6 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --max-generation-failure-streak 1 --max-analysis-failure-streak 1 --max-generation-failure-streak-per-run-id 1 --max-analysis-failure-streak-per-run-id 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-successful-cells-per-run-id 1 --max-failure-streak-per-run-id 1 --execution-log-jsonl results/experiments/smoke_v58_exec/command_log.jsonl --quarantine-json results/experiments/smoke_v58_exec/quarantine_candidates.json --quarantine-csv results/experiments/smoke_v58_exec/quarantine_candidates.csv --budget-report-json results/experiments/smoke_v58_exec/budget_report.json --budget-report-md results/experiments/smoke_v58_exec/budget_report.md --require-min-total-samples 1000
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
- `--require-prompt-bank-version`으로 실행 전 prompt bank 버전 고정, `--require-freeze-artifact`로 필수 근거 파일 존재 여부를 강제해 evidence-freeze 누락을 fail-fast로 차단할 수 있습니다.
- `--require-min-selected-scenarios`와 `--require-min-selected-personas`로 배치 전체의 aggregate coverage floor를 강제해, 너무 좁은 실험 묶음이 통과하지 못하게 할 수 있습니다.
- `--run-id-file`로 배치 실행 대상을 파일 기반으로 고정하고, `--max-retries`/`--retry-backoff-seconds`로 부분 실패 복구 정책을 명시적으로 재현할 수 있습니다.
- `--max-selected-cell-share-per-run-id`, `--max-attempt-share-per-run-id`, `--max-attempt-over-selection-ratio`로 특정 run id가 selection 대비 과도한 retry budget을 소비할 때 즉시 중단할 수 있습니다.
