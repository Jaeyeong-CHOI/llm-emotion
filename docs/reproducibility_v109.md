# Reproducibility v109

## 변경 요약

v109에서는 우선순위 3축을 연속 강화했다.

1. **스크리닝 품질 게이트**: unknown-year query concentration에 `top9` 절대/글로벌 비율 가드를 추가.
2. **프롬프트 뱅크**: `v10.9`로 확장(`top9 ratio guard`, `top9 tail counterbalance`, `temperature top10/top11 tripwire`) + 신규 persona 추가.
3. **실험 러너 preflight 고도화**: temperature `top10` share/over-uniform guardrail을 추가해 `top9` 통과 이후 남는 누적 집중을 fail-fast 차단.

---

## 1) 스크리닝 품질 리포트 재생성

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v109 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top9-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top9-over-global-top9-ratio 1.00
```

산출물:
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`

---

## 2) 프롬프트 뱅크/실험 매트릭스

- Prompt bank version: **v10.9**
- 신규 scenario id:
  - `screening_unknown_year_top9_ratio_guard_v109`
  - `prompt_bank_top9_tail_counterbalance_patch_v109`
  - `runner_temperature_top10_top11_uniformity_tripwire_v109`
- 신규 persona id:
  - `temperature_top11_uniformity_guard_v109`
- 신규 run id:
  - `screening_prompt_runner_top9_top10_top11_v109`

---

## 3) 러너 preflight 재현

### (A) fail-fast 동작 검증

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v109_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top9_top10_top11_v109 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v109.json \
  --selection-csv results/selection_report_smoke_v109.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.9 \
  --max-planned-sample-temperature-top9-share 1.00 \
  --max-planned-sample-temperature-top10-share 0.99 \
  --max-planned-sample-temperature-top9-over-uniform-ratio 1.45 \
  --max-planned-sample-temperature-top10-over-uniform-ratio 1.45
```

기대: `planned_sample_temperature_top10_share ...` RuntimeError로 즉시 중단.

### (B) 통과 케이스

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v109_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top9_top10_top11_v109 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v109.json \
  --selection-csv results/selection_report_smoke_v109.csv \
  --preflight-markdown \
  --require-prompt-bank-version v10.9 \
  --max-planned-sample-temperature-top9-share 1.01 \
  --max-planned-sample-temperature-top10-share 1.01 \
  --max-planned-sample-temperature-top9-over-uniform-ratio 1.70 \
  --max-planned-sample-temperature-top10-over-uniform-ratio 1.70 \
  --manifest-note "preflight v109 top9 unknown-year + top10 runner guard"
```

산출물:
- `results/selection_report_smoke_v109.json`
- `results/selection_report_smoke_v109.csv`
- `results/experiments/smoke_v109_plan/manifest.json`
- `results/experiments/smoke_v109_plan/preflight.md`
