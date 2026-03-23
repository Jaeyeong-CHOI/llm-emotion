#!/usr/bin/env bash
set -euo pipefail

export LLM_EMOTION_ROOT="${LLM_EMOTION_ROOT:-/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion}"
export LLM_EMOTION_REAL_MODEL="${LLM_EMOTION_REAL_MODEL:?missing}"
export LLM_EMOTION_REAL_MODEL_REGION="${LLM_EMOTION_REAL_MODEL_REGION:?missing}"

cd "$LLM_EMOTION_ROOT"

# Reuse the shared guard pipeline instead of duplicating command sequence.
# (readiness -> cron snapshot -> live status -> research status)
bash scripts/check_realtime_guard.sh
