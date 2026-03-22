# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality gate now adds screening-reason dispersion checks (`--min-screening-reason-diversity`, `--max-top-screening-reason-share`) so manual QC가 특정 판단 근거로 과집중되는 드리프트를 더 빨리 탐지합니다.
- Prompt bank expanded to `v4.0` with active-learning recall rescue / counterexample blindspot / stagewise retry backpressure scenarios (`screening_active_learning_misprioritization`, `prompt_bank_counterexample_blindspot`, `runner_stagewise_retry_backpressure`) and personas (`screening_recall_optimizer`, `stagewise_retry_engineer`). Experiment matrix now includes `screening_prompt_runner_stagewise_v41`.
- Experiment runner now supports stage-specific retry budgets (`--max-generation-retries`, `--max-analysis-retries`) and per-run-id success floor (`--require-min-run-id-success-rate`) so 배치 전체 통과율뿐 아니라 run-id 단위 안정성까지 gate로 관리할 수 있습니다.

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
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v41 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v41_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v41.json --selection-csv results/selection_report_smoke_v41.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 16 --require-min-run-ids 8 --require-min-total-samples 11000 --require-min-planned-samples-per-run 1100 --require-min-selected-scenarios 28 --require-min-selected-personas 21 --require-min-selected-scenario-tags 17 --require-min-selected-persona-style-tags 18 --require-prompt-bank-version v4.0 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v41"
printf '%s\n' screening_precision_rebalance_v35 prompt_runner_resilience_v35 screening_prompt_replay_v36 screening_prompt_runner_hardening_v37 screening_prompt_runner_resilience_v38 screening_prompt_runner_autonomy_v39 screening_prompt_runner_reliability_v40 screening_prompt_runner_stagewise_v41 > /tmp/llm_emotion_run_ids_v41.txt
printf '%s\n' screening_prompt_runner_stagewise_v41 > /tmp/llm_emotion_run_ids_v41_exec.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v41_exec --run-id-file /tmp/llm_emotion_run_ids_v41_exec.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 2 --max-analysis-retries 0 --retry-backoff-seconds 1 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --execution-log-jsonl results/experiments/smoke_v41_exec/command_log.jsonl --require-min-total-samples 1000
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
