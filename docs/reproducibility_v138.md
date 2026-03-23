# Reproducibility v138

## 변경 요약
1. **선행연구 스크리닝 품질**
   - `queries/screening_rules.json`에 `emotion causality`, `counterfactual explanation`, `regret sensitivity`, `emotion robustness`, `evidence triangulation` alias를 추가했습니다.
   - review/method cue에 `registered protocol`, `protocol deviation`, `reporting bias`, `triangulation`, `replication package`를 보강해 방법론 근거 추적 신호를 강화했습니다.
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전: `v137.0 -> v138.0`
   - 시나리오 3개(`screening_unknown_year_group_top25_entropy_backstop_v138`, `prompt_bank_countervoice_protocol_bias_mesh_v138`, `runner_temperature_p99_p35_reprolock_tripwire_v138`)와 페르소나 3개를 추가했습니다.
   - `ops/experiment_matrix.json`에 `screening_prompt_runner_unknown_year_group_top25_p99_p35_v138` 스모크 런을 추가했습니다.
3. **실험 러너 고도화**
   - `scripts/run_experiments.py`에 `--max-planned-sample-temperature-p99-over-p35-share-ratio` preflight tripwire를 추가했습니다.
   - preflight summary/markdown/config snapshot에 `planned_sample_temperature_p99_over_p35_share_ratio`를 기록하도록 확장했습니다.

## 재현성 규약
- screening 규칙은 query-group 집중 완화와 함께 protocol/reporting bias 신호를 병행 추적합니다.
- experiment preflight에서는 `--repro-lock-json`을 함께 사용해 selection row/snapshot hash/freeze artifact digest를 lock artifact로 고정합니다.
- temperature guard는 `p99/p45`, `p99/p40`, `p99/p35`를 함께 기록해 상단 tail 가속을 조기 차단합니다.

## 실행 예시
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v138 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-over-global-group-top24-ratio 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-hhi 0.33 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-effective-count 3.3

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v138_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top25_p99_p35_v138 \
  --fail-on-missing-run-id \
  --selection-report results/selection_report_smoke_v138.json \
  --selection-csv results/selection_report_smoke_v138.csv \
  --repro-lock-json results/selection_report_smoke_v138.lock.json \
  --preflight-markdown \
  --require-prompt-bank-version v138.0 \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --max-planned-sample-temperature-p99-over-p45-share-ratio 1.05 \
  --max-planned-sample-temperature-p99-over-p40-share-ratio 1.08 \
  --max-planned-sample-temperature-p99-over-p35-share-ratio 1.12 \
  --manifest-note "preflight v138 top25 entropy backstop + p99/p35 repro-lock guard"
```

## 검증 명령
```bash
python3 -m json.tool queries/screening_rules.json >/dev/null
python3 -m json.tool prompts/prompt_bank_ko.json >/dev/null
python3 -m json.tool ops/experiment_matrix.json >/dev/null
python3 -m py_compile scripts/run_experiments.py
```
