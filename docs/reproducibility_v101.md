# reproducibility_v101

## 요약
- Screening quality: **unknown-year query-group tail share floor + global tail ratio floor** 게이트(`--min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share`, `--min-manual-qc-review-traceable-known-query-unknown-year-group-tail-over-global-group-tail-ratio`)를 추가해 top2 과점이 완화된 것처럼 보여도 tail이 baseline 대비 수축한 케이스를 fail-fast로 차단.
- Prompt bank: `v10.1`로 확장(3 scenarios, 3 personas).
- Runner preflight: **temperature floor-bin share-gap guardrail**(`--max-planned-sample-temperature-floor-bin-share-gap`)을 추가해 floor-bin 개수는 충족해도 내부 편차가 큰 배치를 사전 차단.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v101 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top2-over-global-group-top2-ratio 1.08 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share 0.10 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-tail-over-global-group-tail-ratio 0.85

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v101_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_group_tail_floor_gap_v101 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v101.json \
  --selection-csv results/selection_report_smoke_v101.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.1 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top2-share 0.80 \
  --planned-sample-temperature-floor-share 0.15 \
  --min-planned-sample-temperature-floor-bins 3 \
  --max-planned-sample-temperature-floor-bin-share-gap 0.08 \
  --max-planned-sample-temperature-hhi 0.30 \
  --manifest-note "preflight v101 unknown-year group tail ratio floor + tail mesh + temperature floor-gap guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v101.json`
- `results/selection_report_smoke_v101.csv`
- `results/experiments/smoke_v101_plan/manifest.json`
- `results/experiments/smoke_v101_plan/preflight.json`
- `results/experiments/smoke_v101_plan/preflight.md`
- `results/experiments/smoke_v101_plan/runs.csv`

## 재현 절차
1. screening quality 커맨드를 실행해 unknown-year query-group tail floor/ratio 신규 게이트를 포함한 QC 리포트를 생성한다.
2. plan-only smoke preflight로 `v10.1` prompt bank + 신규 run-id 선택을 동결한다.
3. `preflight.json`에서 `planned_sample_temperature_floor_bins`, `planned_sample_temperature_floor_bin_share_gap`, `planned_samples_by_temperature`를 함께 확인한다.
