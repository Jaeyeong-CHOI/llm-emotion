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

printf "[1/4] real model readiness check\n"
python3 scripts/check_real_model_readiness.py

printf "\n[2/4] cron snapshot refresh\n"
python3 scripts/snapshot_cron_status.py

printf "\n[3/4] live status refresh\n"
python3 scripts/update_live_status.py

printf "\n[4/4] research status\n"
python3 scripts/research_status.py

echo "\nDone."
