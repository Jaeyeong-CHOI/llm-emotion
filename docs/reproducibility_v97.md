# reproducibility_v97

## 요약
- Screening quality: unknown-year raw query 분산만으로 놓치던 query-group drift를 별도 게이트로 점검하도록 확장.
- Prompt bank: `v9.7`로 확장(3 scenarios, 3 personas).
- Runner preflight: top-k share/HHI를 보완하는 temperature tail-share 가드를 추가.

## 실행 커맨드
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v97 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 0 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top1-share 0.75 \
  --max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-js-divergence 0.30 \
  --max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-group-js-divergence 0.35 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-over-global-top1-ratio 1.25

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v97_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_tail_v97 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v97.json \
  --selection-csv results/selection_report_smoke_v97.csv \
  --preflight-markdown \
  --require-prompt-bank-version v9.7 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top3-share 0.90 \
  --max-planned-sample-temperature-top4-share 0.98 \
  --max-planned-sample-temperature-hhi 0.30 \
  --min-planned-sample-temperature-tail-share 0.55 \
  --manifest-note "preflight v97 unknown-year query-group drift + persona fairness lattice + temperature tail share guard"
```

## 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v97.json`
- `results/selection_report_smoke_v97.csv`
- `results/experiments/smoke_v97_plan/manifest.json`
- `results/experiments/smoke_v97_plan/preflight.json`
- `results/experiments/smoke_v97_plan/preflight.md`
- `results/experiments/smoke_v97_plan/runs.csv`

## 재현 절차
1. 위 screening quality 커맨드로 `results/screening_quality_report.{json,md}`를 갱신한다.
2. 이어서 plan-only smoke preflight를 실행해 `v9.7` prompt bank와 새 run-id 선택 결과를 동결한다.
3. `results/experiments/smoke_v97_plan/preflight.json`에서 `planned_sample_temperature_tail_share`, `planned_sample_temperature_hhi`, `prompt_bank_versions`를 확인한다.
4. 필요 시 동일 `--include-run-id screening_prompt_runner_unknown_year_group_tail_v97` 조합으로 execution 모드를 별도 실행한다.

## 참고
- 현재 manual QC 표본에는 unknown-year traceable known-query 행이 0건이라, v9.7 재현 커맨드는 query/group concentration floor를 0으로 열고 drift ceiling 위주로 검증한다.
