# Reproducibility Playbook v71

## 변경 요약
- **(1) 스크리닝 품질 게이트 강화**
  - `check_screening_quality.py`에 review-traceable known-query 분산 불균형 지표 추가
    - `manual_qc_review_traceable_known_query_bottom_share`
    - `manual_qc_review_traceable_known_query_top_bottom_gap`
  - 신규 CLI 옵션
    - `--max-manual-qc-review-traceable-known-query-top-bottom-gap`
- **(2) 프롬프트 뱅크 확장(v7.1)**
  - 신규 시나리오
    - `screening_review_query_counterexample_mix`
    - `prompt_bank_countervoice_query_tension`
    - `runner_live_retry_share_reallocation`
  - 신규 페르소나
    - `query_counterexample_balancer`
    - `retry_share_reallocator`
  - 신규 run id
    - `screening_prompt_runner_retry_share_v71`
- **(3) 실험 러너 고도화**
  - 단계별 시도 압력 통합 지표 추가
    - `stage_attempt_pressure_ratio = max(generation_attempt_over_selection_ratio, analysis_attempt_over_selection_ratio)`
  - 신규 CLI 옵션
    - `--max-stage-attempt-pressure-ratio-per-run-id`
  - budget report/markdown/manifest에 최대 stage attempt pressure 기록

## 검증 커맨드

### 1) 스크리닝 품질(v71)
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v71.json \
  --out-md results/screening_quality_report_v71.md \
  --run-label screening_qc_v71 \
  --max-manual-qc-review-traceable-known-query-top-share 0.7 \
  --max-manual-qc-review-traceable-known-query-top-bottom-gap 0.55 \
  --min-manual-qc-review-traceable-known-query-group-entropy 0.45
```

### 2) v71 preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v71_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_retry_share_v71 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v71.json \
  --selection-csv results/selection_report_smoke_v71.csv \
  --require-min-scenarios 4 \
  --require-min-personas 4 \
  --require-min-temperature-count 3 \
  --require-min-temperature-span 0.5 \
  --require-min-condition-cells 48 \
  --require-min-run-cells 1 \
  --require-min-run-ids 1 \
  --require-min-total-samples 1000 \
  --require-min-unique-scenario-labels 3 \
  --require-min-unique-scenario-tags 6 \
  --require-min-unique-persona-style-tags 8 \
  --require-prompt-bank-version v7.1 \
  --max-stage-attempt-pressure-ratio-per-run-id 1.2
```

## 이번 실행 결과
- `smoke_v71_plan` 통과
  - selected run cells: `1`
  - selected total samples: `1152`
  - prompt bank version: `v7.1`
- `screening_qc_v71`는 현재 데이터 기준 `status=review`(quality score 25.0)로, 신규 top-bottom gap을 포함한 수동 QC 분산 게이트가 실제로 실패를 드러내는지 확인됨
