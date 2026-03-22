# Reproducibility Note v82

- focus: screening review-year drift QC 강화 + prompt bank v8.2 확장 + runner planned-sample-share preflight guard
- prompt bank version: `v8.2`
- new run id: `screening_prompt_runner_year_budget_v82`
- verification timestamp (UTC): `2026-03-22T17:42:54Z`

## Changes
- `scripts/check_screening_quality.py`
  - 신규 게이트: `--max-manual-qc-review-traceable-known-query-year-js-divergence`
  - `review traceable known-query`의 연도 분포가 전체 manual QC 연도 분포에서 과도하게 이탈하는지 JS divergence로 점검
- `prompts/prompt_bank_ko.json`
  - 시나리오 추가: `screening_review_year_drift_patch_v82`, `runner_planned_sample_share_audit_v82`
  - 페르소나 추가: `review_year_balance_curator_v82`, `planned_sample_budget_controller_v82`
  - version: `v8.2`
- `scripts/run_experiments.py`
  - 신규 preflight guard: `--max-planned-sample-share-per-run-id`
  - 신규 preflight guard: `--max-planned-sample-share-gap-per-run-id`
- `ops/experiment_matrix.json`
  - run 추가: `screening_prompt_runner_year_budget_v82`

## Commands
```bash
python3 -m py_compile scripts/generate_dataset.py scripts/run_experiments.py scripts/check_screening_quality.py

python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v82 \
  --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v82_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_entropy_tail_v81 \
  --include-run-id screening_prompt_runner_year_budget_v82 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v82.json \
  --selection-csv results/selection_report_smoke_v82.csv \
  --preflight-markdown \
  --require-prompt-bank-version v8.2 \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --max-planned-sample-share-per-run-id 0.60 \
  --max-planned-sample-share-gap-per-run-id 0.20 \
  --manifest-note "preflight v82 year-budget"
```

## Smoke results
- `py_compile`: pass
- `screening_qc_v82`: `status=review`, `quality_score=0.0`, `fail_count=7`
- 핵심 신규 지표: `manual_qc_review_traceable_known_query_year_js_divergence=0.2087` with threshold `<=0.25` -> `pass`
- `smoke_v82_plan`: pass
  - selected run ids: `2`
  - prompt bank version: `v8.2`
  - planned sample share: `v81=0.4286`, `v82=0.5714`
  - planned sample share gap: `0.1428`

## Artifacts
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v82.json`
- `results/selection_report_smoke_v82.csv`
- `results/experiments/smoke_v82_plan/preflight.json`
- `results/experiments/smoke_v82_plan/preflight.md`
