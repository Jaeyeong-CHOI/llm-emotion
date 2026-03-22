# reproducibility_v99

## 요약
- Screening quality: unknown-year query top2 share 절대값뿐 아니라 **global known-query top2 대비 ratio**를 신규 게이트로 점검.
- Prompt bank: `v9.9`로 확장(3 scenarios, 3 personas).
- Runner preflight: top-k/entropy가 통과해도 소수 temperature 버킷이 비는 현상을 막는 **temperature min-share floor guard** 추가.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v99 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-over-global-top2-ratio 1.10 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top1-over-global-group-top1-ratio 1.10

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v99_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_top2_ratio_floor_v99 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v99.json \
  --selection-csv results/selection_report_smoke_v99.csv \
  --preflight-markdown \
  --require-prompt-bank-version v9.9 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top2-share 0.80 \
  --max-planned-sample-temperature-top2-over-uniform-ratio 1.15 \
  --min-planned-sample-temperature-min-share 0.12 \
  --max-planned-sample-temperature-hhi 0.30 \
  --manifest-note "preflight v99 unknown-year top2 ratio + countervoice mesh + temperature min-share floor"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v99.json`
- `results/selection_report_smoke_v99.csv`
- `results/experiments/smoke_v99_plan/manifest.json`
- `results/experiments/smoke_v99_plan/preflight.json`
- `results/experiments/smoke_v99_plan/preflight.md`
- `results/experiments/smoke_v99_plan/runs.csv`

## 재현 절차
1. screening quality 커맨드를 실행해 unknown-year top2/global top2 ratio 신규 게이트를 포함한 QC 리포트를 갱신한다.
2. plan-only smoke preflight로 `v9.9` prompt bank + 신규 run-id 선택을 동결한다.
3. `preflight.json`에서 `planned_sample_temperature_min_share`, `planned_sample_temperature_top2_over_uniform_ratio`, `planned_samples_by_temperature`를 확인한다.
