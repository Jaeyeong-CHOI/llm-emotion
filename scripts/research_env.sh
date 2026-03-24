#!/usr/bin/env bash

# Shared environment loader for llm-emotion shell scripts.

load_research_env() {
  local env_file
  local -a candidates

  if [[ -n "${LLM_EMOTION_ENV_FILE:-}" ]]; then
    candidates=("${LLM_EMOTION_ENV_FILE}")
  elif [[ -n "${ROOT:-}" ]]; then
    candidates=("${ROOT}/.env.real_model")
  elif [[ -n "${SCRIPT_DIR:-}" ]]; then
    candidates=("${SCRIPT_DIR}/../.env.real_model")
  else
    candidates=(".env.real_model")
  fi

  # 보안/안정성을 위해 일반 파일만 허용(심볼릭 링크/소켓 등 회피).
  for env_file in "${candidates[@]}"; do
    if [ -f "$env_file" ] && [ ! -L "$env_file" ]; then
      set -a
      # shellcheck disable=SC1090
      source "$env_file"
      set +a
      return 0
    fi
  done

  return 1
}
