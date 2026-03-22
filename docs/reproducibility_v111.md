# Reproducibility v111

## 변경 목적
- 스크리닝 품질: unknown-year review known-query에서 query-group **coverage/entropy floor**를 강제해, top-share 지표만 통과하는 편향 케이스를 조기 차단.
- 프롬프트 뱅크: v11.1로 확장해 unknown-year group entropy 복구 및 stage-timeout 운영 시나리오 보강.
- 실험 러너: timeout 편중을 전체가 아닌 stage별(generation/analysis)로 분해해 **timeout-over-selection ratio** 가드 추가.

## 핵심 변경
1. `scripts/check_screening_quality.py`
   - 신규 인자
     - `--min-manual-qc-review-traceable-known-query-unknown-year-group-coverage` (default: 2)
     - `--min-manual-qc-review-traceable-known-query-unknown-year-group-entropy` (default: 0.35)
   - 신규 게이트
     - `manual_qc_review_traceable_known_query_unknown_year_group_coverage_floor`
     - `manual_qc_review_traceable_known_query_unknown_year_group_entropy_floor`

2. `prompts/prompt_bank_ko.json`
   - 버전 `v11.1`로 갱신
   - 시나리오 3개 추가
     - `screening_unknown_year_group_entropy_floor_patch_v111`
     - `prompt_bank_unknown_year_group_entropy_countervoice_patch_v111`
     - `runner_stage_timeout_ratio_tripwire_v111`
   - 페르소나 1개 추가
     - `timeout_stage_ratio_guardian_v111`

3. `scripts/run_experiments.py`
   - 신규 인자
     - `--max-generation-timeout-failure-over-selection-ratio-per-run-id`
     - `--max-analysis-timeout-failure-over-selection-ratio-per-run-id`
   - stage별 timeout 실패 집계(generation/analysis)를 분리하고 budget violation에 반영.

## 재현 커맨드
```bash
python3 -m py_compile scripts/check_screening_quality.py scripts/run_experiments.py

python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out /tmp/screening_quality_report_v111.json \
  --out-md /tmp/screening_quality_report_v111.md \
  --run-label screening_qc_v111_smoke \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-coverage 2 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-entropy 0.35

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v111_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_metadata_entropy_v77 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v11.1 \
  --max-timeout-failure-over-selection-ratio-per-run-id 1.6 \
  --max-generation-timeout-failure-over-selection-ratio-per-run-id 1.8 \
  --max-analysis-timeout-failure-over-selection-ratio-per-run-id 1.8
```
