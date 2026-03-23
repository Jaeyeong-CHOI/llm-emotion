# Reproducibility Note — v141.4

## Scope
- Core-set refinement: recency/method-cue balanced selection policy로 `ops/core_set.json` 재생성(32편).
- Prompt bank expansion: `prompts/prompt_bank_ko.json` -> `v141.4` (scenario 3 + persona 1).
- Real-model transition prep: ENV contract 점검 강화(`check_real_model_readiness.py` 개선).

## Validation
```bash
python3 -m py_compile scripts/check_real_model_readiness.py scripts/run_experiments.py scripts/check_screening_quality.py
python3 scripts/check_real_model_readiness.py
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v1414_plan --plan-only --include-run-id screening_prompt_runner_core_set_recency_env_contract_v1414 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v1414.json --selection-csv results/selection_report_smoke_v1414.csv --preflight-markdown --require-prompt-bank-version v141.4 --max-planned-sample-temperature-p99-over-p25-share-ratio 1.2
```

## Expected
- plan-only preflight 성공
- prompt_bank version mismatch 없음
- readiness 결과에서 미설정 env 명시
