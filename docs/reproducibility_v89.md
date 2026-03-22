# Reproducibility Notes v8.9

- date: 2026-03-23
- prompt bank version: `v8.9`
- focus: screening unknown-year query concentration 완화 + prompt bank temperature countervoice 회전 확장 + runner temperature entropy tripwire 고도화
- new run id: `screening_prompt_runner_unknown_year_temperature_v89`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - review traceable known-query에서 `year=unknown`이 일부 query에 과집중되는 리스크를 별도 감시하도록 지표/게이트 추가
   - 신규 옵션:
     - `--max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share`
     - `--min-manual-qc-review-traceable-known-query-unknown-year-query-coverage`

2. `scripts/run_experiments.py`
   - run 단위 temperature 분산 안정성 가드 추가:
     - `--require-min-temperature-entropy`
   - selected batch planned-sample 온도축 과집중 가드 추가:
     - `--min-planned-sample-temperature-entropy`
     - `--max-planned-sample-temperature-top1-share`

3. `prompts/prompt_bank_ko.json`
   - version `v8.9`
   - 신규 scenarios:
     - `screening_review_unknown_year_query_concentration_relief_v89`
     - `prompt_bank_temperature_countervoice_rotation_patch_v89`
     - `runner_temperature_entropy_circuit_breaker_postmortem_v89`
   - 신규 personas:
     - `unknown_year_query_dispersion_auditor_v89`
     - `temperature_countervoice_rotation_curator_v89`
     - `temperature_entropy_tripwire_steward_v89`

4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_unknown_year_temperature_v89`

## 재현 명령

### 1) 스크리닝 품질(v89)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v89 \
  --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 \
  --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 \
  --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 \
  --min-manual-qc-review-traceable-known-query-year-tail-count 3 \
  --min-manual-qc-review-traceable-known-query-year-entropy 0.45 \
  --min-manual-qc-review-traceable-known-query-year-coverage 3 \
  --max-manual-qc-review-traceable-known-query-unknown-year-share 0.20 \
  --min-manual-qc-review-traceable-known-query-known-year-count 3 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 2
```

### 2) Runner preflight(v89)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v89_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_selected_entropy_v88 \
  --include-run-id screening_prompt_runner_unknown_year_temperature_v89 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v89.json \
  --selection-csv results/selection_report_smoke_v89.csv \
  --preflight-markdown \
  --require-prompt-bank-version v8.9 \
  --require-min-selected-temperatures 3 \
  --require-min-selected-temperature-span 0.7 \
  --require-min-temperature-entropy 0.90 \
  --min-planned-sample-temperature-entropy 0.95 \
  --max-planned-sample-temperature-top1-share 0.36 \
  --require-min-selected-scenario-tag-entropy 0.70 \
  --require-min-selected-persona-style-tag-entropy 0.70 \
  --max-planned-sample-share-per-run-id 0.60 \
  --max-planned-sample-share-gap-per-run-id 0.25 \
  --manifest-note "preflight v89 unknown-year concentration + temperature entropy guard"
```
