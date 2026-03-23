#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion"
cd "$ROOT"

# Optional dotenv file path
if [[ -n "${LLM_EMOTION_ENV_FILE:-}" && -f "$LLM_EMOTION_ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$LLM_EMOTION_ENV_FILE"
  set +a
elif [[ -f "$ROOT/.env.real_model" ]]; then
  set -a
  source "$ROOT/.env.real_model"
  set +a
fi

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
