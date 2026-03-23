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

skip_with_status() {
  local reason="$1"
  echo "[tick] ${reason}; skip"
  refresh_status
  exit 0
}

echo "[tick] $(date -u +'%Y-%m-%dT%H:%M:%SZ') start"

LOCK_DIR="/tmp/llm_emotion_research_tick.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[tick] lock busy; another tick is running, skip"
  exit 0
fi
cleanup_lock() {
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup_lock EXIT

READY_LINE="$(python3 scripts/check_real_model_readiness.py | tr -d '\r' | head -n 1)"
if [[ "$READY_LINE" != "ready=true" ]]; then
  skip_with_status "readiness=${READY_LINE}"
fi

QUEUE_FILE="ops/continuous_run_ids.txt"
if [ ! -f "$QUEUE_FILE" ] || [ ! -s "$QUEUE_FILE" ]; then
  skip_with_status "no queued run-id"
fi

TMP_FILE="$(mktemp "${QUEUE_FILE}.tmp.XXXXXX")"
PICKED_FILE="$(mktemp "/tmp/llm_emotion_run_id.XXXXXX")"
awk -v picked_file="$PICKED_FILE" '
  BEGIN { picked=0 }
  {
    line=$0
    gsub(/\r/, "", line)
    if (!picked && line !~ /^[[:space:]]*$/ && line !~ /^[[:space:]]*#/) {
      print line > picked_file
      picked=1
      next
    }
    print $0
  }
' "$QUEUE_FILE" > "$TMP_FILE"
mv "$TMP_FILE" "$QUEUE_FILE"
RUN_ID="$(tr -d '\r\n' < "$PICKED_FILE")"
rm -f "$PICKED_FILE"


if [ -z "$RUN_ID" ]; then
  skip_with_status "no valid run-id found in queue"
fi

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
