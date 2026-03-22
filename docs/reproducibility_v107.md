# Reproducibility v107

## 목표
- Screening: unknown-year query 상위 7개 과집중(top7) 절대/상대 비율 동시 감시
- Prompt bank: v10.7 시나리오/페르소나 확장 반영
- Runner: temperature top9 누적 점유율 + uniform 대비 비율 guardrail 추가

## 1) Screening QC (top7 guard)

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v107 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top6-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top7-query-share 1.00 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top6-over-global-top6-ratio 1.02 \
  --max-manual-qc-review-traceable-known-query-unknown-year-top7-over-global-top7-ratio 1.01
```

## 2) Preflight (temperature top9 guard)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v107_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_top7_ratio_top9_uniform_v107 \
  --fail-on-missing-run-id \
  --print-selection \
  --preflight-markdown \
  --require-prompt-bank-version v10.7 \
  --max-planned-sample-temperature-top8-share 0.99 \
  --max-planned-sample-temperature-top9-share 1.00 \
  --max-planned-sample-temperature-top8-over-uniform-ratio 1.25 \
  --max-planned-sample-temperature-top9-over-uniform-ratio 1.20 \
  --manifest-note "preflight v107 unknown-year top7 + temperature top9 guard"
```

## 3) Smoke execution

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v107_exec \
  --include-run-id screening_prompt_runner_top7_ratio_top9_uniform_v107 \
  --fail-on-missing-run-id \
  --manifest-markdown \
  --max-runs 1 \
  --max-retries 1 \
  --max-generation-retries 1 \
  --max-analysis-retries 0 \
  --generation-timeout-seconds 120 \
  --analysis-timeout-seconds 90 \
  --max-run-seconds 180 \
  --continue-on-error
```
