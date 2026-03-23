#!/usr/bin/env bash
set -euo pipefail

export LLM_EMOTION_ROOT="${LLM_EMOTION_ROOT:-/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion}"
export LLM_EMOTION_REAL_MODEL="${LLM_EMOTION_REAL_MODEL:?missing}"
export LLM_EMOTION_REAL_MODEL_REGION="${LLM_EMOTION_REAL_MODEL_REGION:?missing}"

cd "$LLM_EMOTION_ROOT"

python3 scripts/check_real_model_readiness.py
python3 scripts/snapshot_cron_status.py
python3 scripts/update_live_status.py
python3 scripts/research_status.py
