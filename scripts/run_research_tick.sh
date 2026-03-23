#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion"
cd "$ROOT"

if [ -f .env.real_model ]; then
  set -a
  # shellcheck disable=SC1090
  source .env.real_model
  set +a
else
  echo "[tick] .env.real_model not found; skip" >&2
  exit 0
fi

refresh_status() {
  python3 scripts/update_live_status.py >/tmp/research_tick_status.log 2>&1 || true
  python3 scripts/research_status.py >/tmp/research_tick_research_status.log 2>&1 || true
}

echo "[tick] $(date -u +'%Y-%m-%dT%H:%M:%SZ') start"

READY_LINE="$(python3 scripts/check_real_model_readiness.py | tr -d '\r' | head -n 1)"
if [[ "$READY_LINE" != "ready=true" ]]; then
  echo "[tick] readiness=${READY_LINE}; skip execution"
  refresh_status
  exit 0
fi

QUEUE_FILE="ops/continuous_run_ids.txt"
if [ ! -f "$QUEUE_FILE" ] || [ ! -s "$QUEUE_FILE" ]; then
  echo "[tick] no queued run-id; skip"
  refresh_status
  exit 0
fi

RUN_ID="$(sed -n '1p' "$QUEUE_FILE" | tr -d '\r\n')"
TMP_FILE="${QUEUE_FILE}.tmp.$$"
sed -n '2,$p' "$QUEUE_FILE" > "$TMP_FILE"
mv "$TMP_FILE" "$QUEUE_FILE"

echo "[tick] execute run_id=$RUN_ID"
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label "smoke_auto_tick_$(date -u +%Y%m%d%H%M%S)" \
  --include-run-id "$RUN_ID" \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --require-live-model \
  --required-live-model-env "OPENAI_API_KEY,LLM_EMOTION_REAL_MODEL,LLM_EMOTION_REAL_MODEL_REGION" \
  --max-failed-cells 0 \
  --max-failure-rate 0.5 \
  --continue-on-error \
  --manifest-markdown \
  --execution-log-jsonl "results/experiments/${RUN_ID}_auto_tick/command_log.jsonl" \
  --budget-report-json "results/experiments/${RUN_ID}_auto_tick/budget_report.json" \
  --budget-report-md "results/experiments/${RUN_ID}_auto_tick/budget_report.md" || true

refresh_status

echo "[tick] done"
