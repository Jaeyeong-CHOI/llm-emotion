#!/usr/bin/env python3
"""Real-model transition readiness 체크와 환경 변수 계약 검증 유틸리티."""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from research_ops_common import write_json

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

# 자주 쓰는 정규식은 미리 컴파일
CONTROL_CHAR_PATTERN = re.compile(r"[\r\n\t]|[\x00-\x08\x0b-\x1f\x7f]")
ENDPOINT_SCHEME_PATTERN = re.compile(r"^https?://")
ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def is_placeholder(value: str) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return False
    return any(re.match(p, v) for p in PLACEHOLDER_PATTERNS)


def has_unsafe_chars(value: str) -> bool:
    """Detect control characters that can break env-var handling."""
    return bool(CONTROL_CHAR_PATTERN.search(value or ""))


def is_probable_openai_api_key(value: str) -> bool:
    """Reject obviously non-OpenAI keys while allowing both sk- and sk-proj-."""
    v = (value or "").strip()
    return bool(re.match(r"^(sk-|sk-proj-)", v))


def dedupe_preserve_order(values: list[str]) -> list[str]:
    """Preserve insertion order while removing duplicates."""
    return list(dict.fromkeys(values))


def normalize_env_name(token: str) -> str:
    """Trim and reject obviously invalid environment-variable tokens."""
    candidate = token.strip()
    if not candidate:
        return ""
    if not ENV_NAME_PATTERN.match(candidate):
        return ""
    return candidate


def parse_env_var_list(raw: str, default: list[str]) -> list[str]:
    """Parse comma/space-separated env-var names with stable de-duplication."""
    raw_tokens = re.split(r"[\s,]+", (raw or "").strip())

    tokens: list[str] = []
    invalid: list[str] = []

    for raw_token in raw_tokens:
        cleaned = raw_token.strip()
        if not cleaned:
            continue
        normalized = normalize_env_name(cleaned)
        if normalized:
            tokens.append(normalized)
        else:
            invalid.append(cleaned)

    # 입력이 비면 기본값 사용(기존 동작 유지)
    if not tokens:
        tokens = dedupe_preserve_order(default)

    # 위험한 이름은 제외하고 경고만 출력해 실패를 유발하지 않는다.
    if invalid:
        print(
            f"[check_real_model_readiness] ignore invalid env var names: {', '.join(invalid)}",
            file=sys.stderr,
        )

    # Keep first occurrence order so CLI intent stays predictable.
    return dedupe_preserve_order(tokens)


def check_var(value: str):
    exists = bool(value and str(value).strip())
    placeholder = is_placeholder(str(value or ""))
    unsafe = has_unsafe_chars(value)
    return exists, placeholder, unsafe


@dataclass(frozen=True)
class EnvBlock:
    """Container for one environment-variable requirement block."""

    names: list[str]
    available: dict[str, bool]
    missing: list[str]
    placeholder: list[str]
    unsafe: list[str]


def check_env_block(names: list[str]) -> EnvBlock:
    """Evaluate a named environment-variable block and return diagnostics."""

    status: dict[str, bool] = {}
    missing: list[str] = []
    placeholder_vars: list[str] = []
    unsafe_vars: list[str] = []

    for name in names:
        value = os.getenv(name)
        exists, placeholder, unsafe = check_var(value)
        status[name] = exists

        if not exists:
            missing.append(name)
            continue
        if placeholder:
            placeholder_vars.append(name)
        if unsafe:
            unsafe_vars.append(name)

    return EnvBlock(
        names=names,
        available=status,
        missing=missing,
        placeholder=placeholder_vars,
        unsafe=unsafe_vars,
    )


def _append_optional_note(
    notes: list[str],
    variables: list[str],
    message: str,
) -> None:
    if variables:
        notes.append(f"{message}: {', '.join(variables)}")


