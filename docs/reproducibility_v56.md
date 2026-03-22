# Reproducibility Playbook (v5.5)

## 목적
- screening quality gate, prompt-bank 버전, runner preflight를 같은 체크리스트로 재실행 가능하게 고정.
- 실행 전에 실패해야 할 조건(guardrail)을 먼저 검증해 재실행 비용을 줄임.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v56 \
  --min-review-bridge-traceability-given-bridge-share 0.70 \
  --min-review-counterexample-share 0.25
```

핵심: `review_bridge_traceability_given_bridge_share`, `review_counterexample_share`가 review subset에서 기준을 만족하는지 확인.

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
assert bank['version']=='v5.5', bank['version']
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight (실행 전 가드)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v56_preflight \
  --plan-only \
  --include-run-id screening_prompt_runner_counterexample_v56 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v5.5 \
  --require-min-successful-cells-per-run-id 1 \
  --max-failure-streak-per-run-id 1 \
  --manifest-markdown
```

> `--plan-only`에서도 coverage, 버전, run-id 무결성 체크는 수행됨.

## 4) 스모크 실행
```bash
printf '%s\n' screening_prompt_runner_counterexample_v56 > /tmp/llm_emotion_run_ids_v56_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v56_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v56_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-failed-cells 1 \
  --continue-on-error \
  --require-min-successful-cells-per-run-id 1 \
  --max-failure-streak-per-run-id 1 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/preflight.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
