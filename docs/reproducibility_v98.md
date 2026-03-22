# reproducibility_v98

## 요약
- Screening quality: unknown-year query-group top1 share의 절대값뿐 아니라 **global group top1 대비 ratio**를 신규 게이트로 점검.
- Prompt bank: `v9.8`로 확장(3 scenarios, 3 personas).
- Runner preflight: top2 share ceiling을 보완하는 **temperature top2-over-uniform ratio guard** 추가.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v98 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 0 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top1-share 0.75 \
  --max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-group-js-divergence 0.35 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top1-over-global-group-top1-ratio 1.10

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v98_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_ratio_v98 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v98.json \
  --selection-csv results/selection_report_smoke_v98.csv \
  --preflight-markdown \
  --require-prompt-bank-version v9.8 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top2-share 0.80 \
  --max-planned-sample-temperature-top2-over-uniform-ratio 1.15 \
  --max-planned-sample-temperature-top3-share 0.90 \
  --max-planned-sample-temperature-hhi 0.30 \
  --manifest-note "preflight v98 unknown-year group ratio + bridge matrix + temperature top2 uniform guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v98.json`
- `results/selection_report_smoke_v98.csv`
- `results/experiments/smoke_v98_plan/manifest.json`
- `results/experiments/smoke_v98_plan/preflight.json`
- `results/experiments/smoke_v98_plan/preflight.md`
- `results/experiments/smoke_v98_plan/runs.csv`

## 재현 절차
1. screening quality 커맨드를 실행해 unknown-year group ratio 신규 게이트를 포함한 QC 리포트를 갱신한다.
2. plan-only smoke preflight로 `v9.8` prompt bank + 신규 run-id 선택을 동결한다.
3. `preflight.json`에서 `planned_sample_temperature_top2_over_uniform_ratio`, `prompt_bank_versions`, `planned_samples_by_temperature`를 확인한다.
