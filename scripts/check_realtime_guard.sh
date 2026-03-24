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
  local total="$3"
  shift 3

  local -a command=("$@")
  printf "[%s/%s] %s\n" "$index" "$total" "$label"
  "${command[@]}"
}

run_step 1 "real model readiness check" 4 python3 scripts/check_real_model_readiness.py
run_step 2 "cron snapshot refresh" 4 python3 scripts/snapshot_cron_status.py
run_step 3 "live status refresh" 4 python3 scripts/update_live_status.py
run_step 4 "research status" 4 python3 scripts/research_status.py

printf "\nDone.\n"