def summarize_readiness_issues(
    required_missing: list[str],
    required_placeholder_vars: list[str],
    required_unsafe_vars: list[str],
    optional_missing: list[str],
    optional_placeholder_vars: list[str],
    optional_unsafe_vars: list[str],
    endpoint_scheme_ok: bool,
    suspicious: list[str],
) -> list[str]:
    """Collect human-readable Korean notes for readiness diagnostics."""

    notes: list[str] = []
    if required_missing:
        notes.append("필수 환경변수 누락")
    _append_optional_note(notes, required_placeholder_vars, "필수 환경변수에 placeholder 값 존재")
    _append_optional_note(
        notes,
        required_unsafe_vars,
        "필수 환경변수에 개행/탭 등 제어문자 존재",
    )
    _append_optional_note(notes, optional_missing, "선택 환경변수 미설정(권장)")
    _append_optional_note(
        notes,
        optional_placeholder_vars,
        "선택 환경변수에 placeholder 값 존재",
    )
    _append_optional_note(
        notes,
        optional_unsafe_vars,
        "선택 환경변수에 개행/탭 등 제어문자 존재",
    )
    if not endpoint_scheme_ok:
        notes.append("OPENAI_BASE_URL 스킴 미일치")
    if "OPENAI_API_KEY" in suspicious:
        notes.append("OPENAI_API_KEY 형식 점검 필요")
    if not notes:
        notes.append("실모델 전환 준비 완료")
    return notes


def build_readiness_payload(
    required: EnvBlock,
    optional: EnvBlock,
    suspicious: list[str],
    endpoint_scheme_ok: bool,
) -> dict:
    """Build a unified payload dict to avoid duplicated serialization logic."""

    required_missing = required.missing
    required_placeholder_vars = required.placeholder
    required_unsafe_vars = required.unsafe
    optional_missing = optional.missing
    optional_placeholder_vars = optional.placeholder
    optional_unsafe_vars = optional.unsafe

    notes = summarize_readiness_issues(
        required_missing=required_missing,
        required_placeholder_vars=required_placeholder_vars,
        required_unsafe_vars=required_unsafe_vars,
        optional_missing=optional_missing,
        optional_placeholder_vars=optional_placeholder_vars,
        optional_unsafe_vars=optional_unsafe_vars,
        endpoint_scheme_ok=endpoint_scheme_ok,
        suspicious=suspicious,
    )

    return {
        "required_missing": required_missing,
        "required_placeholder": required_placeholder_vars,
        "required_unsafe": required_unsafe_vars,
        "optional_missing": optional_missing,
        "optional_placeholder": optional_placeholder_vars,
        "optional_unsafe": optional_unsafe_vars,
        "notes": notes,
        "payload": {
            "ready": not required_missing and not required_placeholder_vars and not required_unsafe_vars and not suspicious,
            "required_vars": required.names,
            "optional_vars": optional.names,
            "available_vars": {**required.available, **optional.available},
            "missing_vars": required_missing,
            "optional_missing_vars": optional_missing,
            "placeholder_vars": required_placeholder_vars,
            "optional_placeholder_vars": optional_placeholder_vars,
            "unsafe_vars": required_unsafe_vars,
            "optional_unsafe_vars": optional_unsafe_vars,
            "suspicious_vars": sorted(set(suspicious)),
            "endpoint": {
                "OPENAI_BASE_URL_present": bool(os.getenv("OPENAI_BASE_URL", "").strip()),
                "scheme_ok": endpoint_scheme_ok,
            },
            "notes": notes,
        },
    }


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

    required_names = parse_env_var_list(args.required_vars, DEFAULT_REQUIRED)
    optional_names = parse_env_var_list(args.optional_vars, OPTIONAL_PROJECT_VARS)

    required = check_env_block(required_names)
    optional = check_env_block(optional_names)

    endpoint = os.getenv("OPENAI_BASE_URL", "").strip()
    endpoint_scheme_ok = True
    suspicious = []
    if args.require_endpoint_scheme and endpoint:
        endpoint_scheme_ok = bool(ENDPOINT_SCHEME_PATTERN.match(endpoint))
        if not endpoint_scheme_ok:
            suspicious.append("OPENAI_BASE_URL")

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if api_key and not is_probable_openai_api_key(api_key):
        suspicious.append("OPENAI_API_KEY")

    # 실모델 실행 게이트는 강제 required 기준 + API 키 유효성 + 엔드포인트 스킴 점검
    readiness = build_readiness_payload(
        required=required,
        optional=optional,
        suspicious=suspicious,
        endpoint_scheme_ok=endpoint_scheme_ok,
    )

    payload = readiness["payload"]
    ready = payload["ready"]

    write_json(Path(args.out), payload)
    print("ready=" + str(ready).lower())


if __name__ == "__main__":
    main()
