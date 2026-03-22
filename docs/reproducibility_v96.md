# reproducibility_v96

## 요약
- Screening quality: unknown-year 분포가 global known-query top1 대비 과도하게 쏠리는지 점검하는 비율 게이트를 추가.
- Prompt bank: `v9.6`로 확장(3 scenarios, 3 personas).
- Runner preflight: temperature 축 concentration을 HHI로 감시하는 게이트를 추가.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v96 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 3 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.40 \
  --max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-js-divergence 0.30 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-over-global-top1-ratio 1.25

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v96_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_query_group_hhi_v96 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v96.json \
  --selection-csv results/selection_report_smoke_v96.csv \
  --preflight-markdown \
  --require-prompt-bank-version v9.6 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top3-share 0.90 \
  --max-planned-sample-temperature-top4-share 0.98 \
  --max-planned-sample-temperature-top4-over-uniform-ratio 1.25 \
  --max-planned-sample-temperature-hhi 0.30 \
  --manifest-note "preflight v96 query-group baseline + crossband mesh + temperature HHI guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v96.json`
- `results/selection_report_smoke_v96.csv`
- `results/experiments/smoke_v96_plan/manifest.json`
- `results/experiments/smoke_v96_plan/preflight.json`
- `results/experiments/smoke_v96_plan/preflight.md`
- `results/experiments/smoke_v96_plan/runs.csv`

## 참고
- 이 스모크는 `--plan-only` 기준 재현성 점검이다. 실제 실행 배치는 동일 run-id에 대해 execution 모드로 별도 수행.
