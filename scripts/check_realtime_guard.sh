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
  local command="$3"
  local idx_total="$4"

  printf "[%s/%s] %s\n" "$index" "$idx_total" "$label"
  bash -lc "$command"
}

STEPS=(
  "real model readiness check|python3 scripts/check_real_model_readiness.py"
  "cron snapshot refresh|python3 scripts/snapshot_cron_status.py"
  "live status refresh|python3 scripts/update_live_status.py"
  "research status|python3 scripts/research_status.py"
)

TOTAL_STEPS="${#STEPS[@]}"

for i in "${!STEPS[@]}"; do
  step="${STEPS[$i]}"
  label="${step%%|*}"
  cmd="${step#*|}"
  run_step "$((i + 1))" "$label" "$cmd" "$TOTAL_STEPS"
done

printf "\nDone.\n"
