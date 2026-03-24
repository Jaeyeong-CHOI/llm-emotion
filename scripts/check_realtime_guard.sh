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

step_labels=(
  "real model readiness check"
  "cron snapshot refresh"
  "live status refresh"
  "research status"
)

step_commands=(
  "python3 scripts/check_real_model_readiness.py"
  "python3 scripts/snapshot_cron_status.py"
  "python3 scripts/update_live_status.py"
  "python3 scripts/research_status.py"
)

total_steps=${#step_labels[@]}

if [ "$total_steps" -ne "${#step_commands[@]}" ]; then
  echo "[guard] mismatch: labels=$total_steps commands=${#step_commands[@]}" >&2
  exit 1
fi

for i in "${!step_labels[@]}"; do
  idx=$((i + 1))
  run_step "$idx" "${step_labels[$i]}" "$total_steps" bash -lc "${step_commands[$i]}"

done

printf "\nDone.\n"
