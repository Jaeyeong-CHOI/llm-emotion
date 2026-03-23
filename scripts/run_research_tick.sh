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

run_status_command() {
  local log_path="$1"
  shift
  "$@" >"$log_path" 2>&1 || true
}

refresh_status() {
  run_status_command /tmp/research_tick_status.log python3 scripts/update_live_status.py
  run_status_command /tmp/research_tick_research_status.log python3 scripts/research_status.py
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

normalize_line() {
  printf '%s' "$1" | tr -d '\r'
}

trim_line() {
  printf '%s' "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

is_queue_data_line() {
  local line="$1"
  [[ -n "$line" ]] && [[ ! "$line" =~ ^# ]]
}

dequeue_run_id() {
  local queue_file="$1"
  local tmp_file
  tmp_file="$(mktemp "${queue_file}.tmp.XXXXXX")"

  local picked=""
  local done=0
  cleanup_tmp() {
    if [ "$done" -eq 0 ]; then
      rm -f "$tmp_file"
    fi
  }
  trap cleanup_tmp RETURN

  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    local line
    line="$(trim_line "$(normalize_line "$raw_line")")"
    if [ -z "$picked" ] && is_queue_data_line "$line"; then
      picked="$line"
      continue
    fi
    printf '%s\n' "$raw_line" >> "$tmp_file"
  done < "$queue_file"

  mv "$tmp_file" "$queue_file"
  done=1
  printf '%s' "$picked"
}

RUN_ID="$(dequeue_run_id "$QUEUE_FILE")"

if [ -z "$RUN_ID" ]; then
  skip_with_status "no valid run-id found in queue"
fi

is_safe_run_id() {
  local run_id="$1"
  [[ "$run_id" =~ ^[A-Za-z0-9._-]+$ ]]
}

if ! is_safe_run_id "$RUN_ID"; then
  skip_with_status "invalid run-id format (${RUN_ID})"
fi

enqueue_run_id_unique() {
  local queue_file="$1"
  local run_id="$2"

  touch "$queue_file"
  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    local line
    line="$(trim_line "$(normalize_line "$raw_line")")"
    if [ "$line" = "$run_id" ]; then
      return 0
    fi
  done < "$queue_file"

  printf '%s\n' "$run_id" >> "$queue_file"
}

echo "[tick] execute run_id=$RUN_ID"
run_failed=0
if ! python3 scripts/run_experiments.py \
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
  --budget-report-md "results/experiments/${RUN_ID}_auto_tick/budget_report.md"; then
  run_failed=1
  echo "[tick] run_id=$RUN_ID failed; re-queue for retry"
  enqueue_run_id_unique "$QUEUE_FILE" "$RUN_ID"
fi

refresh_status

if [ "$run_failed" -eq 0 ]; then
  echo "[tick] done"
else
  echo "[tick] done (with failure, re-queued)"
fi
