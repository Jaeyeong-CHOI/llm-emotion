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
TOTAL_STEPS=${#STEP_LABELS[@]}

run_guard_step() {
  local index="$1"
  local -a cmd=()

  case "$index" in
    0)
      cmd=(python3 scripts/check_real_model_readiness.py)
      ;;
    1)
      cmd=(python3 scripts/snapshot_cron_status.py)
      ;;
    2)
      cmd=(python3 scripts/update_live_status.py)
      ;;
    3)
      cmd=(python3 scripts/research_status.py)
      ;;
    *)
      echo "[warn] unknown guard step index: ${index}" >&2
      return 1
      ;;
  esac

  run_step "$((index + 1))" "${STEP_LABELS[index]}" "$TOTAL_STEPS" "${cmd[@]}"
}

for ((i = 0; i < TOTAL_STEPS; i++)); do
  run_guard_step "$i"
done

printf "\nDone.\n"
