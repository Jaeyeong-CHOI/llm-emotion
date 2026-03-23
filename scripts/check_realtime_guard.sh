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

STEP_LABELS=(
  "real model readiness check"
  "cron snapshot refresh"
  "live status refresh"
  "research status"
)

STEP_COMMANDS=(
  "python3 scripts/check_real_model_readiness.py"
  "python3 scripts/snapshot_cron_status.py"
  "python3 scripts/update_live_status.py"
  "python3 scripts/research_status.py"
)

TOTAL_STEPS="${#STEP_LABELS[@]}"

for i in "${!STEP_LABELS[@]}"; do
  label="${STEP_LABELS[$i]}"
  command="${STEP_COMMANDS[$i]}"
  read -r -a command_parts <<< "$command"
  run_step "$((i + 1))" "$label" "$TOTAL_STEPS" "${command_parts[@]}"
done

printf "\nDone.\n"
