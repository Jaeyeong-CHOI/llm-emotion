#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
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

STATUS_LOG_DIR="${TMPDIR:-/tmp}/llm_emotion_research_tick"
mkdir -p "$STATUS_LOG_DIR"

run_status_command() {
  local log_path="$1"
  shift
  "$@" >"$log_path" 2>&1 || true
}

refresh_status() {
  local ts
  ts="$(date -u +%Y%m%dT%H%M%SZ)_$$"

  run_status_command "$STATUS_LOG_DIR/research_tick_status_${ts}.log" \
    python3 scripts/update_live_status.py
  run_status_command "$STATUS_LOG_DIR/research_tick_research_status_${ts}.log" \
    python3 scripts/research_status.py
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
LOCK_STALE_SECONDS="${LLM_EMOTION_TICK_LOCK_STALE_SECONDS:-900}"
LOCK_ACQUIRED=0
RUN_TICK_SCRIPT="${ROOT}/scripts/run_research_tick.sh"

is_numeric_pid() {
  local pid="$1"
  [[ "$pid" =~ ^[0-9]+$ ]]
}

is_expected_tick_command() {
  local command_line="$1"
  local token=""
  local normalized=""
  local candidate=""

  for token in $command_line; do
    if [[ "$token" != *run_research_tick.sh ]]; then
      continue
    fi

    # 1) literal token itself
    normalized="$(realpath "$token" 2>/dev/null || true)"
    if [ -n "$normalized" ] && [ "$normalized" = "$RUN_TICK_SCRIPT" ]; then
      return 0
    fi

    # 2) token relative to script directory (handles `bash run_research_tick.sh`)
    candidate="${SCRIPT_DIR}/${token}"
    normalized="$(realpath "$candidate" 2>/dev/null || true)"
    if [ -n "$normalized" ] && [ "$normalized" = "$RUN_TICK_SCRIPT" ]; then
      return 0
    fi
  done

  return 1
}

trim_whitespace() {
  sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

read_proc_field() {
  local pid="$1"
  local field="$2"
  local strip_ws="${3:-0}"

  local value=""
  value="$(ps -p "$pid" -o "${field}=" 2>/dev/null | tr -d '\r' | head -n 1 || true)"
  [ -n "$value" ] || return 1

  if [ "$strip_ws" = "1" ]; then
    value="$(printf '%s' "$value" | trim_whitespace)"
  fi

  printf '%s' "$value"
}

lock_pid_uid_and_command() {
  local pid="$1"
  local owner_uid=""
  local command=""

  is_numeric_pid "$pid" || return 1

  owner_uid="$(read_proc_field "$pid" uid 1 || true)"
  command="$(read_proc_field "$pid" command 0 || true)"

  [[ -n "$owner_uid" ]] || return 1
  [[ -n "$command" ]] || return 1
  [[ "$owner_uid" == "$(id -u)" ]] || return 1
  is_expected_tick_command "$command"
}

claim_lock_dir() {
  mkdir "$LOCK_DIR" 2>/dev/null || return 1
  printf '%s\n' "$$" > "$LOCK_PID_FILE"
}

lock_dir_is_safe() {
  [ -d "$LOCK_DIR" ] && [ ! -L "$LOCK_DIR" ]
}

clear_lock_dir() {
  if lock_dir_is_safe; then
    rm -f "$LOCK_PID_FILE"
    rmdir "$LOCK_DIR" 2>/dev/null || true
  fi
}

is_stale_lock_dir() {
  local mtime=""
  local now=""
  local age=""

  if ! lock_dir_is_safe; then
    return 1
  fi

  mtime="$(stat -f "%m" "$LOCK_DIR" 2>/dev/null || echo 0)"
  [ "$mtime" -gt 0 ] || return 1

  now="$(date +%s)"
  age=$(( now - mtime ))
  [ "$age" -gt "$LOCK_STALE_SECONDS" ]
}

recover_stale_lock() {
  local lock_pid="$1"
  if [ -n "$lock_pid" ]; then
    echo "[tick] stale lock detected (pid=$lock_pid); recovering"
  else
    echo "[tick] stale lock directory without pid file detected; recovering"
  fi
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
    LOCK_ACQUIRED=1
    return 0
  fi

  if [ -e "$LOCK_DIR" ] && ! lock_dir_is_safe; then
    echo "[tick] lock path is unsafe (not a directory or symlink): $LOCK_DIR" >&2
    return 1
  fi

  local lock_pid=""
  if [ -f "$LOCK_PID_FILE" ]; then
    lock_pid="$(cat "$LOCK_PID_FILE" 2>/dev/null || true)"
  fi

  if [ -n "$lock_pid" ]; then
    if ! lock_pid_is_active_tick_owner "$lock_pid"; then
      if recover_stale_lock "$lock_pid"; then
        LOCK_ACQUIRED=1
        return 0
      fi
    fi
  elif is_stale_lock_dir; then
    if recover_stale_lock ""; then
      LOCK_ACQUIRED=1
      return 0
    fi
  fi

  return 1
}

if ! acquire_lock; then
  skip_with_status "lock busy; another tick is running"
fi

RUN_IN_FLIGHT=0
RUN_FINALIZED=0
RUN_ID=""

cleanup_on_exit() {
  if [ "$LOCK_ACQUIRED" -eq 1 ]; then
    clear_lock_dir
  fi

  if [ "$RUN_IN_FLIGHT" -eq 1 ] && [ "$RUN_FINALIZED" -eq 0 ] && [ -n "$RUN_ID" ] && [ -n "${QUEUE_FILE:-}" ]; then
    echo "[tick] interrupted before finalizing run_id=$RUN_ID; re-queue for retry"
    enqueue_run_id_unique "$QUEUE_FILE" "$RUN_ID"
  fi
}
trap cleanup_on_exit EXIT

READY_LINE="$(python3 scripts/check_real_model_readiness.py | tr -d '\r' | head -n 1)"
if [[ "$READY_LINE" != "ready=true" ]]; then
  skip_with_status "readiness=${READY_LINE}"
fi

QUEUE_FILE="ops/continuous_run_ids.txt"

canonical_line() {
  printf '%s' "$1" | tr -d '\r' | trim_whitespace
}

strip_queue_comment() {
  local line="$1"
  printf '%s' "${line%%#*}"
}

is_queue_data_line() {
  local line="$1"
  [[ -n "$line" ]] && [[ ! "$line" =~ ^# ]]
}

canonicalize_queue_line() {
  local line
  line="$(strip_queue_comment "$1")"
  line="$(canonical_line "$line")"

  is_queue_data_line "$line" || return 1
  printf '%s' "$line"
}

normalize_queue_run_id() {
  local run_id="$1"
  local canonical_run_id
  canonical_run_id="$(canonicalize_queue_line "$run_id")" || return 1

  if [[ ! "$canonical_run_id" =~ ^[A-Za-z0-9._-]+$ ]]; then
    return 1
  fi

  printf '%s' "$canonical_run_id"
}

iter_queue_lines() {
  local queue_file="$1"
  local raw_line=""

  [ -f "$queue_file" ] || return 0

  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    local canonical
    canonical="$(canonicalize_queue_line "$raw_line" || true)"
    is_queue_data_line "$canonical" || continue

    local normalized
    normalized="$(normalize_queue_run_id "$canonical" || true)"
    if [ -n "$normalized" ]; then
      printf '%s\n' "$normalized"
    else
      echo "[tick] invalid run-id skipped: $canonical" >&2
    fi
  done < "$queue_file"
}

make_queue_temp_file() {
  local queue_file="$1"
  local suffix="${2:-tmp}"

  mktemp "${queue_file}.${suffix}.XXXXXX"
}

commit_queue_tmp_file() {
  local queue_file="$1"
  local tmp_file="$2"
  local changed="$3"

  if [ "$changed" -eq 1 ]; then
    if ! mv "$tmp_file" "$queue_file"; then
      rm -f "$tmp_file"
      return 1
    fi
    return 0
  fi

  rm -f "$tmp_file"
  return 0
}

dedupe_queue_file() {
  local queue_file="$1"
  local tmp_file=""
  local changed=0

  [ -f "$queue_file" ] || return 0
  tmp_file="$(make_queue_temp_file "$queue_file" dedupe)"

  if ! awk '{ if (!seen[$0]++) print $0 }' < <(iter_queue_lines "$queue_file") > "$tmp_file"; then
    rm -f "$tmp_file"
    return 1
  fi

  if cmp -s "$queue_file" "$tmp_file" 2>/dev/null; then
    changed=0
  else
    changed=1
  fi

  if ! commit_queue_tmp_file "$queue_file" "$tmp_file" "$changed"; then
    return 1
  fi
}
dequeue_run_id() {
  local queue_file="$1"
  local tmp_file=""

  if [ ! -f "$queue_file" ]; then
    printf ''
    return 0
  fi

  tmp_file="$(make_queue_temp_file "$queue_file" dequeue)"

  local picked=""
  local line=""
  local changed=0

  while IFS= read -r line || [ -n "$line" ]; do
    if [ -z "$picked" ]; then
      picked="$line"
      changed=1
      continue
    fi

    printf '%s\n' "$line"
  done < <(iter_queue_lines "$queue_file") > "$tmp_file"

  if ! commit_queue_tmp_file "$queue_file" "$tmp_file" "$changed"; then
    return 1
  fi

  printf '%s' "$picked"
}

dedupe_queue_file "$QUEUE_FILE"

if ! RUN_ID="$(dequeue_run_id "$QUEUE_FILE")"; then
  skip_with_status "failed to dequeue run-id"
fi

if [ -z "$RUN_ID" ]; then
  skip_with_status "no queued run-id"
fi

queue_contains_canonical_run_id() {
  local queue_file="$1"
  local canonical_run_id="$2"
  local queued_run_id=""

  while IFS= read -r queued_run_id; do
    if [ "$queued_run_id" = "$canonical_run_id" ]; then
      return 0
    fi
  done < <(iter_queue_lines "$queue_file")

  return 1
}

enqueue_run_id_unique() {
  local queue_file="$1"
  local run_id="$2"
  local canonical_run_id

  canonical_run_id="$(normalize_queue_run_id "$run_id")" || return 0

  touch "$queue_file"
  if queue_contains_canonical_run_id "$queue_file" "$canonical_run_id"; then
    return 0
  fi

  printf '%s\n' "$canonical_run_id" >> "$queue_file"
}

echo "[tick] execute run_id=$RUN_ID"
run_failed=0
RUN_IN_FLIGHT=1
RUN_ARTIFACT_DIR="results/experiments/${RUN_ID}_auto_tick"

if ! python3 scripts/run_experiments_with_profile.py \
  --profile ops/runner_tick_profile.json \
  -- \
  --run-label "smoke_auto_tick_$(date -u +%Y%m%d%H%M%S)" \
  --include-run-id "$RUN_ID" \
  --fail-on-missing-run-id \
  --max-runs 1 \
  --required-live-model-env "OPENAI_API_KEY,LLM_EMOTION_REAL_MODEL,LLM_EMOTION_REAL_MODEL_REGION" \
  --execution-log-jsonl "$RUN_ARTIFACT_DIR/command_log.jsonl" \
  --budget-report-json "$RUN_ARTIFACT_DIR/budget_report.json" \
  --budget-report-md "$RUN_ARTIFACT_DIR/budget_report.md"; then
  run_failed=1
  echo "[tick] run_id=$RUN_ID failed; re-queue for retry"
  enqueue_run_id_unique "$QUEUE_FILE" "$RUN_ID"
fi
RUN_FINALIZED=1
RUN_IN_FLIGHT=0

refresh_status

if [ "$run_failed" -eq 0 ]; then
  echo "[tick] done"
else
  echo "[tick] done (with failure, re-queued)"
fi
