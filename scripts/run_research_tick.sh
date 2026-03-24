#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/research_env.sh"

if ! load_research_env; then
  echo "[tick] env file not found; skip" >&2
  exit 0
fi

ensure_dir() {
  local dir="$1"
  mkdir -p "$dir"
}

utc_now() {
  date -u "+$1"
}

utc_now_ts() {
  utc_now '%Y%m%d%H%M%S'
}

utc_now_iso() {
  utc_now '%Y-%m-%dT%H:%M:%SZ'
}

utc_now_compact() {
  utc_now '%Y%m%dT%H%M%SZ'
}

run_python() {
  local script_path="$1"
  shift
  python3 "$script_path" "$@"
}

run_experiments_tick() {
  local run_id="$1"
  local artifact_dir="$2"

  run_python scripts/run_experiments_with_profile.py \
    --profile ops/runner_tick_profile.json \
    -- \
    --run-label "smoke_auto_tick_$(utc_now_ts)" \
    --include-run-id "$run_id" \
    --fail-on-missing-run-id \
    --max-runs 1 \
    --required-live-model-env OPENAI_API_KEY,LLM_EMOTION_REAL_MODEL,LLM_EMOTION_REAL_MODEL_REGION \
    --execution-log-jsonl "$artifact_dir/command_log.jsonl" \
    --budget-report-json "$artifact_dir/budget_report.json" \
    --budget-report-md "$artifact_dir/budget_report.md"
}
STATUS_LOG_DIR="${TMPDIR:-/tmp}/llm_emotion_research_tick"
ensure_dir "$STATUS_LOG_DIR"

run_status_command() {
  local log_path="$1"
  shift
  "$@" >"$log_path" 2>&1 || true
}

run_status_script() {
  local ts="$1"
  local status_script="$2"
  local status_path="${ROOT}/scripts/${status_script}"

  if [ ! -f "$status_path" ]; then
    echo "[tick] status script missing: ${status_path}" >&2
    return 0
  fi

  run_status_command "${STATUS_LOG_DIR}/research_tick_${status_script%.py}_${ts}.log" \
    run_python "$status_path"
}

STATUS_SCRIPTS=(
  "update_live_status.py"
  "research_status.py"
)

refresh_status() {
  local ts
  local status_script

  ts="$(utc_now_compact)_$$"

  for status_script in "${STATUS_SCRIPTS[@]}"; do
    run_status_script "$ts" "$status_script"
  done
}

skip_with_status() {
  local reason="$1"
  echo "[tick] ${reason}; skip"
  refresh_status
  exit 0
}

echo "[tick] $(utc_now_iso) start"

LOCK_DIR="/tmp/llm_emotion_research_tick.lock"
LOCK_PID_FILE="$LOCK_DIR/pid"
LOCK_ACQUIRED=0
RUN_TICK_SCRIPT="${ROOT}/scripts/run_research_tick.sh"

is_nonnegative_integer() {
  local value="$1"
  [[ "$value" =~ ^[0-9]+$ ]]
}

coalesce_int_env() {
  local value="$1"
  local default_value="$2"

  if is_nonnegative_integer "$value"; then
    printf '%s' "$value"
  else
    printf '%s' "$default_value"
  fi
}

LOCK_STALE_SECONDS="$(coalesce_int_env "${LLM_EMOTION_TICK_LOCK_STALE_SECONDS:-}" 900)"

is_numeric_pid() {
  local pid="$1"
  is_nonnegative_integer "$pid"
}

is_safe_lock_file() {
  local file_path="$1"

  [ -f "$file_path" ] || return 1
  [ ! -L "$file_path" ] || return 1
  [ "$(stat -f '%u' "$file_path" 2>/dev/null)" -eq "$(id -u)" ] || return 1

  return 0
}

normalize_candidate_to_tick_script() {
  local candidate="$1"
  local normalized=""

  [ -e "$candidate" ] || return 1
  normalized="$(realpath "$candidate" 2>/dev/null || true)"
  [ -n "$normalized" ] && [ "$normalized" = "$RUN_TICK_SCRIPT" ]
}

