# Reproducibility v108

## 변경 요약

v108에서는 세 축을 동시에 보강했다.

1. **스크리닝 품질 게이트**: unknown-year query concentration에 `top8` 절대/글로벌 비율 가드를 추가.
2. **프롬프트 뱅크**: `v10.8`로 확장(`top8 ratio guard`, `top8 tail counterbalance`, `temperature top10 tripwire`) + 신규 persona 추가.
3. **실험 러너 preflight 신뢰성**: temperature `top8/top9` share/over-uniform 초과 시 즉시 `RuntimeError`로 fail-fast 하도록 수정(`preflight_errors` 누락 참조 제거).

---

## 1) 스크리닝 품질 리포트 재생성

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v108 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top8-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top8-over-global-top8-ratio 1.00
```

산출물:
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`

---

## 2) 프롬프트 뱅크/실험 매트릭스

- Prompt bank version: **v10.8**
- 신규 scenario id:
  - `screening_unknown_year_top8_ratio_guard_v108`
  - `prompt_bank_top8_tail_counterbalance_patch_v108`
  - `runner_temperature_top10_uniformity_tripwire_v108`
- 신규 persona id:
  - `temperature_top10_uniformity_guard_v108`
- 신규 run id:
  - `screening_prompt_runner_top8_top10_v108`

---

## 3) 러너 preflight 재현

### (A) fail-fast 동작 검증

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v108_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top8_top10_v108 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v108.json \
  --selection-csv results/selection_report_smoke_v108.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.8 \
  --max-planned-sample-temperature-top8-share 0.99 \
  --max-planned-sample-temperature-top9-share 1.00 \
  --max-planned-sample-temperature-top8-over-uniform-ratio 1.40 \
  --max-planned-sample-temperature-top9-over-uniform-ratio 1.45
```

기대: `planned_sample_temperature_top8_share ...` RuntimeError로 즉시 중단.

### (B) 통과 케이스

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v108_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top8_top10_v108 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v108.json \
  --selection-csv results/selection_report_smoke_v108.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.8 \
  --max-planned-sample-temperature-top8-share 1.01 \
  --max-planned-sample-temperature-top9-share 1.01 \
  --max-planned-sample-temperature-top8-over-uniform-ratio 1.60 \
  --max-planned-sample-temperature-top9-over-uniform-ratio 1.70 \
  --manifest-note "preflight v108 top8 unknown-year + top9 runner guard"
```

산출물:
- `results/selection_report_smoke_v108.json`
- `results/selection_report_smoke_v108.csv`
- `results/experiments/smoke_v108_plan/manifest.json`
- `results/experiments/smoke_v108_plan/preflight.md`
