# reproducibility_v100

## 요약
- Screening quality: **unknown-year query-group top2/global group top2 ratio** 게이트(`--max-manual-qc-review-traceable-known-query-unknown-year-group-top2-over-global-group-top2-ratio`)를 추가해 group top1만 통과하고 top2 과점이 남는 케이스를 fail-fast로 차단.
- Prompt bank: `v10.0`으로 확장(3 scenarios, 3 personas).
- Runner preflight: **temperature floor-bin guardrail**(`--planned-sample-temperature-floor-share`, `--min-planned-sample-temperature-floor-bins`)을 추가해 min-share 단일 통과만으로는 잡히지 않는 온도축 hollowing을 차단.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v100 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top1-over-global-group-top1-ratio 1.10 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top2-over-global-group-top2-ratio 1.08

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v100_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_group_top2_floor_bins_v100 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v100.json \
  --selection-csv results/selection_report_smoke_v100.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.0 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top2-share 0.80 \
  --max-planned-sample-temperature-top2-over-uniform-ratio 1.15 \
  --min-planned-sample-temperature-min-share 0.12 \
  --planned-sample-temperature-floor-share 0.15 \
  --min-planned-sample-temperature-floor-bins 3 \
  --max-planned-sample-temperature-hhi 0.30 \
  --manifest-note "preflight v100 unknown-year group top2 ratio + year-tail mesh + temperature floor-bin guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v100.json`
- `results/selection_report_smoke_v100.csv`
- `results/experiments/smoke_v100_plan/manifest.json`
- `results/experiments/smoke_v100_plan/preflight.json`
- `results/experiments/smoke_v100_plan/preflight.md`
- `results/experiments/smoke_v100_plan/runs.csv`

## 재현 절차
1. screening quality 커맨드를 실행해 unknown-year group top2/global group top2 ratio 신규 게이트를 포함한 QC 리포트를 생성한다.
2. plan-only smoke preflight로 `v10.0` prompt bank + 신규 run-id 선택을 동결한다.
3. `preflight.json`에서 `planned_sample_temperature_floor_bins`, `planned_sample_temperature_min_share`, `planned_samples_by_temperature`를 확인한다.
