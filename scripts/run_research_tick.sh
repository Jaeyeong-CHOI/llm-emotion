#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion"
cd "$ROOT"

load_env_file() {
  local env_file="$1"
  [ -f "$env_file" ] || return 1

  set -a
  # shellcheck disable=SC1090
  source "$env_file"
  set +a
  return 0
}

ENV_FILE="${LLM_EMOTION_ENV_FILE:-$ROOT/.env.real_model}"
if ! load_env_file "$ENV_FILE"; then
  echo "[tick] env file not found (${ENV_FILE}); skip" >&2
  exit 0
fi

run_status_command() {
  local log_path="$1"
  shift
  "$@" >"$log_path" 2>&1 || true
}

refresh_status() {
  while IFS='|' read -r log_path command; do
    run_status_command "$log_path" bash -lc "$command"
  done <<'EOF'
/tmp/research_tick_status.log|python3 scripts/update_live_status.py
/tmp/research_tick_research_status.log|python3 scripts/research_status.py
EOF
}

skip_with_status() {
  local reason="$1"
  echo "[tick] ${reason}; skip"
  refresh_status
  exit 0
}

echo "[tick] $(date -u +'%Y-%m-%dT%H:%M:%SZ') start"

LOCK_DIR="/tmp/llm_emotion_research_tick.lock"
LOCK_PID_FILE="$LOCK_DIR/pid"

is_numeric_pid() {
  local pid="$1"
  [[ "$pid" =~ ^[0-9]+$ ]]
}

lock_pid_uid_and_command() {
  local pid="$1"
  local ps_line=""
  local owner_uid=""
  local command=""

  is_numeric_pid "$pid" || return 1

  ps_line="$(ps -p "$pid" -o uid= -o command= 2>/dev/null | head -n 1 | tr -d '\r' || true)"
  [ -n "$ps_line" ] || return 1

  owner_uid="$(printf '%s' "$ps_line" | awk '{print $1}')"
  command="$(printf '%s' "$ps_line" | sed -E 's/^[[:space:]]*[0-9]+[[:space:]]+//')"

  [[ -n "$owner_uid" ]] || return 1
  [[ "$owner_uid" == "$(id -u)" ]] || return 1
  [[ "$command" == *"run_research_tick.sh"* ]]
}

claim_lock_dir() {
  mkdir "$LOCK_DIR" 2>/dev/null || return 1
  printf '%s\n' "$$" > "$LOCK_PID_FILE"
}

clear_lock_dir() {
  rm -f "$LOCK_PID_FILE"
  rmdir "$LOCK_DIR" 2>/dev/null || true
}

recover_stale_lock() {
  local lock_pid="$1"
  echo "[tick] stale lock detected (pid=$lock_pid); recovering"
  clear_lock_dir
  if ! claim_lock_dir; then
    echo "[tick] failed to re-claim lock after stale lock recovery" >&2
    return 1
  fi
}

lock_pid_is_active_tick_owner() {
  local pid="$1"

  is_numeric_pid "$pid" \
    && kill -0 "$pid" 2>/dev/null \
    && lock_pid_uid_and_command "$pid"
}

acquire_lock() {
  if claim_lock_dir; then
    return 0
  fi

  local lock_pid=""
  if [ -f "$LOCK_PID_FILE" ]; then
    lock_pid="$(cat "$LOCK_PID_FILE" 2>/dev/null || true)"
  fi

  if [ -n "$lock_pid" ] && ! lock_pid_is_active_tick_owner "$lock_pid"; then
    if recover_stale_lock "$lock_pid"; then
      return 0
    fi
  fi

  return 1
}

if ! acquire_lock; then
  skip_with_status "lock busy; another tick is running"
fi

cleanup_lock() {
  clear_lock_dir
}
trap cleanup_lock EXIT

READY_LINE="$(python3 scripts/check_real_model_readiness.py | tr -d '\r' | head -n 1)"
if [[ "$READY_LINE" != "ready=true" ]]; then
  skip_with_status "readiness=${READY_LINE}"
fi

QUEUE_FILE="ops/continuous_run_ids.txt"

canonical_line() {
  printf '%s' "$1" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

is_queue_data_line() {
  local line="$1"
  [[ -n "$line" ]] && [[ ! "$line" =~ ^# ]]
}

iter_queue_data_lines() {
  local queue_file="$1"
  local raw_line=""

  [ -f "$queue_file" ] || return 0

  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    local line
    line="$(canonical_line "$raw_line")"
    if is_queue_data_line "$line"; then
      printf '%s\n' "$line"
    fi
  done < "$queue_file"
}

dequeue_run_id() {
  local queue_file="$1"
  local tmp_file=""

  if [ ! -f "$queue_file" ]; then
    printf ''
    return 0
  fi

  tmp_file="$(mktemp "${queue_file}.tmp.XXXXXX")"

  local picked=""
  local raw_line=""

  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    local line
    line="$(canonical_line "$raw_line")"
    if [ -z "$picked" ] && is_queue_data_line "$line"; then
      picked="$line"
      continue
    fi
    printf '%s\n' "$raw_line"
  done < "$queue_file" > "$tmp_file"

  if ! mv "$tmp_file" "$queue_file"; then
    rm -f "$tmp_file"
    return 1
  fi

  printf '%s' "$picked"
}

if ! RUN_ID="$(dequeue_run_id "$QUEUE_FILE")"; then
  skip_with_status "failed to dequeue run-id"
fi

if [ -z "$RUN_ID" ]; then
  skip_with_status "no queued run-id"
fi

normalize_queue_run_id() {
  local run_id="$1"
  local canonical_run_id
  canonical_run_id="$(canonical_line "$run_id")"

  if ! is_queue_data_line "$canonical_run_id"; then
    return 1
  fi

  if [[ ! "$canonical_run_id" =~ ^[A-Za-z0-9._-]+$ ]]; then
    return 1
  fi

  printf '%s' "$canonical_run_id"
}

if ! RUN_ID="$(normalize_queue_run_id "$RUN_ID")"; then
  skip_with_status "invalid run-id format (${RUN_ID})"
fi

queue_contains_run_id() {
  local queue_file="$1"
  local run_id="$2"
  local canonical_run_id
  local queued_run_id=""

  canonical_run_id="$(normalize_queue_run_id "$run_id")" || return 1

  while IFS= read -r queued_run_id; do
    if [ "$queued_run_id" = "$canonical_run_id" ]; then
      return 0
    fi
  done < <(iter_queue_data_lines "$queue_file")

  return 1
}

enqueue_run_id_unique() {
  local queue_file="$1"
  local run_id="$2"
  local canonical_run_id

  canonical_run_id="$(normalize_queue_run_id "$run_id")" || return 0

  touch "$queue_file"
  if queue_contains_run_id "$queue_file" "$canonical_run_id"; then
    return 0
  fi

  printf '%s\n' "$canonical_run_id" >> "$queue_file"
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
