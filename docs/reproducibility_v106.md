# reproducibility_v106

## 요약
- Screening quality: unknown-year query 집중도에서 **top6 absolute share + global top6 ratio ceiling**(`--max-manual-qc-review-traceable-known-query-unknown-year-top6-query-share`, `--max-manual-qc-review-traceable-known-query-unknown-year-top6-over-global-top6-ratio`)을 추가해 top5 통과 이후 남는 tail 과점을 차단한다.
- Prompt bank: `v10.6`로 확장(3 scenarios + 1 persona 추가).
- Runner preflight: `top8 share / top8-over-uniform` 가드를 추가해 top7 통과 이후 숨은 온도축 과집중을 fail-fast로 차단한다.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v106 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top4-query-share 0.99 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top5-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top6-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-over-global-top2-ratio 1.10 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-over-global-top3-ratio 1.08 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top4-over-global-top4-ratio 1.06 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top5-over-global-top5-ratio 1.04 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top6-over-global-top6-ratio 1.02

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v106_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top6_ratio_top8_uniform_v106 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v106.json \
  --selection-csv results/selection_report_smoke_v106.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.6 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top8-share 1.00 \
  --max-planned-sample-temperature-top8-over-uniform-ratio 1.03 \
  --manifest-note "preflight v106 unknown-year top6 ratio + top8 uniformity guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v106.json`
- `results/selection_report_smoke_v106.csv`
- `results/experiments/smoke_v106_plan/manifest.json`
- `results/experiments/smoke_v106_plan/preflight.json`
- `results/experiments/smoke_v106_plan/preflight.md`

## 재현 체크포인트
1. `screening_quality_report.json`에서 `manual_qc_review_traceable_known_query_unknown_year_top6_query_share`, `manual_qc_review_traceable_known_query_unknown_year_top6_over_global_top6_ratio` 및 신규 gate status를 확인한다.
2. `preflight.json`에서 `planned_sample_temperature_top8_share`, `planned_sample_temperature_top8_over_uniform_ratio`가 summary/constraints에 함께 기록됐는지 확인한다.
3. `manifest.json`에서 `prompt_bank_version=v10.6` 고정을 확인한다.
