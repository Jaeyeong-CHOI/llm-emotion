# reproducibility_v110

## 요약
- Screening quality: `queries/screening_rules.json`에 **emotional attribution / empathy / social-emotional reasoning** 계열 alias·method cue를 보강해 선행연구 스크리닝 재현율(특히 경계 review 구간) 개선.
- Prompt bank: `v11.0`으로 확장(3 scenarios, 1 persona).
- Runner preflight: temperature guard를 **top11/top12 share + top11/top12 over-uniform ratio**까지 확장.

## 실행 커맨드
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v110_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top10_top11_top12_v110 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v110.json \
  --selection-csv results/selection_report_smoke_v110.csv \
  --preflight-markdown \
  --require-prompt-bank-version v11.0 \
  --min-planned-sample-temperature-entropy 0.90 \
  --max-planned-sample-temperature-top10-share 1.01 \
  --max-planned-sample-temperature-top11-share 1.01 \
  --max-planned-sample-temperature-top12-share 1.01 \
  --max-planned-sample-temperature-top10-over-uniform-ratio 1.20 \
  --max-planned-sample-temperature-top11-over-uniform-ratio 1.20 \
  --max-planned-sample-temperature-top12-over-uniform-ratio 1.20 \
  --manifest-note "preflight v110 unknown-year top10 ratio + top10 counterbalance + temperature top11/top12 uniformity guard"
```

## 산출물
- `results/selection_report_smoke_v110.json`
- `results/selection_report_smoke_v110.csv`
- `results/experiments/smoke_v110_plan/manifest.json`
- `results/experiments/smoke_v110_plan/preflight.json`
- `results/experiments/smoke_v110_plan/preflight.md`
- `results/experiments/smoke_v110_plan/runs.csv`

## 재현 절차
1. prompt bank version이 `v11.0`인지 확인한다.
2. 위 plan-only 커맨드로 신규 run-id(`screening_prompt_runner_top10_top11_top12_v110`) preflight를 고정한다.
3. `preflight.json`에서 `planned_sample_temperature_top11_share`, `planned_sample_temperature_top12_share`, `planned_sample_temperature_top11_over_uniform_ratio`, `planned_sample_temperature_top12_over_uniform_ratio`를 점검한다.
4. screening rules 보강 효과를 보려면 `scripts/search_openalex.py` 결과에서 review/include 경계 구간의 `screening_reasons`에 신규 alias hit가 반영되는지 확인한다.
