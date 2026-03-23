#!/usr/bin/env bash

# Shared environment loader for llm-emotion shell scripts.

load_research_env() {
  local env_file

  if [[ -n "${LLM_EMOTION_ENV_FILE:-}" ]]; then
    env_file="${LLM_EMOTION_ENV_FILE}"
  elif [[ -n "${ROOT:-}" ]]; then
    env_file="${ROOT}/.env.real_model"
  elif [[ -n "${SCRIPT_DIR:-}" ]]; then
    env_file="${SCRIPT_DIR}/../.env.real_model"
  else
    env_file=".env.real_model"
  fi

  if [ ! -f "$env_file" ]; then
    return 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "$env_file"
  set +a
  return 0
}
