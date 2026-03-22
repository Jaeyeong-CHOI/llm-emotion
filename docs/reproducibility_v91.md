# Reproducibility Notes v9.1

- date: 2026-03-23
- prompt bank version: `v9.1`
- focus: unknown-year query top2 concentration 가드 + multiaxis countervoice mesh 확장 + temperature uniform pressure tripwire
- new run id: `screening_prompt_runner_unknown_year_top2_uniform_v91`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - year=unknown review traceable known-query 분포에 **top2 share ceiling** 게이트 추가
   - 신규 옵션:
     - `--max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share`

2. `scripts/run_experiments.py`
   - 온도 분포의 top1/top2 통과 뒤에 남는 편중을 잡기 위해 균등 대비 과부하/격차 가드 추가
   - 신규 옵션:
     - `--max-planned-sample-temperature-share-gap`
     - `--max-planned-sample-temperature-over-uniform-ratio`

3. `prompts/prompt_bank_ko.json`
   - version `v9.1`
   - 신규 scenarios 3개 + personas 3개 추가
     - `screening_unknown_year_top2_concentration_relief_v91`
     - `prompt_bank_multiaxis_countervoice_mesh_v91`
     - `runner_temperature_uniform_pressure_guard_v91`
     - `unknown_year_top2_dispersion_coach_v91`
     - `multiaxis_countervoice_mesh_curator_v91`
     - `temperature_uniformity_tripwire_auditor_v91`

4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_unknown_year_top2_uniform_v91`

## 재현 명령

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v91 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.9 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 2 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.35

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v91_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_entropy_top2_v90 \
  --include-run-id screening_prompt_runner_unknown_year_top2_uniform_v91 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v91.json \
  --selection-csv results/selection_report_smoke_v91.csv \
  --preflight-markdown \
  --require-prompt-bank-version v9.1 \
  --require-min-temperature-entropy 0.90 \
  --min-planned-sample-temperature-entropy 0.95 \
  --max-planned-sample-temperature-top1-share 0.36 \
  --max-planned-sample-temperature-top2-share 0.68 \
  --max-planned-sample-temperature-share-gap 0.2 \
  --max-planned-sample-temperature-over-uniform-ratio 1.25 \
  --manifest-note "preflight v91 unknown-year top2 + temperature uniform pressure guard"
```