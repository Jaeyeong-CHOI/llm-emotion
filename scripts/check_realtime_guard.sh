#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

load_env_file() {
  local env_file="${LLM_EMOTION_ENV_FILE:-$ROOT/.env.real_model}"

  if [[ -n "${LLM_EMOTION_ENV_FILE:-}" && -f "${LLM_EMOTION_ENV_FILE}" ]]; then
    env_file="$LLM_EMOTION_ENV_FILE"
  elif [[ -f "$ROOT/.env.real_model" ]]; then
    env_file="$ROOT/.env.real_model"
  else
    return 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "$env_file"
  set +a
  return 0
}

load_env_file

run_step() {
  local index="$1"
  local label="$2"
  shift 2

  printf "[%s/4] %s\n" "$index" "$label"
  "$@"
}

run_step 1 "real model readiness check" python3 scripts/check_real_model_readiness.py
run_step 2 "cron snapshot refresh" python3 scripts/snapshot_cron_status.py
run_step 3 "live status refresh" python3 scripts/update_live_status.py
run_step 4 "research status" python3 scripts/research_status.py

echo "\nDone."