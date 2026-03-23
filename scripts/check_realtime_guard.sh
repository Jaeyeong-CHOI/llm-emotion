#!/usr/bin/env bash
set -euo pipefail
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion

printf "[1/4] real model readiness check\n"
python3 scripts/check_real_model_readiness.py

printf "\n[2/4] cron snapshot refresh\n"
python3 scripts/snapshot_cron_status.py

printf "\n[3/4] live status refresh\n"
python3 scripts/update_live_status.py

printf "\n[4/4] research status\n"
python3 scripts/research_status.py

echo "\nDone."
