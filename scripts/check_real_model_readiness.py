#!/usr/bin/env python3
"""Real-model transition readiness 체크와 환경 변수 계약 검증 유틸리티."""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from research_ops_common import dedupe_preserve_order, write_json

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
ENV_LIST_SPLIT_PATTERN = re.compile(r"[\s,;]+")


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



def normalize_env_name(token: str) -> str:
    """Trim and reject obviously invalid environment-variable tokens."""
    candidate = token.strip()
    if not candidate:
        return ""
    if not ENV_NAME_PATTERN.match(candidate):
        return ""
    return candidate


def parse_env_var_list(raw: str, default: list[str]) -> list[str]:
    """Parse comma/space/semicolon-separated env-var names with stable de-duplication."""
    raw_tokens = ENV_LIST_SPLIT_PATTERN.split((raw or "").strip()) if (raw or "").strip() else []

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

    if not tokens:
        tokens = dedupe_preserve_order(default)

    invalid = dedupe_preserve_order(invalid)

    # 위험한 이름은 제외하고 경고만 출력해 실패를 유발하지 않는다.
    if invalid:
        print(
            f"[check_real_model_readiness] ignore invalid env var names: {', '.join(invalid)}",
            file=sys.stderr,
        )

    # Keep first occurrence order so CLI intent stays predictable.
    return dedupe_preserve_order(tokens)


def split_required_optional_vars(
    required_raw: list[str], optional_raw: list[str]
) -> tuple[list[str], list[str], list[str]]:
    """Deduplicate names and remove duplicates from optional that already appear in required."""

    required = dedupe_preserve_order(required_raw)
    optional_clean = dedupe_preserve_order(optional_raw)

    unique_optional: list[str] = []
    overlap: list[str] = []
    required_set = set(required)

    for name in optional_clean:
        if name in required_set:
            overlap.append(name)
            continue
        unique_optional.append(name)

    return required, unique_optional, overlap


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
    duplicate_requested_vars: list[str],
    endpoint_scheme_ok: bool,
    suspicious: list[str],
) -> list[str]:
    """Collect human-readable Korean notes for readiness diagnostics."""

    notes: list[str] = []
    if required_missing:
        notes.append("필수 환경변수 누락")

    optional_notes = [
        (required_placeholder_vars, "필수 환경변수에 placeholder 값 존재"),
        (required_unsafe_vars, "필수 환경변수에 개행/탭 등 제어문자 존재"),
        (optional_missing, "선택 환경변수 미설정(권장)"),
        (optional_placeholder_vars, "선택 환경변수에 placeholder 값 존재"),
        (optional_unsafe_vars, "선택 환경변수에 개행/탭 등 제어문자 존재"),
    ]

    for vars_, message in optional_notes:
        _append_optional_note(notes, vars_, message)

    if duplicate_requested_vars:
        notes.append(
            "required/optional env var 중복 지정: "
            + ", ".join(duplicate_requested_vars)
        )
    if not endpoint_scheme_ok:
        notes.append("OPENAI_BASE_URL 스킴 미일치")
    if "OPENAI_API_KEY" in suspicious:
        notes.append("OPENAI_API_KEY 형식 점검 필요")
    if not notes:
        notes.append("실모델 전환 준비 완료")
    return notes


def _block_payload(block: EnvBlock, *, kind: str) -> dict:
    """Convert an EnvBlock into a compact payload section and keep key names aligned."""

    return {
        f"{kind}_missing": block.missing,
        f"{kind}_placeholder": block.placeholder,
        f"{kind}_unsafe": block.unsafe,
        f"{kind}_available": block.available,
    }

def _build_readiness_summary_payload(
    required_payload: dict,
    optional_payload: dict,
    notes: list[str],
) -> dict:
    """Build the top-level readiness summary payload from required/optional summaries."""

    return {
        **required_payload,
        **optional_payload,
        "notes": notes,
    }


def _build_endpoint_payload(base_url: str, endpoint_scheme_ok: bool) -> dict:
    """Build endpoint inspection fields for readiness payload."""

    return {
        "OPENAI_BASE_URL_present": bool(base_url.strip()),
        "scheme_ok": endpoint_scheme_ok,
    }


def _build_env_payload_fields(
    required_payload: dict,
    optional_payload: dict,
) -> dict:
    """Normalize required/optional block summaries into payload-level fields."""

    return {
        "missing_vars": required_payload["required_missing"],
        "optional_missing_vars": optional_payload["optional_missing"],
        "placeholder_vars": required_payload["required_placeholder"],
        "optional_placeholder_vars": optional_payload["optional_placeholder"],
        "unsafe_vars": required_payload["required_unsafe"],
        "optional_unsafe_vars": optional_payload["optional_unsafe"],
    }


def _merge_available_vars(
    required_payload: dict,
    optional_payload: dict,
) -> dict:
    """Merge required/optional availability maps in a single place."""

    return {
        **required_payload["required_available"],
        **optional_payload["optional_available"],
    }


def build_readiness_payload(
    required: EnvBlock,
    optional: EnvBlock,
    duplicate_requested_vars: list[str],
    suspicious: list[str],
    endpoint_scheme_ok: bool,
    endpoint: str,
) -> dict:
    """Build a unified payload dict to avoid duplicated serialization logic."""

    required_payload = _block_payload(required, kind="required")
    optional_payload = _block_payload(optional, kind="optional")

    notes = summarize_readiness_issues(
        required_missing=required_payload["required_missing"],
        required_placeholder_vars=required_payload["required_placeholder"],
        required_unsafe_vars=required_payload["required_unsafe"],
        optional_missing=optional_payload["optional_missing"],
        optional_placeholder_vars=optional_payload["optional_placeholder"],
        optional_unsafe_vars=optional_payload["optional_unsafe"],
        duplicate_requested_vars=duplicate_requested_vars,
        endpoint_scheme_ok=endpoint_scheme_ok,
        suspicious=suspicious,
    )

    suspicious_vars = sorted(set(suspicious))
    payload_summary = _build_readiness_summary_payload(
        required_payload=required_payload,
        optional_payload=optional_payload,
        notes=notes,
    )

    readiness_ok = (
        not required_payload["required_missing"]
        and not required_payload["required_placeholder"]
        and not required_payload["required_unsafe"]
        and not suspicious_vars
    )

    return {
        **payload_summary,
        "payload": {
            "ready": readiness_ok,
            "required_vars": required.names,
            "optional_vars": optional.names,
            "available_vars": _merge_available_vars(
                required_payload=required_payload,
                optional_payload=optional_payload,
            ),
            **_build_env_payload_fields(
                required_payload=required_payload,
                optional_payload=optional_payload,
            ),
            "suspicious_vars": suspicious_vars,
            "endpoint": _build_endpoint_payload(
                base_url=endpoint,
                endpoint_scheme_ok=endpoint_scheme_ok,
            ),
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

    required_names, optional_names, duplicate_requested_vars = split_required_optional_vars(
        required_raw=parse_env_var_list(args.required_vars, DEFAULT_REQUIRED),
        optional_raw=parse_env_var_list(args.optional_vars, OPTIONAL_PROJECT_VARS),
    )

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
        duplicate_requested_vars=duplicate_requested_vars,
        suspicious=suspicious,
        endpoint_scheme_ok=endpoint_scheme_ok,
        endpoint=endpoint,
    )

    payload = readiness["payload"]
    ready = payload["ready"]

    write_json(Path(args.out), payload)
    print("ready=" + str(ready).lower())


if __name__ == "__main__":
    main()
