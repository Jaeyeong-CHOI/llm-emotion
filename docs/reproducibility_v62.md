# Reproducibility Playbook (v6.2)

## 목적
- 스크리닝 품질 게이트에 **review traceability + known query 결합 하한**(`manual_qc_review_traceable_known_query_share`)을 추가해, 근거 문장은 있으나 쿼리 출처가 비는 review 표본을 fail-fast 차단.
- 프롬프트 뱅크 `v6.2` 확장(스크리닝 query-traceability 보강 + retry pressure 운영 시나리오/페르소나).
- 실험 러너에 **retry pressure guardrail**(`--max-retry-share-per-run-id`, `--max-retry-over-selection-ratio`)을 추가해 특정 run id의 재시도 과열을 통제.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v62 \
  --min-manual-qc-review-traceable-known-query-share 0.55 \
  --max-review-counterexample-without-bridge-share 0.35 \
  --max-manual-qc-review-evidence-link-decay-share 0.45
```

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
assert bank['version']=='v6.2', bank['version']
for sid in [
  'screening_review_query_traceability_patch',
  'prompt_bank_evidence_anchor_recovery_drill',
  'runner_retry_pressure_rebalance',
]:
  assert any(s.get('id')==sid for s in bank.get('scenarios', [])), sid
for pid in ['review_query_traceability_auditor','retry_pressure_balancer']:
  assert any(p.get('id')==pid for p in bank.get('personas', [])), pid
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v62_preflight \
  --plan-only \
  --include-run-id screening_prompt_runner_retry_pressure_v62 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v6.2 \
  --max-retry-share-per-run-id 0.6 \
  --max-retry-over-selection-ratio 1.8 \
  --manifest-markdown
```

## 4) 스모크 실행
```bash
printf '%s\n' screening_prompt_runner_retry_pressure_v62 > /tmp/llm_emotion_run_ids_v62_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v62_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v62_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --continue-on-error \
  --max-failed-cells 1 \
  --max-retry-share-per-run-id 1.0 \
  --max-retry-over-selection-ratio 2.2 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
