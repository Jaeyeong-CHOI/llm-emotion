# Reproducibility Note v86

- date: 2026-03-23
- focus: screening year-query tail 결합 품질 게이트 강화 + prompt bank v8.6 확장 + runner planned-sample top2/entropy guard 추가
- new run id: `screening_prompt_runner_entropy_top2_v86`

## 변경 요약

1. **screening quality gate 강화** (`scripts/check_screening_quality.py`)
   - 신규 gate: `--max-manual-qc-review-traceable-known-query-year-top3-share`
   - summary/hotspot에 `manual_qc_review_traceable_known_query_year_top3_share` 반영
   - year top1/top2만으로는 놓치던 연도 과점(상위 3개 연도 집중) 탐지를 보강

2. **prompt bank v8.6 확장** (`prompts/prompt_bank_ko.json`)
   - 버전 업데이트: `v8.6`
   - 시나리오 추가:
     - `screening_year_query_tail_joint_repair_v86`
     - `prompt_bank_countervoice_domain_temperature_grid_patch_v86`
     - `runner_planned_sample_top2_entropy_guard_v86`

3. **experiment runner preflight 가드 강화** (`scripts/run_experiments.py`)
   - 신규 guard:
     - `--max-planned-sample-top2-share-per-run-id`
     - `--min-planned-sample-entropy`
   - preflight summary/manifest에 `planned_sample_top2_share`, `planned_sample_entropy` 기록

4. **실험 매트릭스 확장** (`ops/experiment_matrix.json`)
   - run 추가: `screening_prompt_runner_entropy_top2_v86`

## 재현 명령

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v86 \
  --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 \
  --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 \
  --max-manual-qc-review-traceable-known-query-year-top3-share 0.95 \
  --min-manual-qc-review-traceable-known-query-year-tail-share 0.10

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v86_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_year_query_temp_span_v85 \
  --include-run-id screening_prompt_runner_entropy_top2_v86 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v86.json \
  --selection-csv results/selection_report_smoke_v86.csv \
  --preflight-markdown \
  --require-min-scenarios 3 \
  --require-min-personas 4 \
  --require-min-temperature-count 3 \
  --require-min-condition-cells 24 \
  --require-min-total-samples 1600 \
  --require-min-planned-samples-per-run 800 \
  --require-min-unique-scenario-labels 2 \
  --require-min-unique-scenario-tags 10 \
  --require-min-unique-scenario-domains 3 \
  --require-min-unique-scenario-emotion-axes 3 \
  --require-min-unique-scenario-difficulties 1 \
  --require-min-unique-persona-style-tags 12 \
  --require-prompt-bank-version v8.6 \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --max-planned-sample-share-per-run-id 0.60 \
  --max-planned-sample-share-gap-per-run-id 0.20 \
  --max-planned-sample-top2-share-per-run-id 1.00 \
  --min-planned-sample-entropy 1.00 \
  --max-planned-sample-over-selection-ratio-per-run-id 1.20 \
  --manifest-note "preflight v86 year-query-tail coupling + planned-sample top2/entropy guard"
```

## 결과 스냅샷

- `screening_qc_v86`: `status=review`, `quality_score=0.0`, `fail_count=11`
  - `manual_qc_review_traceable_known_query_year_top2_share=1.0`
  - `manual_qc_review_traceable_known_query_year_top3_share=1.0`
  - `manual_qc_review_traceable_known_query_year_tail_share=0.0`
- `smoke_v86_plan`: pass
  - selected run ids: `v85`, `v86`
  - `planned_sample_top2_share=1.0`
  - `planned_sample_entropy=1.0`

## 산출물

- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v86.json`
- `results/selection_report_smoke_v86.csv`
- `results/experiments/smoke_v86_plan/preflight.json`
- `results/experiments/smoke_v86_plan/preflight.md`
- `results/experiments/smoke_v86_plan/manifest.json`