strip_surrounding_quotes() {
  local value="$1"
  local len=0
  local first=""
  local last=""

  len=${#value}
  if [ "$len" -lt 2 ]; then
    printf '%s' "$value"
    return
  fi

  first="${value:0:1}"
  last="${value:len-1:1}"

  if [[ "$first" == '"' && "$last" == '"' ]] || [[ "$first" == "'" && "$last" == "'" ]]; then
    printf '%s' "${value:1:len-2}"
    return
  fi

  printf '%s' "$value"
}

candidate_resolves_to_tick_script() {
  local token="$1"
  local candidate=""

  for candidate in "$token" "${SCRIPT_DIR}/${token}" "${ROOT}/${token}"; do
    normalize_candidate_to_tick_script "$candidate" && return 0
  done

  return 1
}

is_expected_tick_command() {
  local command_line="$1"
  local token=""
  local -a tokens=()

  [ -n "$command_line" ] || return 1

  # Quick-path for common command wrappers: if the tick script path appears
  # anywhere in the process command, treat it as owned by this loop.
  if [[ "$command_line" == *"/run_research_tick.sh"* ]]; then
    return 0
  fi

  IFS=' ' read -r -a tokens <<< "$command_line" || true
  for token in "${tokens[@]}"; do
    candidate_resolves_to_tick_script "$(strip_surrounding_quotes "$token")" && return 0
  done

  return 1
}

trim_whitespace() {
  sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

normalize_text() {
  local value="$1"
  value="${value//$'\r'/}"
  # Handle common copy/paste/UTF-8 BOM artifacts at the start of queue lines.
  value="${value#$'\ufeff'}"
  trim_whitespace <<< "$value"
}

read_first_line_normalized() {
  local file="$1"
  local raw_line=""

  raw_line="$(head -n 1 "$file" 2>/dev/null || true)"
  [ -n "$raw_line" ] || return 1

  normalize_text "$raw_line"
}

read_lock_pid_file() {
  local pid_file="$1"

  is_safe_lock_file "$pid_file" || return 1
  read_first_line_normalized "$pid_file" || return 1
}

ensure_queue_file_safe() {
  local queue_file="$1"
  local when_fail="${2:-1}"

  is_path_safe_from_symlink "$queue_file" || return "$when_fail"
  if [ -e "$queue_file" ] && [ ! -f "$queue_file" ]; then
    echo "[tick] rejected queue path (not a regular file): ${queue_file}" >&2
    return "$when_fail"
  fi
}

read_proc_uid_and_command() {
  local pid="$1"
  local raw_line=""
  local owner_uid=""
  local command=""

  raw_line="$(ps -p "$pid" -o uid= -o command= 2>/dev/null | tr -d '\r' | head -n 1 || true)"
  [ -n "$raw_line" ] || return 1

  owner_uid="$(awk '{print $1}' <<< "$raw_line")"
  command="$(sed -E 's/^[[:space:]]*[0-9]+[[:space:]]+//' <<< "$raw_line")"

  [ -n "$owner_uid" ] || return 1
  [ -n "$command" ] || return 1

  printf '%s\n%s\n' "$owner_uid" "$command"
}

lock_pid_uid_and_command() {
  local pid="$1"
  local owner_uid=""
  local command=""
  local proc_info=""
  local IFS=$'\n'

  is_numeric_pid "$pid" || return 1

  proc_info="$(read_proc_uid_and_command "$pid")" || return 1
  read -r owner_uid command <<< "$proc_info"

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
    if is_safe_lock_file "$LOCK_PID_FILE"; then
      rm -f "$LOCK_PID_FILE"
    fi
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

  try_recover_lock() {
    local candidate_pid="${1:-}"

    if recover_stale_lock "$candidate_pid"; then
      LOCK_ACQUIRED=1
      return 0
    fi
    return 1
  }

  local lock_pid=""
  if [ -f "$LOCK_PID_FILE" ]; then
    if lock_pid="$(read_lock_pid_file "$LOCK_PID_FILE" || true)"; then
      if ! lock_pid_is_active_tick_owner "$lock_pid"; then
        if try_recover_lock "$lock_pid"; then
          return 0
        fi
      fi
    elif try_recover_lock ""; then
      return 0
    fi
  elif is_stale_lock_dir; then
    if try_recover_lock ""; then
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

capture_script_output() {
  local script_path="$1"
  local output=""

  output="$(run_python "$script_path" 2>&1)" || return 1
  printf '%s' "$output"
}

read_readiness_line() {
  local raw_line=""
  local readiness_output=""

  readiness_output="$(capture_script_output scripts/check_real_model_readiness.py)" || return 1
  raw_line="$(awk '/^ready=/{print $0; exit}' <<< "$readiness_output")"

  [ -n "$raw_line" ] || return 1
  printf '%s' "$(normalize_text "$raw_line")"
}

READY_LINE="$(read_readiness_line || true)"
if [ -z "$READY_LINE" ] || [[ "$READY_LINE" != "ready=true" ]]; then
  skip_with_status "readiness=${READY_LINE:-unknown}"
fi

QUEUE_FILE="ops/continuous_run_ids.txt"

strip_queue_comment() {
  local line="$1"
  printf '%s' "${line%%#*}"
}

canonicalize_run_id_line() {
  local raw_line="$1"

  printf '%s' "$(normalize_text "$(strip_queue_comment "$raw_line")")"
}

is_path_safe_from_symlink() {
  local path="$1"
  local current="${path}"

  [ -n "$path" ] || return 1

  while [ -n "$current" ] && [ "$current" != "." ] && [ "$current" != "/" ]; do
    if [ -L "$current" ]; then
      echo "[tick] rejected unsafe path (symlink): ${current}" >&2
      return 1
    fi

    # Move to the parent component; paths without separators ("a") still get a
    # final check on the basename before exiting.
    if [ "${current%/*}" = "$current" ]; then
      break
    fi

    current="${current%/*}"
  done

  return 0
}
is_valid_run_id() {
  local value="$1"
  [[ "$value" =~ ^[A-Za-z0-9._-]+$ ]]
}

parse_queue_line() {
  local raw_line="$1"
  local log_invalid="$2"
  local canonical=""

  canonical="$(canonicalize_run_id_line "$raw_line")"
  [[ -n "$canonical" ]] || return 1

  if is_valid_run_id "$canonical"; then
    printf '%s' "$canonical"
    return 0
  fi

  if [ "$log_invalid" = "1" ]; then
    echo "[tick] invalid run-id skipped: $canonical" >&2
  fi

  return 1
}

sanitize_queue_run_id() {
  parse_queue_line "$1" 0
}

iter_queue_lines() {
  local queue_file="$1"
  local raw_line=""
  local sanitized=""

  [ -f "$queue_file" ] || return 0

  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    if sanitized="$(parse_queue_line "$raw_line" 1 2>/dev/null)"; then
      printf '%s\n' "$sanitized"
      continue
    fi
  done < "$queue_file"
}

make_queue_temp_file() {
  local queue_file="$1"
  local suffix="${2:-tmp}"

  mktemp "${queue_file}.${suffix}.XXXXXX"
}

with_materialized_queue_tmp() {
  local queue_file="$1"
  local suffix="$2"
  local sanitized_tmp=""

  sanitized_tmp="$(make_queue_temp_file "$queue_file" "$suffix")"
  if ! materialize_sanitized_queue "$queue_file" "$sanitized_tmp"; then
    cleanup_tmp_files "$sanitized_tmp"
    return 1
  fi

  printf '%s' "$sanitized_tmp"
}

replace_if_changed() {
  local queue_file="$1"
  local tmp_file="$2"

  if cmp -s "$queue_file" "$tmp_file" 2>/dev/null; then
    rm -f "$tmp_file"
    return 0
  fi

  mv "$tmp_file" "$queue_file"
  return 0
}

cleanup_tmp_files() {
  local file=""

  for file in "$@"; do
    [ -n "$file" ] || continue
    rm -f "$file"
  done
}

materialize_sanitized_queue() {
  local queue_file="$1"
  local out_file="$2"

  if [ ! -f "$queue_file" ]; then
    : > "$out_file"
    return 0
  fi

  iter_queue_lines "$queue_file" > "$out_file"
}

commit_queue_update() {
  local queue_file="$1"
  local tmp_file="$2"

  if ! replace_if_changed "$queue_file" "$tmp_file"; then
    rm -f "$tmp_file"
    return 1
  fi
}

finalize_queue_update() {
  local queue_file="$1"
  local tmp_file="$2"

  if ! commit_queue_update "$queue_file" "$tmp_file"; then
    cleanup_tmp_files "$tmp_file"
    return 1
  fi

  cleanup_tmp_files "$tmp_file"
}

dedupe_queue_file() {
  local queue_file="$1"
  local dedup_file=""
  local deduped_file=""

  ensure_queue_file_safe "$queue_file" 1 || return 1
  dedup_file="$(with_materialized_queue_tmp "$queue_file" dedupe)" || return 1
  deduped_file="${dedup_file}.deduped"

  if ! awk '{ if (!seen[$0]++) print $0 }' "$dedup_file" > "$deduped_file"; then
    cleanup_tmp_files "$dedup_file" "$deduped_file"
    return 1
  fi

  if ! finalize_queue_update "$queue_file" "$deduped_file"; then
    cleanup_tmp_files "$dedup_file"
    return 1
  fi

  cleanup_tmp_files "$dedup_file"
}
dequeue_run_id() {
  local queue_file="$1"
  local tmp_file=""
  local next_file=""
  local picked=""

  ensure_queue_file_safe "$queue_file" 1 || return 1

  if [ ! -f "$queue_file" ]; then
    printf ''
    return 0
  fi

  tmp_file="$(with_materialized_queue_tmp "$queue_file" dequeue)" || return 1
  next_file="${tmp_file}.next"

  picked="$(sed -n '1p' "$tmp_file")"
  if [ -n "$picked" ]; then
    if ! sed -n '2,$p' "$tmp_file" > "$next_file"; then
      cleanup_tmp_files "$tmp_file" "$next_file"
      return 1
    fi
    if ! finalize_queue_update "$queue_file" "$next_file"; then
      cleanup_tmp_files "$tmp_file"
      return 1
    fi
  fi

  cleanup_tmp_files "$tmp_file" "$next_file"
  printf '%s' "$picked"
}

if ! dedupe_queue_file "$QUEUE_FILE"; then
  skip_with_status "unsafe or invalid queue path: $QUEUE_FILE"
fi

if ! RUN_ID="$(dequeue_run_id "$QUEUE_FILE")"; then
  skip_with_status "failed to dequeue run-id"
fi

if [ -z "$RUN_ID" ]; then
  skip_with_status "no queued run-id"
fi

queue_contains_sanitized_run_id() {
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
  local canonical_run_id=""

  ensure_queue_file_safe "$queue_file" 0 || return 0
  canonical_run_id="$(sanitize_queue_run_id "$run_id")" || return 0

  touch "$queue_file"
  if queue_contains_sanitized_run_id "$queue_file" "$canonical_run_id"; then
    return 0
  fi

  printf '%s\n' "$canonical_run_id" >> "$queue_file"
}

echo "[tick] execute run_id=$RUN_ID"
run_failed=0
RUN_IN_FLIGHT=1
RUN_ARTIFACT_DIR="results/experiments/${RUN_ID}_auto_tick"
ensure_dir "$RUN_ARTIFACT_DIR"

if ! run_experiments_tick "$RUN_ID" "$RUN_ARTIFACT_DIR"; then
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
