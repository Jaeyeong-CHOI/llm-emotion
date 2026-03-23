# Reproducibility v124

## 변경 범위
- 스크리닝 규칙: `queries/screening_rules.json`에 affective forecasting/anticipated regret/emotion regulation/emotional granularity alias 및 method cue 강화
- 프롬프트 뱅크: `v124.0`로 갱신하고 top16 countervoice + p99/p95 tripwire 대응 scenario·persona 추가
- 실험 러너: `--max-planned-sample-temperature-p99-over-p95-share-ratio` preflight 가드 추가

## 실행 커맨드
```bash
python3 -m py_compile scripts/run_experiments.py scripts/check_screening_quality.py scripts/generate_dataset.py

python3 - <<'PY'
import json, pathlib
for path in ['queries/screening_rules.json','prompts/prompt_bank_ko.json','ops/experiment_matrix.json']:
    json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    print(f'validated {path}')
PY

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v124_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top16_temperature_p99_p95_v124 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v124.json \
  --selection-csv results/selection_report_smoke_v124.csv \
  --preflight-markdown \
  --require-prompt-bank-version v124.0 \
  --max-planned-sample-temperature-p99-over-p95-share-ratio 1.0 \
  --manifest-note "preflight v124 unknown-year group top16 + temperature p99/p95 guard"
```

## 기대 산출물
- `results/selection_report_smoke_v124.json`
- `results/selection_report_smoke_v124.csv`
- `results/experiments/smoke_v124_plan/preflight.json`
- `results/experiments/smoke_v124_plan/preflight.md`
- `results/experiments/smoke_v124_plan/manifest.json`
