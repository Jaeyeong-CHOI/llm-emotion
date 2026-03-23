# Reproducibility v127

## 변경 범위
- 스크리닝 품질: `scripts/check_screening_quality.py`에 unknown-year query-group **top18 절대/글로벌 비율 가드** 추가
- 프롬프트 뱅크: `v127.0`으로 갱신하고 top18 countervoice mesh 시나리오·페르소나 추가
- 실험 러너: `scripts/run_experiments.py` preflight에 **p99/p80 temperature ratio 가드**(`--max-planned-sample-temperature-p99-over-p80-share-ratio`) 추가
- 스크리닝 규칙: `queries/screening_rules.json`에 decision affect theory / post-decisional regret / regulation flexibility 및 micro-longitudinal method cue 확장

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
  --out results/screening_quality_report_v127.json \
  --out-md results/screening_quality_report_v127.md \
  --run-label screening_qc_v127 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top18-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top18-over-global-group-top18-ratio 1.0

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v127_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top18_temperature_p99_p80_v127 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v127.json \
  --selection-csv results/selection_report_smoke_v127.csv \
  --preflight-markdown \
  --require-prompt-bank-version v127.0 \
  --max-planned-sample-temperature-p99-over-p80-share-ratio 1.10 \
  --manifest-note "preflight v127 unknown-year group top18 + temperature p99/p80 guard"
```

## 기대 산출물
- `results/screening_quality_report_v127.json`
- `results/screening_quality_report_v127.md`
- `results/selection_report_smoke_v127.json`
- `results/selection_report_smoke_v127.csv`
- `results/experiments/smoke_v127_plan/preflight.json`
- `results/experiments/smoke_v127_plan/preflight.md`
- `results/experiments/smoke_v127_plan/manifest.json`
