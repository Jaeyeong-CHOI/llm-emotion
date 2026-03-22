# Reproducibility Note v78

- focus: screening known-query 분포 이탈(JS divergence) 감시 + prompt bank v7.8 확장 + runner timeout 집중도 가드
- new run id: `screening_prompt_runner_timeout_focus_v78`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - 신규 지표: `manual_qc_review_traceable_known_query_js_divergence`
   - 신규 게이트 인자: `--max-manual-qc-review-traceable-known-query-js-divergence` (default `0.35`)
2. `prompts/prompt_bank_ko.json`
   - version `v7.8`
   - scenarios 3종 추가
   - personas 3종 추가
3. `scripts/run_experiments.py`
   - 신규 budget gate: `--max-timeout-failure-share-per-run-id`
   - run-id별 timeout 실패 집중도가 임계치를 넘으면 배치 실패 처리
4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_timeout_focus_v78`

## 재현 커맨드 (smoke)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v78 \
  --max-manual-qc-review-traceable-known-query-js-divergence 0.35

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v78_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_timeout_focus_v78 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v78.json \
  --selection-csv results/selection_report_smoke_v78.csv \
  --require-prompt-bank-version v7.8

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v78_exec \
  --include-run-id screening_prompt_runner_timeout_focus_v78 \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 1 \
  --max-analysis-retries 0 \
  --generation-timeout-seconds 120 \
  --analysis-timeout-seconds 90 \
  --continue-on-error \
  --max-timeout-failure-share-per-run-id 0.9
```
