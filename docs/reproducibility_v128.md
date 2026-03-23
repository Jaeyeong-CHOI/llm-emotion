# Reproducibility v128

## 변경 범위
- 스크리닝 품질: `scripts/check_screening_quality.py`에 unknown-year query-group **top19 절대/글로벌 비율 가드** 추가
- 프롬프트 뱅크: `v128.0`으로 갱신하고 top19 countervoice mesh 시나리오·페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p75 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p75-share-ratio`) 추가
- 스크리닝 규칙: `queries/screening_rules.json`에 affective forecasting bias / impact bias / emotion regulation choice / regulatory flexibility alias와 pre-registered study / within-subject design / measurement invariance method cue 확장

## 실행 커맨드
```bash
python3 -m py_compile scripts/run_experiments.py scripts/check_screening_quality.py scripts/generate_dataset.py scripts/search_openalex.py

python3 - <<'PY'
import json, pathlib
for path in ['prompts/prompt_bank_ko.json','ops/experiment_matrix.json','queries/screening_rules.json']:
    json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    print(f'validated {path}')
PY

python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v128.json \
  --out-md results/screening_quality_report_v128.md \
  --run-label screening_qc_v128 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top19-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top19-over-global-group-top19-ratio 1.0

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v128_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top19_temperature_p99_p75_v128 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v128.json \
  --selection-csv results/selection_report_smoke_v128.csv \
  --preflight-markdown \
  --require-prompt-bank-version v128.0 \
  --max-planned-sample-temperature-p99-over-p75-share-ratio 1.10 \
  --manifest-note "preflight v128 unknown-year group top19 + temperature p99/p75 guard"
```

## 기대 산출물
- `results/screening_quality_report_v128.json`
- `results/screening_quality_report_v128.md`
- `results/selection_report_smoke_v128.json`
- `results/selection_report_smoke_v128.csv`
- `results/experiments/smoke_v128_plan/preflight.json`
- `results/experiments/smoke_v128_plan/preflight.md`
- `results/experiments/smoke_v128_plan/manifest.json`

## 실행 결과
- `py_compile`: 통과
- JSON 검증: `prompts/prompt_bank_ko.json`, `ops/experiment_matrix.json`, `queries/screening_rules.json` 모두 로드 성공
- `check_screening_quality.py`: 산출물 생성 성공, 기존 로컬 데이터 기준 `status=review`, `quality_score=0.0`, `unknown_year_group_top19_share=0.0`, `unknown_year_group_top19_over_global_group_top19_ratio=0.0`
- `run_experiments.py --plan-only`: 산출물 생성 성공, `selected_run_id_count=1`, `planned_sample_temperature_top3_share=0.75`, `planned_sample_temperature_p99_over_p75_share_ratio=1.0`
