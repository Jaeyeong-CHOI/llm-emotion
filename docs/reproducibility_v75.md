# Reproducibility Playbook v75

## 변경 요약
- **(1) 스크리닝 품질 게이트 강화**
  - `check_screening_quality.py`에 review traceable known-query **group top2 과점 점검 지표** 추가
    - `manual_qc_review_traceable_known_query_group_top2_share`
  - 신규 CLI 옵션
    - `--max-manual-qc-review-traceable-known-query-group-top2-share`
  - query 분포가 괜찮아 보여도 source group이 상위 2개에 과점되면 fail-fast로 차단하도록 확장
- **(2) 프롬프트 뱅크 확장(v7.5)**
  - 신규 시나리오
    - `screening_review_bridge_unknown_query_repair`
    - `prompt_bank_countervoice_rotation_gap_patch`
    - `runner_scenario_label_entropy_tripwire`
  - 신규 페르소나
    - `review_query_traceability_triager`
    - `countervoice_rotation_architect`
    - `label_entropy_tripwire_operator`
  - 신규 run id
    - `screening_prompt_runner_entropy_bridge_v75`
- **(3) 실험 러너 고도화**
  - preflight에서 scenario label 편중을 차단하는 guardrail 추가
    - `--require-max-scenario-label-dominance`
  - run 별 scenario label 분포가 과점되면 실행 전 fail-fast 가능

## 검증 커맨드

### 1) 스크리닝 품질(v75)
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v75.json \
  --out-md results/screening_quality_report_v75.md \
  --run-label screening_qc_v75 \
  --max-manual-qc-review-traceable-known-query-top2-share 0.9 \
  --min-manual-qc-review-traceable-known-query-tail-share 0.15 \
  --min-manual-qc-review-traceable-known-query-bottom2-share 0.08 \
  --max-manual-qc-review-traceable-known-query-group-top2-share 0.9
```

### 2) v75 preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v75_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_entropy_bridge_v75 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v75.json \
  --selection-csv results/selection_report_smoke_v75.csv \
  --require-min-scenarios 4 \
  --require-min-personas 4 \
  --require-min-temperature-count 3 \
  --require-min-temperature-span 0.5 \
  --require-min-condition-cells 48 \
  --require-min-run-cells 1 \
  --require-min-run-ids 1 \
  --require-min-total-samples 1000 \
  --require-min-unique-scenario-labels 3 \
  --require-max-scenario-label-dominance 0.55 \
  --require-min-scenario-label-entropy 0.75 \
  --require-min-unique-scenario-tags 6 \
  --require-min-unique-persona-style-tags 8 \
  --require-prompt-bank-version v7.5
```

### 3) v75 smoke exec (1 cell)
```bash
printf '%s\n' screening_prompt_runner_entropy_bridge_v75 > /tmp/llm_emotion_run_ids_v75_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v75_exec \
  --run-id-file /tmp/llm_emotion_run_ids_v75_exec.txt \
  --fail-on-missing-run-id \
  --manifest-markdown \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 2 \
  --max-analysis-retries 0 \
  --max-generation-attempts-per-run-id 3 \
  --max-analysis-attempts-per-run-id 2 \
  --max-attempts-per-cell 4 \
  --max-selected-cell-share-per-run-id 1.0 \
  --max-attempt-share-per-run-id 1.0 \
  --max-generation-attempt-share-per-run-id 1.0 \
  --max-analysis-attempt-share-per-run-id 1.0 \
  --max-live-generation-attempt-share-per-run-id 1.0 \
  --max-live-analysis-attempt-share-per-run-id 1.0 \
  --max-live-combined-attempt-share-per-run-id 1.0 \
  --max-live-stage-attempt-share-gap-per-run-id 1.0 \
  --max-live-retry-over-selection-ratio-per-run-id 4.0 \
  --max-live-attempt-over-selection-ratio-per-run-id 4.0 \
  --max-attempt-over-selection-ratio 2.5 \
  --max-retry-share-per-run-id 1.0 \
  --max-retry-over-selection-ratio 2.2 \
  --max-failure-over-selection-ratio 2.0 \
  --max-failed-cell-share-per-run-id 0.6 \
  --max-stage-attempt-imbalance-ratio-per-run-id 2.0 \
  --max-stage-total-attempt-imbalance-ratio 1.8 \
  --require-max-scenario-label-dominance 0.55 \
  --require-min-scenario-label-entropy 0.75 \
  --require-min-generation-success-rate 0.8 \
  --require-min-analysis-success-rate 0.8 \
  --retry-backoff-seconds 1 \
  --generation-timeout-seconds 120 \
  --analysis-timeout-seconds 90 \
  --max-run-seconds 180 \
  --continue-on-error \
  --max-failed-cells 1 \
  --max-failure-rate 0.5 \
  --max-failure-streak 1 \
  --max-generation-failure-streak 1 \
  --max-analysis-failure-streak 1 \
  --max-generation-failure-streak-per-run-id 1 \
  --max-analysis-failure-streak-per-run-id 1 \
  --require-min-successful-cells 1 \
  --require-min-success-rate 0.4 \
  --require-min-run-id-success-rate 0.4 \
  --require-min-successful-cells-per-run-id 1 \
  --max-failure-streak-per-run-id 1 \
  --execution-log-jsonl results/experiments/smoke_v75_exec/command_log.jsonl \
  --quarantine-json results/experiments/smoke_v75_exec/quarantine_candidates.json \
  --quarantine-csv results/experiments/smoke_v75_exec/quarantine_candidates.csv \
  --budget-report-json results/experiments/smoke_v75_exec/budget_report.json \
  --budget-report-md results/experiments/smoke_v75_exec/budget_report.md \
  --budget-violations-json results/experiments/smoke_v75_exec/budget_violations.json \
  --require-min-total-samples 1000
```

## 이번 실행 결과
- `screening_qc_v75`: `status=review`, `quality_score=25.0`, `fail_count=5`
- `smoke_v75_plan` 통과
  - selected run cells: `1`
  - selected total samples: `1152`
  - prompt bank version: `v7.5`
- `smoke_v75_exec` 통과
  - executed: `1/1`
  - successful cells: `1`
  - success rate: `1.0`
