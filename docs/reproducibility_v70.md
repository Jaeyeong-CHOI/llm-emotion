# Reproducibility Playbook v70

## 변경 요약
- **선행연구 스크리닝 품질 게이트 강화**
  - `check_screening_quality.py`에 review traceable known-query의 source group 편중 감시 지표 추가
    - `manual_qc_review_traceable_known_query_group_coverage`
    - `manual_qc_review_traceable_known_query_group_top_share`
  - 신규 CLI 옵션
    - `--min-manual-qc-review-traceable-known-query-group-coverage`
    - `--max-manual-qc-review-traceable-known-query-group-top-share`
- **프롬프트 뱅크 v7.0 확장**
  - 신규 시나리오
    - `screening_query_bridge_counterbalance_repair`
    - `prompt_bank_countervoice_gap_matrix_patch`
    - `runner_live_retry_pressure_circuit_breaker`
  - 신규 페르소나
    - `review_counterbalance_auditor`
    - `countervoice_matrix_curator`
    - `live_retry_pressure_sentinel`
  - 신규 실험 매트릭스 run id
    - `screening_prompt_runner_retry_tripwire_v70`
- **실험 러너 고도화**
  - 실시간 retry 점유율 tripwire 옵션 추가
    - `--max-live-retry-share-per-run-id`
  - 실행 중 특정 run-id가 전체 retry를 과점하면 즉시 중단하여 budget pressure 확산을 차단

## 재현 커맨드

### 1) 스크리닝 품질 체크(v70)
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v70 \
  --min-manual-qc-review-traceable-known-query-group-entropy 0.45 \
  --min-manual-qc-review-traceable-known-query-group-coverage 2 \
  --max-manual-qc-review-traceable-known-query-group-top-share 0.75
```

### 2) v70 run-id preflight
```bash
printf '%s\n' screening_prompt_runner_retry_tripwire_v70 > /tmp/llm_emotion_run_ids_v70_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v70_plan \
  --plan-only --print-selection \
  --selection-report results/selection_report_smoke_v70.json \
  --selection-csv results/selection_report_smoke_v70.csv \
  --run-id-file /tmp/llm_emotion_run_ids_v70_exec.txt \
  --require-prompt-bank-version v7.0
```

### 3) v70 실행(live retry-share tripwire 포함)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v70_exec \
  --run-id-file /tmp/llm_emotion_run_ids_v70_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 2 \
  --max-analysis-retries 1 \
  --continue-on-error \
  --max-live-generation-attempt-share-per-run-id 0.9 \
  --max-live-analysis-attempt-share-per-run-id 0.9 \
  --max-live-combined-attempt-share-per-run-id 0.9 \
  --max-live-stage-attempt-share-gap-per-run-id 0.35 \
  --max-live-retry-share-per-run-id 0.7
```
