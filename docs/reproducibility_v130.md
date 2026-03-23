# Reproducibility v130

## 변경 요약
- 스크리닝 품질: `scripts/check_screening_quality.py`에 unknown-year query-group **top21 절대/글로벌 비율 가드** 추가
- 프롬프트 뱅크: `v130.0`으로 갱신하고 top21 countervoice mesh 시나리오·페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p65 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p65-share-ratio`) 추가
- 스크리닝 규칙: `queries/screening_rules.json`에 counterfactual richness / emotion differentiation training / metacognitive reappraisal alias와 equivalence test / SESOI / invariance testing method cue 추가

## 재현 커맨드

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v130.json \
  --out-md results/screening_quality_report_v130.md \
  --run-label screening_qc_v130 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top21-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top21-over-global-group-top21-ratio 1.0

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v130_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top21_temperature_p99_p65_v130 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v130.json \
  --selection-csv results/selection_report_smoke_v130.csv \
  --preflight-markdown \
  --require-prompt-bank-version v130.0 \
  --max-planned-sample-temperature-p99-over-p65-share-ratio 1.15 \
  --manifest-note "preflight v130 unknown-year group top21 + temperature p99/p65 guard"
```

## 기대 산출물
- `results/screening_quality_report_v130.json`
- `results/screening_quality_report_v130.md`
- `results/selection_report_smoke_v130.json`
- `results/selection_report_smoke_v130.csv`
- `results/experiments/smoke_v130_plan/preflight.json`
- `results/experiments/smoke_v130_plan/preflight.md`
- `results/experiments/smoke_v130_plan/manifest.json`
