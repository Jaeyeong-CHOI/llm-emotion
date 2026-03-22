# Reproducibility Playbook v69

## 변경 요약
- **선행연구 스크리닝 품질 게이트 강화**
  - `check_screening_quality.py`에 review traceable known-query의 **group entropy** 지표 추가
    - `manual_qc_review_traceable_known_query_group_entropy`
  - 신규 CLI 옵션
    - `--min-manual-qc-review-traceable-known-query-group-entropy`
- **프롬프트 뱅크 v6.9 확장**
  - 신규 시나리오
    - `screening_query_cluster_counterexample_sweep`
    - `prompt_bank_countervoice_ladder_audit`
    - `runner_live_stage_gap_recovery_drill`
  - 신규 페르소나
    - `query_cluster_diversity_guard`
    - `countervoice_ladder_calibrator`
    - `live_stage_gap_sentinel`
  - 신규 실험 매트릭스 run id
    - `screening_prompt_runner_live_stage_gap_v69`
- **실험 러너 고도화**
  - 실시간 단계 점유율 격차 tripwire 옵션 추가
    - `--max-live-stage-attempt-share-gap-per-run-id`
  - 실행 중 `abs(live_generation_attempt_share - live_analysis_attempt_share)`가 상한을 넘으면 즉시 중단해 stage imbalance 확산을 차단

## 재현 커맨드

### 1) 스크리닝 품질 체크(v69)
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v69 \
  --min-manual-qc-review-traceable-known-query-coverage 3 \
  --max-manual-qc-review-traceable-known-query-hhi 0.35 \
  --min-manual-qc-review-traceable-known-query-group-entropy 0.45
```

### 2) v69 run-id preflight
```bash
printf '%s\n' screening_prompt_runner_live_stage_gap_v69 > /tmp/llm_emotion_run_ids_v69_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v69_plan \
  --plan-only --print-selection \
  --selection-report results/selection_report_smoke_v69.json \
  --selection-csv results/selection_report_smoke_v69.csv \
  --run-id-file /tmp/llm_emotion_run_ids_v69_exec.txt \
  --require-prompt-bank-version v6.9
```

### 3) v69 실행(live stage-gap tripwire 포함)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v69_exec \
  --run-id-file /tmp/llm_emotion_run_ids_v69_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 2 \
  --max-analysis-retries 0 \
  --continue-on-error \
  --max-live-generation-attempt-share-per-run-id 0.9 \
  --max-live-analysis-attempt-share-per-run-id 0.9 \
  --max-live-combined-attempt-share-per-run-id 0.9 \
  --max-live-stage-attempt-share-gap-per-run-id 0.35
```
