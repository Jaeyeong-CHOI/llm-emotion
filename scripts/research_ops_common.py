#!/usr/bin/env python3
"""Shared helpers for continuous research operations scripts."""

from __future__ import annotations

import copy
import datetime as dt
import json
import os
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def display_value(value: Any, default: str = "-") -> str:
    """Return a user-facing string with stable placeholder for missing values."""
    return default if value is None else str(value)


def render_markdown_rows(rows: list[tuple[str, Any]], indent: str = "") -> list[str]:
    """Render a compact markdown bullet list with stable display conversion."""

    return [
        f"{indent}- {key}: {display_value(value)}" for key, value in rows
    ]


def _normalize_token_set(values: Any) -> set[str]:
    """Normalize an arbitrary token-like container into a unique string set."""

    tokens = list(_iter_token_values(values))
    return {
        normalized
        for raw in tokens
        if (normalized := str(raw).strip())
    }


def _iter_token_values(values: Any):
    """Yield raw token candidates from common container-like inputs."""

    if values is None:
        return ()

    if isinstance(values, str):
        return values.split(",")

    if isinstance(values, dict):
        # Preserve previous behavior (ignoring malformed dict values) while still
        # handling key/value maps that may be serialized as collections.
        return values.keys()

    if isinstance(values, Iterable):
        return values

    return ()


def parse_csv_set(value: Any) -> set[str]:
    """Parse a comma-separated value list into a normalized set."""
    return _normalize_token_set(value)


def row_list_values(row: dict[str, Any], field: str) -> set[str]:
    """Extract a normalized token set from an iterable row field."""
    return _normalize_token_set(row.get(field, []))


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ops" / "research_state.json"


def now_iso_seconds() -> str:
    """Return an unambiguous UTC ISO-8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)."""
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")



def _is_symlink_path(path: Path) -> bool:
    """Return True when `path` or any parent is a symlink.

    This prevents state-file path traversal via symlink replacement while still
    preserving strict local-path safety checks for reads and writes.
    """
    current = path
    while True:
        if current.is_symlink():
            return True
        if current == current.parent:
            return False
        current = current.parent


def read_json(path: Path, default: Any | None = None) -> Any:
    """Read JSON with a defensive fallback on missing/invalid files.

    Returning a deep-copied fallback prevents accidental shared-state mutation
    when callers pass mutable defaults (dict/list).
    """
    fallback = {} if default is None else default

    # Ignore unsafe symlink-backed paths for local state files.
    if not path.exists() or _is_symlink_path(path):
        return copy.deepcopy(fallback)

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, TypeError):
        # Keep behavior deterministic when files are missing, corrupted, or
        # temporarily incomplete, while surfacing the issue to callers via
        # fallback data.
        return copy.deepcopy(fallback)


def as_dict(value: Any) -> dict[str, Any]:
    """Coerce unknown JSON payloads into a dict for defensive callers."""
    return value if isinstance(value, dict) else {}


def read_json_dict(path: Path) -> dict[str, Any]:
    """Read a JSON file and always return a dictionary."""
    return as_dict(read_json(path, default={}))


def get_nested_field(
    payload: dict[str, Any],
    section: str,
    field: str,
    default: str = "unknown",
) -> str:
    """Read a nested field from a mapping with defensive type checks."""
    section_data = payload.get(section)
    if not isinstance(section_data, dict):
        return default
    return display_value(section_data.get(field), default)


def write_json(path: Path, payload: Any) -> None:
    """Atomically write *payload* as JSON to *path* (mode 0o600).

    Uses a sibling temp-file + rename to avoid half-written state files.
    Refuses writes through symlink-backed paths to prevent path-hijacking.
    """
    # Harden against symlink-based path hijacking for local state files.
    if _is_symlink_path(path):
        raise RuntimeError(f"refusing to write via symlink path: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False, indent=2)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(data)
        handle.flush()
        os.fchmod(handle.fileno(), 0o600)
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)

    temp_path.replace(path)

    # Best-effort directory fsync so rename metadata is durably recorded.
    try:
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        pass


def load_research_state() -> dict[str, Any]:
    return read_json_dict(STATE_PATH)


def save_research_state(state: dict[str, Any]) -> None:
    write_json(STATE_PATH, state)


def safe_int(value: Any, default: int = 0) -> int:
    """Best-effort integer coercion for potentially dirty numeric inputs.

    This helper tolerates strings/None/float-like values and falls back to a
    caller-provided default when coercion fails. Booleans are treated as
    invalid values to avoid accidental True/False -> 1/0 coercion.
    """
    if isinstance(value, bool) or value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default




def get_stats_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """Return a stable stats snapshot with defaults for missing fields."""
    stats = state.get("stats", {})
    if not isinstance(stats, dict):
        stats = {}
    return {
        "papers_collected": safe_int(stats.get("papers_collected", 0)),
        "evidence_rows": safe_int(stats.get("evidence_rows", 0)),
        "mock_samples_generated": safe_int(stats.get("mock_samples_generated", 0)),
        "last_success": state.get("last_success", "-"),
        "last_error": state.get("last_error"),
    }


def dedupe_preserve_order(values: object) -> list[str]:
    """Preserve insertion order while removing duplicates in a compact form.

    Non-string values are stringified, whitespace-only tokens are dropped, and
    None/blank entries are ignored to harden queue/config-style inputs.
    """

    seen: set[str] = set()
    deduped: list[str] = []
    for value in (values or []):
        token = str(value).strip() if value is not None else ""
        if not token or token in seen:
            continue
        seen.add(token)
        deduped.append(token)

    return deduped


def pct(numerator: int, denominator: int) -> float:
    """Return a safe percentage (0–1 scale) rounded to 4 decimal places."""
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def append_note(state: dict[str, Any], text: str, limit: int = 40) -> None:
    """Append a timestamped *text* entry to ``state["notes"]``, keeping the
    most recent *limit* entries.

    *limit* is already annotated as ``int``; ``max(1, limit)`` guards against
    a caller passing 0 or a negative value without the overhead of a
    try/except that would mask genuine type errors.
    """
    notes = state.get("notes")
    if not isinstance(notes, list):
        notes = []

    safe_limit = max(1, limit)
    notes.append(f"[{now_iso_seconds()}] {text}")
    state["notes"] = notes[-safe_limit:]
