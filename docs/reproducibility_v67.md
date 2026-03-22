# Reproducibility Playbook v67

## 변경 요약
- screening 품질 게이트(리뷰 쿼리 집중도):
  - `--min-manual-qc-review-traceable-known-query-entropy`
  - `--max-manual-qc-review-traceable-known-query-top-share`
  - 목적: review traceability가 존재해도 특정 source_query 과집중을 조기 차단
- prompt bank: `v6.7`
  - 시나리오: `screening_review_query_concentration_relief`, `prompt_bank_countervoice_domain_parity`, `runner_runid_stage_imbalance_tripwire`
  - 페르소나: `review_query_diversity_curator`, `countervoice_domain_parity_designer`, `stage_imbalance_tripwire_operator`
- runner 예산 감사 산출물 추가:
  - `--budget-violations-json`
  - 목적: budget pressure threshold 위반 run-id를 기계가독 형태로 재현 가능하게 보존

## v67 screening QC 예시
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --run-label screening_qc_v67 \
  --min-manual-qc-review-traceable-known-query-entropy 0.45 \
  --max-manual-qc-review-traceable-known-query-top-share 0.70
```

## v67 preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v67_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_stage_imbalance_v67 \
  --require-prompt-bank-version v6.7 \
  --require-min-unique-scenario-labels 2 \
  --require-min-selected-scenario-labels 2 \
  --preflight-markdown \
  --print-selection
```

## v67 smoke 실행
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v67_exec \
  --include-run-id screening_prompt_runner_stage_imbalance_v67 \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 2 \
  --max-analysis-retries 1 \
  --max-stage-attempt-imbalance-ratio-per-run-id 2.0 \
  --budget-report-json results/experiments/smoke_v67_exec/budget_report.json \
  --budget-report-md results/experiments/smoke_v67_exec/budget_report.md \
  --budget-violations-json results/experiments/smoke_v67_exec/budget_violations.json \
  --manifest-markdown
```