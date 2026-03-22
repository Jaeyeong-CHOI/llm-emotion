# Reproducibility Playbook (v6.0)

## 목적
- 선행연구 스크리닝에서 **counterexample은 있는데 bridge signal이 비는 비율**(`review_counterexample_without_bridge_share`)을 상한 게이트로 차단.
- 프롬프트 뱅크 v6.0 확장(교차 쿼리 합의 복구 / countervoice temperature ladder / runner live gap tripwire) 고정.
- 실험 러너에서 run-id별 단계 점유율 격차뿐 아니라 **stage total attempt gap**까지 tripwire로 통제.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v60 \
  --max-review-bridge-counterexample-traceability-gap-share 0.45 \
  --max-review-counterexample-without-bridge-share 0.35 \
  --max-manual-qc-review-evidence-link-decay-share 0.45
```

핵심: `review_counterexample_without_bridge_share`가 상한을 넘으면 반례 근거가 bridge와 연결되지 않은 review 표본이 많다는 뜻으로 즉시 재검토.

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
assert bank['version']=='v6.0', bank['version']
for sid in [
  'screening_crossquery_consensus_repair',
  'prompt_bank_countervoice_temperature_ladder',
  'runner_live_stage_gap_tripwire',
]:
  assert any(s.get('id')==sid for s in bank.get('scenarios', [])), sid
for pid in ['crossquery_consensus_moderator','live_budget_tripwire_operator']:
  assert any(p.get('id')==pid for p in bank.get('personas', [])), pid
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight (실행 전 가드)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v60_preflight \
  --plan-only \
  --include-run-id screening_prompt_runner_live_gap_v60 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v6.0 \
  --max-stage-attempt-share-gap-per-run-id 0.35 \
  --max-stage-total-attempt-gap-share 0.30 \
  --manifest-markdown
```

## 4) 스모크 실행
```bash
printf '%s\n' screening_prompt_runner_live_gap_v60 > /tmp/llm_emotion_run_ids_v60_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v60_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v60_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --continue-on-error \
  --max-failed-cells 1 \
  --max-stage-attempt-share-gap-per-run-id 0.6 \
  --max-stage-total-attempt-gap-share 0.55 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
