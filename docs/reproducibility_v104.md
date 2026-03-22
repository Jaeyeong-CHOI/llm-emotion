# reproducibility_v104

## 요약
- Screening quality: unknown-year query 집중도에서 **top4 absolute share ceiling**(`--max-manual-qc-review-traceable-known-query-unknown-year-top4-query-share`)을 추가해, ratio 지표가 통과해도 누적 과점을 즉시 차단한다.
- Prompt bank: `v10.4`로 확장(3 scenarios 추가).
- Runner preflight: `top6 share / top6-over-uniform` 가드가 **실제 fail-fast 체크 + constraint snapshot**에 모두 반영되도록 보강했다.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v104 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top4-query-share 0.99 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-over-global-top2-ratio 1.10 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-over-global-top3-ratio 1.08 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top4-over-global-top4-ratio 1.06

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v104_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top4_ratio_top6_uniform_v103 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v104.json \
  --selection-csv results/selection_report_smoke_v104.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.4 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top6-share 1.00 \
  --max-planned-sample-temperature-top6-over-uniform-ratio 1.05 \
  --manifest-note "preflight v104 unknown-year top4 absolute share + top6 guard enforcement"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v104.json`
- `results/selection_report_smoke_v104.csv`
- `results/experiments/smoke_v104_plan/manifest.json`
- `results/experiments/smoke_v104_plan/preflight.json`
- `results/experiments/smoke_v104_plan/preflight.md`

## 재현 체크포인트
1. `screening_quality_report.json`에서 `manual_qc_review_traceable_known_query_unknown_year_top4_query_share`와 관련 gate status를 확인한다.
2. `preflight.json`에서 `planned_sample_temperature_top6_share`, `planned_sample_temperature_top6_over_uniform_ratio`가 존재하고 constraints에도 동일 키가 기록됐는지 확인한다.
3. `manifest.json`에서 `prompt_bank_version=v10.4`가 고정됐는지 확인한다.
