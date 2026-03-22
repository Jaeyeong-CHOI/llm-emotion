# Reproducibility Notes v9.0

- date: 2026-03-23
- prompt bank version: `v9.0`
- focus: screening unknown-year query entropy 복구 + prompt temperature lattice 확장 + runner top2 temperature pressure tripwire
- new run id: `screening_prompt_runner_unknown_year_entropy_top2_v90`

## 변경 요약

1. `scripts/check_screening_quality.py`
   - year=unknown review traceable known-query 분포에 query entropy gate 추가
   - 신규 옵션:
     - `--min-manual-qc-review-traceable-known-query-unknown-year-query-entropy`

2. `scripts/run_experiments.py`
   - selected batch 온도 편중을 top2 share 기준으로도 차단
   - 신규 옵션:
     - `--max-planned-sample-temperature-top2-share`

3. `prompts/prompt_bank_ko.json`
   - version `v9.0`
   - 신규 scenarios/personas 추가 (unknown-year entropy, temperature lattice, top2 tripwire)

4. `ops/experiment_matrix.json`
   - run 추가: `screening_prompt_runner_unknown_year_entropy_top2_v90`

## 재현 명령

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v90 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 2 \
  --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.35

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v90_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_temperature_v89 \
  --include-run-id screening_prompt_runner_unknown_year_entropy_top2_v90 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v90.json \
  --selection-csv results/selection_report_smoke_v90.csv \
  --preflight-markdown \
  --require-prompt-bank-version v9.0 \
  --require-min-temperature-entropy 0.90 \
  --min-planned-sample-temperature-entropy 0.95 \
  --max-planned-sample-temperature-top1-share 0.36 \
  --max-planned-sample-temperature-top2-share 0.68 \
  --manifest-note "preflight v90 unknown-year entropy + temperature top2 guard"
```
