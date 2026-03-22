# Reproducibility v113

## 개요
- 날짜(로컬): 2026-03-23 (Asia/Seoul)
- 목적: (1) 선행연구 스크리닝 품질 가드 확장(top4 group ratio), (2) 프롬프트 뱅크 v11.3 확장, (3) 실험 러너 temperature top12 uniformity guardrail 추가

## 코드/설정 변경
- `scripts/check_screening_quality.py`
  - unknown-year query-group `top4 share` 및 `top4 over global top4 ratio` 계산/요약/게이트 추가
  - 신규 CLI 인자:
    - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top4-share`
    - `--max-manual-qc-review-traceable-known-query-unknown-year-group-top4-over-global-group-top4-ratio`
- `scripts/run_experiments.py`
  - planned-sample temperature `top12 share`, `top12-over-uniform ratio` 계산/요약/프리플라이트 fail-fast 추가
  - 신규 CLI 인자:
    - `--max-planned-sample-temperature-top12-share`
    - `--max-planned-sample-temperature-top12-over-uniform-ratio`
- `prompts/prompt_bank_ko.json`
  - 버전 `v11.3`
  - 신규 시나리오 3개:
    - `screening_unknown_year_group_top4_ratio_guard_v113`
    - `prompt_bank_unknown_year_group_top4_counterbalance_v113`
    - `runner_temperature_top12_uniformity_tripwire_v113`
  - 신규 페르소나 1개:
    - `temperature_top12_uniformity_guard_v113`
- `ops/experiment_matrix.json`
  - 신규 run 추가:
    - `screening_prompt_runner_unknown_year_group_top4_temperature_top12_v113`

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v113.json \
  --out-md results/screening_quality_report_v113.md \
  --run-label screening_qc_v113 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top1-share 0.75 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top2-over-global-group-top2-ratio 1.15 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top3-share 0.98 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top3-over-global-group-top3-ratio 1.08 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top4-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top4-over-global-group-top4-ratio 1.05 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share 0.08

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v113_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top4_temperature_top12_v113 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v113.json \
  --selection-csv results/selection_report_smoke_v113.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.3 \
  --max-generation-timeout-failure-over-selection-ratio-per-run-id 1.8 \
  --max-analysis-timeout-failure-over-selection-ratio-per-run-id 1.8 \
  --max-generation-timeout-failure-share-per-run-id 0.65 \
  --max-analysis-timeout-failure-share-per-run-id 0.65 \
  --max-planned-sample-temperature-top12-share 1.0 \
  --max-planned-sample-temperature-top12-over-uniform-ratio 1.0 \
  --manifest-note "preflight v113 unknown-year group top4 + temperature top12 uniformity guard"
```

## 산출물
- `results/screening_quality_report_v113.json`
- `results/screening_quality_report_v113.md`
- `results/selection_report_smoke_v113.json`
- `results/selection_report_smoke_v113.csv`
- `results/experiments/smoke_v113_plan/`

## 실행 결과 요약
- screening quality: `status=review`, `quality_score=0.0`, `fail_count=17`
- preflight plan-only: selected run cell 2개, `selected_total_samples=3456`, 실행 실패 셀 0
