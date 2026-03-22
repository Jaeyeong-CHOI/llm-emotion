# Reproducibility Playbook v65

## 변경 요약
- screening 품질 게이트: `manual_qc_review_query_traceability_share` 추가
  - CLI: `--min-manual-qc-review-query-traceability-share`
  - 의미: review 근거가 남은 표본 중 source_query가 추적 가능한 비율 하한
- prompt bank: `v6.5`
  - 시나리오: `screening_query_provenance_gap_repair`, `prompt_bank_countervoice_translation_hole`, `runner_live_share_tripwire_recovery`
  - 페르소나: `query_provenance_guard`, `countervoice_translation_curator`, `live_tripwire_controller`
- runner: live attempt-share tripwire 추가
  - `--max-live-generation-attempt-share-per-run-id`
  - `--max-live-analysis-attempt-share-per-run-id`
  - `--max-live-combined-attempt-share-per-run-id`

## v65 preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v65_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_live_traceability_v65 \
  --require-prompt-bank-version v6.5 \
  --require-min-unique-scenario-labels 2 \
  --require-min-selected-scenario-labels 2 \
  --print-selection
```

## v65 smoke 실행
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v65_exec \
  --include-run-id screening_prompt_runner_live_traceability_v65 \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 2 \
  --max-analysis-retries 1 \
  --max-live-generation-attempt-share-per-run-id 0.9 \
  --max-live-analysis-attempt-share-per-run-id 0.9 \
  --max-live-combined-attempt-share-per-run-id 0.9 \
  --manifest-markdown
```

## screening QC 예시
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --run-label screening_qc_v65 \
  --min-manual-qc-review-query-traceability-share 0.75
```
