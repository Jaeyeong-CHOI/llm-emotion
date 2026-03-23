#!/usr/bin/env bash
set -euo pipefail

# Copy selected API keys from AVRTG_QUERY_GEN/.env into llm-emotion .env.real_model
# (values are not printed)

SRC_ENV="${AVRTG_ENV_FILE:-/Users/jaeyeong_openclaw/.openclaw/workspace/AVRTG_QUERY_GEN/.env}"
DST_ENV="${LLM_EMOTION_ENV_FILE:-/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion/.env.real_model}"

if [ ! -f "$SRC_ENV" ]; then
  echo "ERROR: source env not found: $SRC_ENV" >&2
  exit 1
fi

# read source env safely
source "$SRC_ENV"

: "${OPENAI_API_KEY:?OPENAI_API_KEY missing in source}"
: "${GEMINI_API_KEY:?GEMINI_API_KEY missing in source}"

# keep existing destination then replace/add keys
python3 - "$SRC_ENV" "$DST_ENV" <<'PY'
import os
import re
import sys
from pathlib import Path

src, dst = sys.argv[1], sys.argv[2]
# values kept in environment by caller
pairs = [
    ('OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY','')),
    ('GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY','')),
]

# required keys for llm-emotion
pairs += [
    ('LLM_EMOTION_REAL_MODEL', os.environ.get('LLM_EMOTION_REAL_MODEL','gpt-4o')),
    ('LLM_EMOTION_REAL_MODEL_REGION', os.environ.get('LLM_EMOTION_REAL_MODEL_REGION','us-east-1')),
    ('OPENAI_ORG_ID', os.environ.get('OPENAI_ORG_ID','')),
    ('OPENAI_PROJECT', os.environ.get('OPENAI_PROJECT','')),
]

# if user has manually set org/project, keep them; otherwise preserve old values if present
existing = {}
if Path(dst).exists():
    for line in Path(dst).read_text().splitlines():
        if not line or line.startswith('#') or '=' not in line:
            continue
        k,v=line.split('=',1)
        existing[k.strip()] = v

for k,_ in pairs:
    if k in os.environ and os.environ[k]:
        existing[k] = os.environ[k]

# write preserving order of existing + new keys
out = []
keys_to_keep = [k for k,_ in pairs]
seen = set()
if Path(dst).exists():
    for line in Path(dst).read_text().splitlines():
        if not line or '=' not in line:
            out.append(line)
            continue
        k,_=line.split('=',1)
        k=k.strip()
        if k in keys_to_keep:
            if k in seen:
                continue
            out.append(f"{k}={existing[k]}")
            seen.add(k)
        else:
            out.append(line)

for k,_ in pairs:
    if k in seen:
        continue
    if k in existing and existing[k] != '':
        out.append(f"{k}={existing[k]}")
        seen.add(k)

# append required keys that exist now (at least gpt/gemini)
out_tail=[]
for k,_ in pairs:
    if k in existing and existing[k] != '':
        if k not in [line.split('=',1)[0].strip() for line in out]:
            out_tail.append(f"{k}={existing[k]}")

if out and out[-1] != '' and out_tail:
    out.append('')
out.extend(out_tail)

Path(dst).parent.mkdir(parents=True, exist_ok=True)
Path(dst).write_text('\n'.join(out).rstrip()+'\n', encoding='utf-8')
PY

chmod 600 "$DST_ENV"

echo "Synced keys from $SRC_ENV -> $DST_ENV"
echo "SET: OPENAI_API_KEY, GEMINI_API_KEY, LLM_EMOTION_REAL_MODEL, LLM_EMOTION_REAL_MODEL_REGION"
[ -n "${OPENAI_ORG_ID:-}" ] && echo "KEEP: OPENAI_ORG_ID"
[ -n "${OPENAI_PROJECT:-}" ] && echo "KEEP: OPENAI_PROJECT"
