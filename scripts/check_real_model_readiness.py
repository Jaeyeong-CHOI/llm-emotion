#!/usr/bin/env python3
"""Simple readiness check for real-model transition."""

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ops" / "real_model_readiness.json"

DEFAULT_REQUIRED = [
    "OPENAI_API_KEY",
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT",
    "LLM_EMOTION_REAL_MODEL",
    "LLM_EMOTION_REAL_MODEL_REGION",
]

def check_var(name: str):
    value = os.getenv(name)
    return bool(value and str(value).strip()), bool(value and "sk-" in str(value))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    status = {}
    missing = []
    suspicious = []
    for name in DEFAULT_REQUIRED:
        exists, plausible = check_var(name)
        status[name] = exists
        if not exists:
            missing.append(name)
        elif name == "OPENAI_API_KEY" and not plausible:
            suspicious.append(name)

    ready = not missing and not suspicious
    payload = {
        "ready": ready,
        "required_vars": DEFAULT_REQUIRED,
        "available_vars": status,
        "missing_vars": missing,
        "suspicious_vars": suspicious,
        "notes": [] if ready else ["환경변수 미설정 또는 포맷 점검 필요"],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ready=" + str(ready).lower())
    if not ready:
        if missing:
            print("missing_vars=" + ",".join(missing))
        if suspicious:
            print("suspicious_vars=" + ",".join(suspicious))

if __name__ == "__main__":
    main()
