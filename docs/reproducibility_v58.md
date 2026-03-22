# Reproducibility Playbook (v5.8)

## 목적
- 선행연구 스크리닝 품질에서 review 근거의 `bridge × counterexample` 결합 신호를 추가로 검증.
- 프롬프트 뱅크 v5.8 확장(temporal recall / countervoice strength ladder / runner re-entry cascade)을 재현 가능한 방식으로 고정.
- 실험 러너에서 run-id 단위 stage failure streak 가드를 명시적으로 점검.

## 1) Screening 품질 재현 점검
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v58 \
  --min-review-bridge-counterexample-coupled-share 0.18 \
  --min-review-bridge-counterexample-traceable-share 0.12
```

핵심: review 라벨에서 bridge signal과 counterexample signal이 같이 존재하는 비율(`review_bridge_counterexample_coupled_share`)과 추적 가능한 결합 비율을 함께 본다.

## 2) Prompt-bank/Matrix 고정 확인
```bash
python3 - <<'PY'
import json
from pathlib import Path
bank=json.loads(Path('prompts/prompt_bank_ko.json').read_text(encoding='utf-8'))
assert bank['version']=='v5.8', bank['version']
for sid in [
  'screening_temporal_counterexample_backfill',
  'prompt_bank_countervoice_strength_ladder',
  'runner_stage_reentry_budget_cascade',
]:
  assert any(s.get('id')==sid for s in bank.get('scenarios', [])), sid
print('prompt_bank_version=', bank['version'])
PY
```

## 3) Runner preflight (실행 전 가드)
```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v58_preflight \
  --plan-only \
  --include-run-id screening_prompt_runner_temporal_v58 \
  --fail-on-missing-run-id \
  --require-prompt-bank-version v5.8 \
  --max-generation-failure-streak-per-run-id 1 \
  --max-analysis-failure-streak-per-run-id 1 \
  --max-failure-streak-per-run-id 1 \
  --manifest-markdown
```

## 4) 스모크 실행
```bash
printf '%s\n' screening_prompt_runner_temporal_v58 > /tmp/llm_emotion_run_ids_v58_exec.txt
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label repro_v58_smoke \
  --run-id-file /tmp/llm_emotion_run_ids_v58_exec.txt \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --max-retries 1 \
  --max-failed-cells 1 \
  --continue-on-error \
  --max-generation-failure-streak-per-run-id 1 \
  --max-analysis-failure-streak-per-run-id 1 \
  --max-failure-streak-per-run-id 1 \
  --manifest-markdown
```

## 산출물 확인
- `results/experiments/<run_label>/manifest.json`
- `results/experiments/<run_label>/preflight.json`
- `results/experiments/<run_label>/budget_report.json`
- `results/screening_quality_report.json`
