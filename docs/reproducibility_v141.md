# Reproducibility v141

## 변경 요약
1. **선행연구 스크리닝 품질 개선**
   - `queries/screening_rules.json`에 선행연구 검증 신호를 강화하는 규칙어를 추가했습니다.
     - `analysis plan`, `search strategy`, `analysis pipeline`, `sensitivity analysis`, `data availability statement`
   - `review_priority_any`에도 `analysis reproducibility`, `registered protocol compliance`를 보강해 추적성 신호를 강화했습니다.
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전을 `v139.0`에서 `v141.0`으로 상향.
   - 시나리오 3개(`screening_unknown_year_group_top27_entropy_stability_v141`, `prompt_bank_countervoice_protocol_trace_mesh_v141`, `runner_temperature_p99_p25_reprolock_tripwire_v141`) 추가.
   - 페르소나 3개(`unknown_year_group_top27_entropy_steward_v141`, `protocol_trace_countervoice_curator_v141`, `p99_p25_reprolock_operator_v141`) 추가.
   - `ops/experiment_matrix.json`에 `screening_prompt_runner_unknown_year_group_top27_temperature_p99_p25_v141` 러너 스모크 ID 추가.
3. **실험 러너 고도화**
   - `scripts/run_experiments.py`에 `--max-planned-sample-temperature-p99-over-p25-share-ratio`를 추가해 계획 수립 전(preflight)에서 p99/p25 비율까지 감시.
   - preflight summary/마크다운/config snapshot에 새 지표를 기록.
4. **실모델 전환 준비(선행 단계)**
   - 스모크에서 `p99/p25`와 `top27` 쿼리-그룹 안정화까지 검증하도록 조건을 넣어, 실배치 전 가드 조건 후보를 하나 더 좁힘.


### v141 추가 변경
1. **선행연구 스크리닝 품질 개선**
   - `scripts/check_screening_quality.py`에 `--min-review-method-cue-share` 게이트를 추가.
   - review 큐에서 `method_cues=` 토큰 비율이 낮을 경우 즉시 경고/실패하도록 강화.
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전을 `v141.0`으로 상향.
   - 시나리오 3개 추가: `screening_query_bridge_method_audit_v141`, `prompt_bank_batch_diversification_v141`, `runner_real_model_transition_preflight_v141`
   - persona 2개 추가: `screening_method_audit_caretaker_v141`, `real_model_governor_v141`
3. **실험 러너 고도화**
   - `scripts/run_experiments.py`에 실모델 전환 준비용 preflight 옵션 추가:
     - `--require-live-model`
     - `--required-live-model-env`
   - preflight JSON/manifest/markdown에 위 설정 및 점검 결과를 기록.
4. **실모델 본실험 전환 준비**
   - `--require-live-model`을 켜고 실제 키를 지정해 `--required-live-model-env`로 실행 전 누락 변수를 강제할 수 있는 체크라인을 추가.

## 재현성 규약
- preflight는 freeze artifact(`--repro-lock-json`)와 함께 실행하며, 결과 디렉터리의 selection report/lock를 함께 고정합니다.
- 온도 분포 가드는 `p99/p40`, `p99/p35`, `p99/p30`, `p99/p25`를 모두 기록/점검하도록 확장.

## 실행 예시
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v141 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top24-over-global-group-top24-ratio 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-hhi 0.32 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-effective-count 3.4

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v141_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top27_temperature_p99_p25_v141 \
  --fail-on-missing-run-id \
  --selection-report results/selection_report_smoke_v141.json \
  --selection-csv results/selection_report_smoke_v141.csv \
  --repro-lock-json results/selection_report_smoke_v141.lock.json \
  --preflight-markdown \
  --require-prompt-bank-version v141.0 \
  --require-live-model \
  --required-live-model-env OPENAI_API_KEY,OPENAI_ORG_ID \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --max-planned-sample-temperature-p99-over-p40-share-ratio 1.08 \
  --max-planned-sample-temperature-p99-over-p35-share-ratio 1.12 \
  --max-planned-sample-temperature-p99-over-p30-share-ratio 1.16 \
  --max-planned-sample-temperature-p99-over-p25-share-ratio 1.20 \
  --manifest-note "preflight v141 top27 entropy stability + p99/p25 repro-lock guard"
```

## 검증 명령
```bash
python3 -m json.tool queries/screening_rules.json >/dev/null
python3 -m json.tool prompts/prompt_bank_ko.json >/dev/null
python3 -m json.tool ops/experiment_matrix.json >/dev/null
python3 -m py_compile scripts/run_experiments.py
```