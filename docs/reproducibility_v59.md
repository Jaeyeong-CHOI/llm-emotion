# Reproducibility Playbook (v5.9)

## 목적
- 선행연구 스크리닝에서 `bridge × counterexample` 근거가 있어도 traceability가 비는 구간을 상한 게이트로 차단.
- 프롬프트 뱅크 v5.9 확장(bridge-counterexample density / countervoice calibration grid / runner stage-share gap) 고정.
- 실험 러너에서 run-id별 생성/분석 단계 시도 점유율 격차를 tripwire로 통제.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v59 \
  --max-review-bridge-counterexample-traceability-gap-share 0.45 \
  --max-manual-qc-review-evidence-link-decay-share 0.45
```

핵심: `review_bridge_counterexample_traceability_gap_share`가 상한을 넘으면 review 근거 밀도 부족으로 즉시 재검토.

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
assert bank['version']=='v5.9', bank['version']
for sid in [
  'screening_bridge_counterexample_density_repair',
  'prompt_bank_countervoice_calibration_grid',
  'runner_stage_share_gap_throttle',
]:
  assert any(s.get('id')==sid for s in bank.get('scenarios', [])), sid
for pid in ['review_density_auditor','stage_share_gap_controller']:
  assert any(p.get('id')==pid for p in bank.get('personas', [])), pid
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight (실행 전 가드)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v59_preflight \
  --plan-only \
  --include-run-id screening_prompt_runner_gap_v59 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v5.9 \
  --max-stage-attempt-share-gap-per-run-id 0.35 \
  --manifest-markdown
```

## 4) 스모크 실행
```bash
printf '%s\n' screening_prompt_runner_gap_v59 > /tmp/llm_emotion_run_ids_v59_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v59_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v59_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --continue-on-error \
  --max-failed-cells 1 \
  --max-stage-attempt-share-gap-per-run-id 0.6 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
