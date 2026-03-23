#!/usr/bin/env bash
set -euo pipefail

: "${OPENAI_ORG_ID:?Set OPENAI_ORG_ID}"
: "${OPENAI_PROJECT:?Set OPENAI_PROJECT}"
: "${LLM_EMOTION_REAL_MODEL:?Set LLM_EMOTION_REAL_MODEL}"
: "${LLM_EMOTION_REAL_MODEL_REGION:?Set LLM_EMOTION_REAL_MODEL_REGION}"

export LLM_EMOTION_ROOT="${LLM_EMOTION_ROOT:-/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion}"
cd "$LLM_EMOTION_ROOT"

python3 scripts/check_real_model_readiness.py
python3 scripts/snapshot_cron_status.py
python3 scripts/update_live_status.py
python3 scripts/research_status.py
