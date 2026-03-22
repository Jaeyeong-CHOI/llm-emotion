# Reproducibility Playbook (v6.3)

## 목적
- 스크리닝 품질 게이트에 **review traceability + unknown query 상한**(`manual_qc_review_traceable_unknown_query_share`)을 추가해, 근거 문장은 있으나 source query가 비는 review 표본을 조기 차단.
- 프롬프트 뱅크 `v6.3` 확장(이유쌍 traceability / countervoice stress-test / stage-share circuit-breaker 시나리오·페르소나).
- 실험 러너에 **stage attempt share guardrail**(`--max-generation-attempt-share-per-run-id`, `--max-analysis-attempt-share-per-run-id`)을 추가해 단계별 점유율 과열을 fail-fast 제어.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v63 \
  --min-manual-qc-review-traceable-known-query-share 0.55 \
  --max-manual-qc-review-traceable-unknown-query-share 0.15 \
  --max-review-counterexample-without-bridge-share 0.35 \
  --max-manual-qc-review-evidence-link-decay-share 0.45
```

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
assert bank['version']=='v6.3', bank['version']
for sid in [
  'screening_conflict_reason_pairing_repair',
  'prompt_bank_countervoice_pressure_test',
  'runner_stage_attempt_share_circuit_breaker',
]:
  assert any(s.get('id')==sid for s in bank.get('scenarios', [])), sid
for pid in ['reason_pair_traceability_keeper','countervoice_stress_tester','stage_share_circuit_operator']:
  assert any(p.get('id')==pid for p in bank.get('personas', [])), pid
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v63_preflight \
  --plan-only \
  --include-run-id screening_prompt_runner_circuit_v63 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v6.3 \
  --max-generation-attempt-share-per-run-id 0.7 \
  --max-analysis-attempt-share-per-run-id 0.7 \
  --manifest-markdown
```

## 4) 스모크 실행
```bash
printf '%s\n' screening_prompt_runner_circuit_v63 > /tmp/llm_emotion_run_ids_v63_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v63_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v63_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --continue-on-error \
  --max-failed-cells 1 \
  --max-generation-attempt-share-per-run-id 1.0 \
  --max-analysis-attempt-share-per-run-id 1.0 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
