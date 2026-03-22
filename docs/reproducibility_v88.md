# Reproducibility Notes v8.8

- date: 2026-03-23
- prompt bank version: `v8.8`
- focus: screening unknown-year traceability 품질 강화 + prompt bank entropy rebalance 확장 + runner selected entropy tripwire 고도화
- new run id: `screening_prompt_runner_selected_entropy_v88`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - review traceable known-query에서 `unknown` year 비중/절대량을 분리 감시하는 가드 추가
   - 신규 옵션:
     - `--max-manual-qc-review-traceable-known-query-unknown-year-share`
     - `--min-manual-qc-review-traceable-known-query-known-year-count`

2. `scripts/run_experiments.py`
   - run 단위 entropy 가드:
     - `--require-min-scenario-tag-entropy`
     - `--require-min-persona-style-tag-entropy`
   - selected batch 단위 entropy 가드:
     - `--require-min-selected-scenario-tag-entropy`
     - `--require-min-selected-persona-style-tag-entropy`

3. `prompts/prompt_bank_ko.json`
   - version `v8.8`
   - 신규 scenarios:
     - `screening_review_unknown_year_traceability_backfill_v88`
     - `prompt_bank_persona_style_entropy_rebalance_drill_v88`
     - `runner_selected_tag_entropy_tripwire_v88`
   - 신규 personas:
     - `unknown_year_traceability_curator_v88`
     - `selected_entropy_tripwire_operator_v88`

4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_selected_entropy_v88`

---

## 재현 명령

### 1) 스크리닝 품질(v88)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v88 \
  --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 \
  --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 \
  --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 \
  --min-manual-qc-review-traceable-known-query-year-tail-count 3 \
  --min-manual-qc-review-traceable-known-query-year-entropy 0.45 \
  --min-manual-qc-review-traceable-known-query-year-coverage 3 \
  --max-manual-qc-review-traceable-known-query-unknown-year-share 0.20 \
  --min-manual-qc-review-traceable-known-query-known-year-count 3
```

### 2) Runner preflight(v88)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v88_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_year_query_persona_entropy_v87 \
  --include-run-id screening_prompt_runner_selected_entropy_v88 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v88.json \
  --selection-csv results/selection_report_smoke_v88.csv \
  --preflight-markdown \
  --require-prompt-bank-version v8.8 \
  --require-min-selected-temperatures 3 \
  --require-min-selected-temperature-span 0.7 \
  --require-min-selected-scenario-tag-entropy 0.70 \
  --require-min-selected-persona-style-tag-entropy 0.70 \
  --require-min-scenario-tag-entropy 0.65 \
  --require-min-persona-style-tag-entropy 0.65 \
  --max-planned-sample-share-per-run-id 0.60 \
  --max-planned-sample-share-gap-per-run-id 0.25 \
  --manifest-note "preflight v88 unknown-year + selected entropy guard"
```

## 검증 포인트

- `results/screening_quality_report.json`
  - `manual_qc_review_traceable_known_query_unknown_year_share`
  - `manual_qc_review_traceable_known_query_known_year_count`
- `results/experiments/smoke_v88_plan/preflight.json`
  - `selected_scenario_tag_entropy`
  - `selected_persona_style_tag_entropy`
  - run별 `scenario_tag_entropy`, `persona_style_tag_entropy`
