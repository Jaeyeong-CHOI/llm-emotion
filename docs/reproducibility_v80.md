# Reproducibility Note v80

- focus: screening source-group tail-share floor 강화 + prompt bank v8.0 확장 + runner batch aggregate metadata floor guard
- new run id: `screening_prompt_runner_group_tail_metadata_v80`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - 신규 지표: `manual_qc_review_traceable_known_query_group_tail_share`
   - 신규 게이트 인자: `--min-manual-qc-review-traceable-known-query-group-tail-share` (default `0.1`)
2. `prompts/prompt_bank_ko.json`
   - version `v8.0`
   - scenarios 2종 추가
   - personas 2종 추가
3. `scripts/run_experiments.py`
   - 신규 batch aggregate floor 인자:
     - `--require-min-selected-scenario-domains`
     - `--require-min-selected-scenario-emotion-axes`
     - `--require-min-selected-scenario-difficulties`
   - run-id 개별 preflight를 통과해도, 배치 전체 축 커버리지가 부족하면 fail-fast
4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_group_tail_metadata_v80`

## 재현 커맨드 (smoke)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v80 \
  --min-manual-qc-review-traceable-known-query-group-tail-share 0.10

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v80_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_group_tail_metadata_v80 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v80.json \
  --selection-csv results/selection_report_smoke_v80.csv \
  --require-prompt-bank-version v8.0 \
  --require-min-selected-scenario-domains 3 \
  --require-min-selected-scenario-emotion-axes 3 \
  --require-min-selected-scenario-difficulties 1

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v80_exec \
  --include-run-id screening_prompt_runner_group_tail_metadata_v80 \
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
