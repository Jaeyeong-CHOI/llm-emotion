#!/usr/bin/env python3
"""Real-model transition readiness check with env contract validation."""

import argparse
import json
import os
import re
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

PLACEHOLDER_PATTERNS = (
    r"^your[_-]",
    r"^replace[_-]",
    r"^example",
    r"^test$",
    r"^todo$",
    r"^changeme$",
)


def is_placeholder(value: str) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return False
    return any(re.match(p, v) for p in PLACEHOLDER_PATTERNS)


def parse_required_vars(raw: str):
    if not raw:
        return DEFAULT_REQUIRED
    tokens = re.split(r"[\s,]+", raw.strip())
    vars_ = [t for t in tokens if t]
    return vars_ or DEFAULT_REQUIRED


def check_var(name: str, value: str):
    exists = bool(value and str(value).strip())
    placeholder = is_placeholder(str(value or ""))
    return exists, placeholder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument(
        "--required-vars",
        default=",".join(DEFAULT_REQUIRED),
        help="comma/space separated env var names to enforce",
    )
    ap.add_argument(
        "--require-endpoint-scheme",
        action="store_true",
        help="when OPENAI_BASE_URL is present, require http:// or https:// scheme",
    )
    args = ap.parse_args()

    required = parse_required_vars(args.required_vars)
    status = {}
    missing = []
    suspicious = []
    placeholder_vars = []

    for name in required:
        value = os.getenv(name)
        exists, placeholder = check_var(name, value)
        status[name] = exists
        if not exists:
            missing.append(name)
            continue
        if placeholder:
            placeholder_vars.append(name)
        if name == "OPENAI_API_KEY" and "sk-" not in str(value):
            suspicious.append(name)

    endpoint = os.getenv("OPENAI_BASE_URL", "").strip()
    endpoint_scheme_ok = True
    if args.require_endpoint_scheme and endpoint:
        endpoint_scheme_ok = bool(re.match(r"^https?://", endpoint))
        if not endpoint_scheme_ok:
            suspicious.append("OPENAI_BASE_URL")

    ready = not missing and not suspicious and not placeholder_vars
    notes = []
    if missing:
        notes.append("필수 환경변수 누락")
    if placeholder_vars:
        notes.append("placeholder/샘플값으로 보이는 환경변수 존재")
    if suspicious:
        notes.append("형식 점검 필요 환경변수 존재")
    if not notes:
        notes.append("실모델 전환 준비 완료")

    payload = {
        "ready": ready,
        "required_vars": required,
        "available_vars": status,
        "missing_vars": missing,
        "placeholder_vars": placeholder_vars,
        "suspicious_vars": sorted(set(suspicious)),
        "endpoint": {
            "OPENAI_BASE_URL_present": bool(endpoint),
            "scheme_ok": endpoint_scheme_ok,
        },
        "notes": notes,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ready=" + str(ready).lower())


if __name__ == "__main__":
    main()
