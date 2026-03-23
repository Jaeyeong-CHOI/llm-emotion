#!/usr/bin/env bash
set -euo pipefail

# Copy selected API keys from AVRTG_QUERY_GEN/.env into llm-emotion .env.real_model
# (values are not printed).

SRC_ENV="${AVRTG_ENV_FILE:-/Users/jaeyeong_openclaw/.openclaw/workspace/AVRTG_QUERY_GEN/.env}"
DST_ENV="${LLM_EMOTION_ENV_FILE:-/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion/.env.real_model}"

if [ ! -f "$SRC_ENV" ]; then
  echo "ERROR: source env not found: $SRC_ENV" >&2
  exit 1
fi

python3 - "$SRC_ENV" "$DST_ENV" <<'PY'
import sys
from pathlib import Path


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def parse_file_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def extract_env_map(lines: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw in lines:
        if not raw or "=" not in raw or raw.lstrip().startswith("#"):
            continue
        key, value = raw.split("=", 1)
        env[key.strip()] = value
    return env


src_path = Path(sys.argv[1])
dst_path = Path(sys.argv[2])

source = load_env(src_path)
for required_key in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
    if not source.get(required_key):
        raise SystemExit(f"ERROR: {required_key} missing in source env")

existing_lines = parse_file_lines(dst_path)
existing_map = extract_env_map(existing_lines)

pairs = [
    ("OPENAI_API_KEY", source.get("OPENAI_API_KEY", ""), True),
    ("GEMINI_API_KEY", source.get("GEMINI_API_KEY", ""), True),
    ("LLM_EMOTION_REAL_MODEL", source.get("LLM_EMOTION_REAL_MODEL", "gpt-4o"), True),
    ("LLM_EMOTION_REAL_MODEL_REGION", source.get("LLM_EMOTION_REAL_MODEL_REGION", "us-east-1"), True),
    ("OPENAI_ORG_ID", source.get("OPENAI_ORG_ID", existing_map.get("OPENAI_ORG_ID", "")), False),
    ("OPENAI_PROJECT", source.get("OPENAI_PROJECT", existing_map.get("OPENAI_PROJECT", "")), False),
]

key_set = {k for k, _, _ in pairs}
updated = {}
for key, value, _ in pairs:
    updated[key] = value

out_lines: list[str] = []
seen: set[str] = set()
for raw in existing_lines:
    if not raw or "=" not in raw:
        out_lines.append(raw)
        continue

    key, _ = raw.split("=", 1)
    key = key.strip()
    if key in key_set:
        if key in seen:
            continue
        out_lines.append(f"{key}={updated[key]}")
        seen.add(key)
    else:
        out_lines.append(raw)

for key, value, required in pairs:
    if key in seen:
        continue
    if not value and not required:
        # optional key: skip empty
        continue
    out_lines.append(f"{key}={value}")
    seen.add(key)

final_map = extract_env_map(out_lines)
for required_key in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
    if not final_map.get(required_key):
        raise SystemExit(f"ERROR: sync failed to set {required_key}")


dst_path.parent.mkdir(parents=True, exist_ok=True)
dst_path.write_text("\n".join(out_lines).rstrip() + "\n", encoding="utf-8")

print(f"Synced keys from {src_path} -> {dst_path}")
for keep_key in ("OPENAI_ORG_ID", "OPENAI_PROJECT"):
    if final_map.get(keep_key):
        print(f"KEEP: {keep_key}")
PY

chmod 600 "$DST_ENV"

echo "SET: OPENAI_API_KEY, GEMINI_API_KEY, LLM_EMOTION_REAL_MODEL, LLM_EMOTION_REAL_MODEL_REGION"
