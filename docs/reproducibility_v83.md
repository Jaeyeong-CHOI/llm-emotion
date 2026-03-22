# Reproducibility Note v83

- date: 2026-03-23
- focus: screening review-year tail 복구 게이트 추가 + prompt bank v8.3 확장 + runner planned-sample pressure ratio 가드 추가
- new run id: `screening_prompt_runner_year_tail_pressure_v83`

## 변경 요약

1. **screening quality gate 강화** (`scripts/check_screening_quality.py`)
   - 신규 gate: `--max-manual-qc-review-traceable-known-query-year-top2-share`
   - 신규 gate: `--min-manual-qc-review-traceable-known-query-year-tail-share`
   - summary/hotspot에 year top2/tail 지표 추가

2. **prompt bank v8.3 확장** (`prompts/prompt_bank_ko.json`)
   - 시나리오 추가: `screening_review_year_tail_recovery_v83`, `runner_planned_sample_pressure_audit_v83`
   - 페르소나 추가: `review_year_tail_safeguard_operator_v83`, `planned_sample_pressure_auditor_v83`

3. **experiment runner preflight 가드 강화** (`scripts/run_experiments.py`)
   - 신규 preflight guard: `--max-planned-sample-over-selection-ratio-per-run-id`
   - preflight summary에 `max_planned_sample_over_selection_ratio` 기록

4. **실험 매트릭스 확장** (`ops/experiment_matrix.json`)
   - run 추가: `screening_prompt_runner_year_tail_pressure_v83`

## 재현 명령

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v83 \
  --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 \
  --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 \
  --min-manual-qc-review-traceable-known-query-year-tail-share 0.10

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v83_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_year_budget_v82 \
  --include-run-id screening_prompt_runner_year_tail_pressure_v83 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v83.json \
  --selection-csv results/selection_report_smoke_v83.csv \
  --preflight-markdown \
  --require-min-scenarios 3 \
  --require-min-personas 4 \
  --require-min-temperature-count 3 \
  --require-min-condition-cells 27 \
  --require-min-total-samples 1600 \
  --require-min-planned-samples-per-run 800 \
  --require-min-unique-scenario-labels 2 \
  --require-min-unique-scenario-tags 10 \
  --require-min-unique-scenario-domains 3 \
  --require-min-unique-scenario-emotion-axes 3 \
  --require-min-unique-scenario-difficulties 1 \
  --require-min-unique-persona-style-tags 12 \
  --require-prompt-bank-version v8.3 \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --max-planned-sample-share-per-run-id 0.60 \
  --max-planned-sample-share-gap-per-run-id 0.20 \
  --max-planned-sample-over-selection-ratio-per-run-id 1.20 \
  --manifest-note "preflight v83 year-tail + planned-sample-pressure guard"
```

## 결과 스냅샷

- `screening_qc_v83`: `status=review`, `quality_score=0.0`, `fail_count=9`
  - `manual_qc_review_traceable_known_query_year_top2_share=1.0`
  - `manual_qc_review_traceable_known_query_year_tail_share=0.0`
  - `manual_qc_review_traceable_known_query_year_js_divergence=0.2087`
- `smoke_v83_plan`: pass
  - selected run ids: `v82`, `v83`
  - planned sample share: `v82=0.5`, `v83=0.5`
  - max planned sample over selection ratio: `1.0`

## 산출물

- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v83.json`
- `results/selection_report_smoke_v83.csv`
- `results/experiments/smoke_v83_plan/preflight.json`
- `results/experiments/smoke_v83_plan/preflight.md`
- `results/experiments/smoke_v83_plan/manifest.json`
