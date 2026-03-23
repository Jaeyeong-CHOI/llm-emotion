#!/usr/bin/env python3
"""Real-model transition readiness 체크와 환경 변수 계약 검증 유틸리티."""

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ops" / "real_model_readiness.json"

# 기본 요구값: 실험 실행을 막지 않기 위해 실무 최소값만 강제
DEFAULT_REQUIRED = [
    "OPENAI_API_KEY",
    "LLM_EMOTION_REAL_MODEL",
    "LLM_EMOTION_REAL_MODEL_REGION",
]

# 추적/과금/조직 관리에는 유용하지만 당장은 실행 차단에서 제외하는 보조 변수
OPTIONAL_PROJECT_VARS = [
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT",
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


def parse_env_var_list(raw: str, default: list[str]) -> list[str]:
    """Parse comma/space-separated env-var names with stable de-duplication."""
    if not raw:
        return list(dict.fromkeys(default))

    tokens = re.split(r"[\s,]+", raw.strip())
    vars_ = [t for t in tokens if t]
    if not vars_:
        return list(dict.fromkeys(default))

    # Keep first occurrence order so CLI intent stays predictable.
    return list(dict.fromkeys(vars_))


def check_var(value: str):
    exists = bool(value and str(value).strip())
    placeholder = is_placeholder(str(value or ""))
    return exists, placeholder


def check_vars(names):
    status = {}
    missing = []
    placeholder_vars = []

    for name in names:
        value = os.getenv(name)
        exists, placeholder = check_var(value)
        status[name] = exists
        if not exists:
            missing.append(name)
            continue
        if placeholder:
            placeholder_vars.append(name)
    return status, missing, placeholder_vars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument(
        "--required-vars",
        default=",".join(DEFAULT_REQUIRED),
        help="comma/space separated env var names to enforce",
    )
    ap.add_argument(
        "--optional-vars",
        default=",".join(OPTIONAL_PROJECT_VARS),
        help="comma/space separated env vars to check but not block readiness",
    )
    ap.add_argument(
        "--require-endpoint-scheme",
        action="store_true",
        help="when OPENAI_BASE_URL is present, require http:// or https:// scheme",
    )
    args = ap.parse_args()

    required = parse_env_var_list(args.required_vars, DEFAULT_REQUIRED)
    optional = parse_env_var_list(args.optional_vars, OPTIONAL_PROJECT_VARS)

    required_status, required_missing, required_placeholder_vars = check_vars(required)
    optional_status, optional_missing, optional_placeholder_vars = check_vars(optional)

    endpoint = os.getenv("OPENAI_BASE_URL", "").strip()
    endpoint_scheme_ok = True
    suspicious = []
    if args.require_endpoint_scheme and endpoint:
        endpoint_scheme_ok = bool(re.match(r"^https?://", endpoint))
        if not endpoint_scheme_ok:
            suspicious.append("OPENAI_BASE_URL")

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if api_key and not re.match(r"^sk-", api_key):
        suspicious.append("OPENAI_API_KEY")

    available_vars = {**required_status, **optional_status}

    # 실모델 실행 게이트는 강제 required 기준 + API 키 유효성 + 엔드포인트 스킴 점검
    ready = not required_missing and not required_placeholder_vars and not suspicious

    notes = []
    if required_missing:
        notes.append("필수 환경변수 누락")
    if required_placeholder_vars:
        notes.append("필수 환경변수에 placeholder 값 존재")
    if optional_missing:
        notes.append(f"선택 환경변수 미설정(권장): {', '.join(optional)}")
    if optional_placeholder_vars:
        notes.append(f"선택 환경변수에 placeholder 값 존재: {', '.join(optional_placeholder_vars)}")
    if not endpoint_scheme_ok:
        notes.append("OPENAI_BASE_URL 스킴 미일치")
    if suspicious and "OPENAI_API_KEY" in suspicious:
        notes.append("OPENAI_API_KEY 형식 점검 필요")
    if not notes:
        notes.append("실모델 전환 준비 완료")

    payload = {
        "ready": ready,
        "required_vars": required,
        "optional_vars": optional,
        "available_vars": available_vars,
        "missing_vars": required_missing,
        "optional_missing_vars": optional_missing,
        "placeholder_vars": required_placeholder_vars,
        "optional_placeholder_vars": optional_placeholder_vars,
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
