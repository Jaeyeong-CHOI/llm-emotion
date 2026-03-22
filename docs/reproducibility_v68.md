# Reproducibility Playbook v68

## 변경 요약
- **선행연구 스크리닝 품질 게이트 강화**
  - `check_screening_quality.py`에 review traceable known-query 집중도 지표 추가
    - `manual_qc_review_traceable_known_query_coverage`
    - `manual_qc_review_traceable_known_query_hhi`
  - 신규 CLI 옵션
    - `--min-manual-qc-review-traceable-known-query-coverage`
    - `--max-manual-qc-review-traceable-known-query-hhi`
- **프롬프트 뱅크 v6.8 확장**
  - 신규 시나리오
    - `screening_review_query_cluster_floor`
    - `prompt_bank_countervoice_intensity_band`
    - `runner_stage_retry_mix_guard`
  - 신규 페르소나
    - `review_query_cluster_guard`
    - `countervoice_intensity_curator`
    - `stage_retry_mix_operator`
- **실험 러너 고도화**
  - 단계별 재시도 점유율 상한 옵션 추가
    - `--max-generation-retry-share-per-run-id`
    - `--max-analysis-retry-share-per-run-id`
  - run-id별 재시도 편중이 임계치를 넘으면 budget violation으로 즉시 실패 처리

## 재현 커맨드

### 1) 스크리닝 품질 체크(v68)
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v68 \
  --min-manual-qc-review-traceable-known-query-coverage 3 \
  --max-manual-qc-review-traceable-known-query-hhi 0.35
```

### 2) v68 run-id preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v68_plan \
  --plan-only --print-selection \
  --selection-report results/selection_report_smoke_v68.json \
  --selection-csv results/selection_report_smoke_v68.csv \
  --run-id-file /tmp/llm_emotion_run_ids_v68_exec.txt \
  --require-prompt-bank-version v6.8
```

### 3) v68 실행(단계별 재시도 점유율 가드 포함)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v68_exec \
  --run-id-file /tmp/llm_emotion_run_ids_v68_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 2 \
  --max-analysis-retries 0 \
  --continue-on-error \
  --max-generation-retry-share-per-run-id 0.8 \
  --max-analysis-retry-share-per-run-id 0.8
```
