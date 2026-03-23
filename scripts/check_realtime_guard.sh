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

# label|command for each step
STEP_DEFS=(
  "real model readiness check|python3 scripts/check_real_model_readiness.py"
  "cron snapshot refresh|python3 scripts/snapshot_cron_status.py"
  "live status refresh|python3 scripts/update_live_status.py"
  "research status|python3 scripts/research_status.py"
)

TOTAL_STEPS=${#STEP_DEFS[@]}

INDEX=1
for step in "${STEP_DEFS[@]}"; do
  label=""
  command_line=""
  IFS='|' read -r label command_line <<< "$step"
  if [ -z "$label" ] || [ -z "$command_line" ]; then
    echo "[warn] malformed step definition: $step" >&2
    continue
  fi

  read -ra command_parts <<< "$command_line"
  run_step "$INDEX" "$label" "$TOTAL_STEPS" "${command_parts[@]}"
  INDEX=$((INDEX + 1))
done

printf "\nDone.\n"
