#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/research_env.sh"

load_research_env

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