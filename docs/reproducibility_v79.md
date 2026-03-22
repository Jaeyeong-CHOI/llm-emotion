# Reproducibility Note v79

- focus: screening source-group drift(JS divergence) 강화 + prompt bank v7.9 확장 + runner timeout pressure guard
- new run id: `screening_prompt_runner_tail_timeout_v79`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - 신규 지표: `manual_qc_review_traceable_known_query_group_js_divergence`
   - 신규 게이트 인자: `--max-manual-qc-review-traceable-known-query-group-js-divergence` (default `0.35`)
2. `prompts/prompt_bank_ko.json`
   - version `v7.9`
   - scenarios 2종 추가
   - personas 2종 추가
3. `scripts/run_experiments.py`
   - 신규 budget gate: `--max-timeout-failure-over-selection-ratio-per-run-id`
   - timeout failure share만 보지 않고 selected-cell share 대비 압박 비율까지 실패 조건으로 점검
4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_tail_timeout_v79`

## 재현 커맨드 (smoke)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v79 \
  --max-manual-qc-review-traceable-known-query-group-js-divergence 0.35

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v79_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_tail_timeout_v79 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v79.json \
  --selection-csv results/selection_report_smoke_v79.csv \
  --require-prompt-bank-version v7.9

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v79_exec \
  --include-run-id screening_prompt_runner_tail_timeout_v79 \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 1 \
  --max-analysis-retries 0 \
  --generation-timeout-seconds 120 \
  --analysis-timeout-seconds 90 \
  --continue-on-error \
  --max-timeout-failure-share-per-run-id 0.9 \
  --max-timeout-failure-over-selection-ratio-per-run-id 2.0
```