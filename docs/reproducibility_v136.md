# Reproducibility v136

## 변경 요약
1. **선행연구 스크리닝 품질**
   - `scripts/check_screening_quality.py`에 unknown-year query-group `HHI` ceiling과 `effective_count` floor를 추가했습니다.
   - `queries/screening_rules.json`에 `construct validity`, `many-analyst`, `open data`, `emotion schema` 용어군과 방법론 cue를 보강했습니다.
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전: `v135.0 -> v136.0`
   - 시나리오 3개(`screening_unknown_year_group_hhi_guard_v136`, `prompt_bank_repro_countervoice_mesh_v136`, `runner_repro_lock_freeze_guard_v136`)와 페르소나 3개를 추가했습니다.
   - `ops/experiment_matrix.json`에 `screening_prompt_runner_unknown_year_group_hhi_repro_lock_v136` 스모크 런을 추가했습니다.
3. **실험 러너 고도화**
   - `scripts/run_experiments.py`에 `--repro-lock-json` 옵션을 추가했습니다.
   - `require_freeze_artifact` 검증 결과에 `sha256`, `bytes`, `mtime_utc`를 기록하도록 확장했습니다.

## 재현성 규약
- screening quality report는 top-N 누적 비율뿐 아니라 unknown-year query-group `HHI`와 `effective_count`를 함께 기록해야 합니다.
- experiment plan 단계에서는 `selection_report(.json/.csv)`와 함께 `repro_lock.json`을 남겨, 선택된 run-id/row/snapshot hash/freeze artifact digest를 한 번에 보존합니다.
- `manifest_note`는 실험 의도와 우회 사유를 간결하게 남기고, lock artifact에도 동일 문자열이 복제됩니다.

## 실행 예시
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v136 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-hhi 0.34 \
  --min-manual-qc-review-traceable-known-query-unknown-year-group-effective-count 3.2

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v136_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_hhi_repro_lock_v136 \
  --fail-on-missing-run-id \
  --selection-report results/selection_report_smoke_v136.json \
  --selection-csv results/selection_report_smoke_v136.csv \
  --repro-lock-json results/selection_report_smoke_v136.lock.json \
  --preflight-markdown \
  --require-prompt-bank-version v136.0 \
  --require-freeze-artifact refs/openalex_results.jsonl \
  --require-freeze-artifact results/lit_search_report.json \
  --require-freeze-artifact results/screening_quality_report.json \
  --manifest-note "preflight v136 unknown-year group HHI + repro lock"
```

## 기대 산출물
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`
- `results/selection_report_smoke_v136.json`
- `results/selection_report_smoke_v136.csv`
- `results/selection_report_smoke_v136.lock.json`
- `results/experiments/smoke_v136_plan/manifest.json`

## 검증 명령
```bash
python3 -m json.tool queries/screening_rules.json >/dev/null
python3 -m json.tool prompts/prompt_bank_ko.json >/dev/null
python3 -m json.tool ops/experiment_matrix.json >/dev/null
python3 -m py_compile scripts/check_screening_quality.py scripts/run_experiments.py
```
