# reproducibility_v105

## 요약
- Screening quality: unknown-year query 집중도에서 **top5 absolute share + global top5 ratio ceiling**(`--max-manual-qc-review-traceable-known-query-unknown-year-top5-query-share`, `--max-manual-qc-review-traceable-known-query-unknown-year-top5-over-global-top5-ratio`)을 추가해 top4 이후 잔여 과점을 차단한다.
- Prompt bank: `v10.5`로 확장(3 scenarios + 1 persona 추가).
- Runner preflight: `top7 share / top7-over-uniform` 가드를 추가해 top6 통과 이후 숨은 온도축 과집중을 fail-fast로 차단한다.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v105 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top4-query-share 0.99 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top5-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-over-global-top2-ratio 1.10 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-over-global-top3-ratio 1.08 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top4-over-global-top4-ratio 1.06 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top5-over-global-top5-ratio 1.04

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v105_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top5_ratio_top7_uniform_v105 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v105.json \
  --selection-csv results/selection_report_smoke_v105.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.5 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top7-share 1.00 \
  --max-planned-sample-temperature-top7-over-uniform-ratio 1.04 \
  --manifest-note "preflight v105 unknown-year top5 ratio + top7 guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v105.json`
- `results/selection_report_smoke_v105.csv`
- `results/experiments/smoke_v105_plan/manifest.json`
- `results/experiments/smoke_v105_plan/preflight.json`
- `results/experiments/smoke_v105_plan/preflight.md`

## 재현 체크포인트
1. `screening_quality_report.json`에서 `manual_qc_review_traceable_known_query_unknown_year_top5_query_share`, `manual_qc_review_traceable_known_query_unknown_year_top5_over_global_top5_ratio` 및 신규 gate status를 확인한다.
2. `preflight.json`에서 `planned_sample_temperature_top7_share`, `planned_sample_temperature_top7_over_uniform_ratio`가 summary/constraints에 함께 기록됐는지 확인한다.
3. `manifest.json`에서 `prompt_bank_version=v10.5` 고정을 확인한다.
