# Reproducibility v137

## 변경 요약
1. **선행연구 스크리닝 품질**
   - `queries/screening_rules.json`에 `risk of bias`, `prisma`, `evidence synthesis` 용어군과 방법론 cue(`risk of bias assessment`, `prisma flow diagram`, `systematic evidence synthesis`)를 추가했습니다.
   - unknown-year query-group 점검에서 top-N 비율만으로 통과시키지 않도록 HHI/entropy/effective-count 동시 점검 시나리오를 prompt bank에 반영했습니다.
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전: `v136.0 -> v137.0`
   - 시나리오 3개(`screening_unknown_year_group_hhi_entropy_ratio_v137`, `prompt_bank_countervoice_evidence_synthesis_mesh_v137`, `runner_temperature_p99_p40_reprolock_tripwire_v137`)와 페르소나 3개를 추가했습니다.
   - `ops/experiment_matrix.json`에 `screening_prompt_runner_unknown_year_group_hhi_p99_p40_reprolock_v137` 스모크 런을 추가했습니다.
3. **실험 러너 고도화**
   - `scripts/run_experiments.py`에 `--max-planned-sample-temperature-p99-over-p40-share-ratio` preflight tripwire를 추가했습니다.
   - preflight summary/markdown/config snapshot에 `planned_sample_temperature_p99_over_p40_share_ratio`를 기록해 재현 가능한 fail-fast 근거를 남기도록 확장했습니다.

## 재현성 규약
- screening QC는 unknown-year query-group의 top-N 비율뿐 아니라 `HHI`, `entropy`, `effective_count`를 동시에 기록합니다.
- experiment preflight에서는 `--repro-lock-json`을 함께 사용해 selection row/snapshot hash/freeze artifact digest를 lock artifact로 고정합니다.
- temperature guard는 `p99/p45`와 `p99/p40`를 함께 기록해 상단 tail 가속을 조기에 차단합니다.

## 실행 예시
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v137 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-over-global-group-top24-ratio 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-hhi 0.33 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-effective-count 3.3

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v137_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_hhi_p99_p40_reprolock_v137 \
  --fail-on-missing-run-id \
  --selection-report results/selection_report_smoke_v137.json \
  --selection-csv results/selection_report_smoke_v137.csv \
  --repro-lock-json results/selection_report_smoke_v137.lock.json \
  --preflight-markdown \
  --require-prompt-bank-version v137.0 \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --max-planned-sample-temperature-p99-over-p45-share-ratio 1.05 \
  --max-planned-sample-temperature-p99-over-p40-share-ratio 1.08 \
  --manifest-note "preflight v137 unknown-year group hhi+entropy + p99/p40 repro-lock guard"
```

## 검증 명령
```bash
python3 -m json.tool queries/screening_rules.json >/dev/null
python3 -m json.tool prompts/prompt_bank_ko.json >/dev/null
python3 -m json.tool ops/experiment_matrix.json >/dev/null
python3 -m py_compile scripts/run_experiments.py
```
