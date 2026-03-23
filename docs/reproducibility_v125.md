# Reproducibility v125

## 변경 범위
- 스크리닝 품질: `scripts/check_screening_quality.py`에 unknown-year query-group **top16 절대/글로벌 비율 가드** 추가
- 프롬프트 뱅크: `v125.0`으로 갱신하고 top16 tail countervoice 보강 시나리오·페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p90 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p90-share-ratio`) 추가

## 실행 커맨드
```bash
python3 -m py_compile scripts/run_experiments.py scripts/check_screening_quality.py scripts/generate_dataset.py

python3 - <<'PY'
import json, pathlib
for path in ['prompts/prompt_bank_ko.json','ops/experiment_matrix.json']:
    json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    print(f'validated {path}')
PY

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v125_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top16_temperature_p99_p90_v125 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v125.json \
  --selection-csv results/selection_report_smoke_v125.csv \
  --preflight-markdown \
  --require-prompt-bank-version v125.0 \
  --max-planned-sample-temperature-p99-over-p90-share-ratio 1.08 \
  --manifest-note "preflight v125 unknown-year group top16 backstop + temperature p99/p90 guard"
```

## 기대 산출물
- `results/selection_report_smoke_v125.json`
- `results/selection_report_smoke_v125.csv`
- `results/experiments/smoke_v125_plan/preflight.json`
- `results/experiments/smoke_v125_plan/preflight.md`
- `results/experiments/smoke_v125_plan/manifest.json`
