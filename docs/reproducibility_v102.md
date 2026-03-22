# reproducibility_v102

## 요약
- Screening quality: unknown-year query top3 집중을 global known-query top3 baseline과 비교하는 **ratio ceiling gate** 추가.
- Prompt bank: `v10.2`로 확장(3 scenarios, 3 personas).
- Runner preflight: top4 통과 배치에서도 잔존할 수 있는 온도 과집중을 막기 위한 **top5 share + top5-over-uniform guardrail** 추가.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v102 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-over-global-top2-ratio 1.10 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-over-global-top3-ratio 1.08 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top2-over-global-group-top2-ratio 1.10

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v102_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top3_ratio_top5_uniform_v102 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v102.json \
  --selection-csv results/selection_report_smoke_v102.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.2 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top4-share 0.98 \
  --max-planned-sample-temperature-top5-share 1.00 \
  --max-planned-sample-temperature-top4-over-uniform-ratio 1.25 \
  --max-planned-sample-temperature-top5-over-uniform-ratio 1.08 \
  --max-planned-sample-temperature-hhi 0.30 \
  --manifest-note "preflight v102 unknown-year top3 ratio + temperature top5 uniformity guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v102.json`
- `results/selection_report_smoke_v102.csv`
- `results/experiments/smoke_v102_plan/manifest.json`
- `results/experiments/smoke_v102_plan/preflight.json`
- `results/experiments/smoke_v102_plan/preflight.md`
- `results/experiments/smoke_v102_plan/runs.csv`

## 재현 절차
1. screening quality 커맨드로 unknown-year top3/global top3 ratio 신규 게이트를 반영한 QC 리포트를 생성한다.
2. plan-only smoke preflight로 `v10.2` prompt bank + 신규 run-id selection을 동결한다.
3. `preflight.json`에서 `planned_sample_temperature_top5_share`, `planned_sample_temperature_top5_over_uniform_ratio`, `planned_sample_temperature_shares`를 확인한다.
