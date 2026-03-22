# Reproducibility Playbook (v6.4)

## 목적
- 스크리닝 품질 게이트에 **dedup 안정성 점검**(`manual_qc_dedup_label_conflict_share`, `manual_qc_dedup_score_range_alert_share`)을 추가해, 수동 QC 큐에서 병합 불안정성이 누적되는 상황을 조기 차단.
- 프롬프트 뱅크 `v6.4` 확장(중복 충돌 triage / scenario-label coverage rebalance / preflight guardrail 시나리오·페르소나).
- 실험 러너에 **scenario label coverage guardrail**(`--require-min-unique-scenario-labels`, `--require-min-selected-scenario-labels`)을 추가해 태그 수는 충분하지만 label 축이 편향된 배치를 사전에 차단.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v64 \
  --max-manual-qc-dedup-label-conflict-share 0.20 \
  --min-dedup-score-range-alert 1.0 \
  --max-manual-qc-dedup-score-range-alert-share 0.20 \
  --max-manual-qc-review-evidence-link-decay-share 0.45
```

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
matrix=json.loads(Path('ops/experiment_matrix.json').read_text(encoding='utf-8'))
assert bank['version']=='v6.4', bank['version']
for sid in [
  'screening_dedup_conflict_triage',
  'prompt_bank_label_coverage_rebalance',
  'runner_scenario_label_guardrail',
]:
  assert any(s.get('id')==sid for s in bank.get('scenarios', [])), sid
for pid in ['dedup_conflict_auditor','label_coverage_rebalancer','scenario_label_guard_operator']:
  assert any(p.get('id')==pid for p in bank.get('personas', [])), pid
assert any(run.get('id')=='screening_dedup_label_guard_v64' for run in matrix.get('runs', []))
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v64_preflight \
  --plan-only \
  --include-run-id screening_dedup_label_guard_v64 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v6.4 \
  --require-min-unique-scenario-labels 3 \
  --require-min-selected-scenario-labels 3 \
  --manifest-markdown
```

## 4) 스모크 실행
```bash
printf '%s\n' screening_dedup_label_guard_v64 > /tmp/llm_emotion_run_ids_v64_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v64_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v64_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --continue-on-error \
  --max-failed-cells 1 \
  --require-min-unique-scenario-labels 3 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/preflight.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
