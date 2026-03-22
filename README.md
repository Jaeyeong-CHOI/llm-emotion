# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality gate now adds **manual QC 연도 분산 점검**(`--min-manual-qc-year-diversity`, `--max-manual-qc-single-year-share`, `--min-manual-qc-year-entropy`) so 특정 연도 논문에 과집중된 검토 큐를 조기에 탐지할 수 있습니다.
- Prompt bank expanded to `v4.4` with precision/recall pivot, antithesis-rotation debt, and stage-quarantine failover scenarios (`screening_precision_recall_pivot_debt`, `prompt_bank_antithesis_rotation_debt`, `runner_stage_quarantine_failover`) plus new personas (`screening_precision_recall_negotiator`, `antithesis_rotation_curator`, `stage_quarantine_supervisor`). Experiment matrix now includes `screening_prompt_runner_quarantine_v45`.
- Experiment runner now supports **run-id별 실패 격리 상한**(`--max-failed-cells-per-run-id`) so 반복 실패가 한 run-id에 집중될 때 남은 반복 셀을 스킵하고 배치 전체 전염을 줄일 수 있습니다.

## Repository structure
- `docs/`: review protocol, screening rubric, experiment plan, ops notes
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-min-per-label 2 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v44 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-source-groups 3 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v44_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v43.json --selection-csv results/selection_report_smoke_v43.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 18 --require-min-run-ids 9 --require-min-total-samples 12000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 31 --require-min-selected-personas 24 --require-min-selected-scenario-tags 18 --require-min-selected-persona-style-tags 19 --require-prompt-bank-version v4.3 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v42"
printf '%s\n' screening_prompt_replay_v36 screening_prompt_runner_hardening_v37 screening_prompt_runner_resilience_v38 screening_prompt_runner_autonomy_v39 screening_prompt_runner_reliability_v40 screening_prompt_runner_stagewise_v41 screening_prompt_runner_timeout_v42 screening_prompt_runner_multilingual_v44 > /tmp/llm_emotion_run_ids_v44.txt
printf '%s\n' screening_prompt_runner_multilingual_v44 > /tmp/llm_emotion_run_ids_v44_exec.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v44_exec --run-id-file /tmp/llm_emotion_run_ids_v44_exec.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --execution-log-jsonl results/experiments/smoke_v44_exec/command_log.jsonl --require-min-total-samples 1000
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
- `--require-prompt-bank-version`으로 실행 전 prompt bank 버전 고정, `--require-freeze-artifact`로 필수 근거 파일 존재 여부를 강제해 evidence-freeze 누락을 fail-fast로 차단할 수 있습니다.
- `--require-min-selected-scenarios`와 `--require-min-selected-personas`로 배치 전체의 aggregate coverage floor를 강제해, 너무 좁은 실험 묶음이 통과하지 못하게 할 수 있습니다.
- `--run-id-file`로 배치 실행 대상을 파일 기반으로 고정하고, `--max-retries`/`--retry-backoff-seconds`로 부분 실패 복구 정책을 명시적으로 재현할 수 있습니다.
