#!/usr/bin/env python3
"""Shared helpers for continuous research operations scripts."""

from __future__ import annotations

import copy
import datetime as dt
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ops" / "research_state.json"


def now_isoseconds() -> str:
    """Return an unambiguous UTC ISO-8601 timestamp for research logs/state."""
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def read_json(path: Path, default: Any | None = None) -> Any:
    """Read JSON with a defensive fallback copy on missing/invalid files.

    Returning a deep-copied fallback prevents accidental shared-state mutation
    when callers pass mutable defaults (dict/list).
    """
    fallback = {} if default is None else default
    if not path.exists():
        return copy.deepcopy(fallback)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return copy.deepcopy(fallback)


def as_dict(value: Any) -> dict[str, Any]:
    """Coerce unknown JSON payloads into a dict for defensive callers."""
    return value if isinstance(value, dict) else {}


def read_json_dict(path: Path) -> dict[str, Any]:
    """Read a JSON file and always return a dictionary."""
    return as_dict(read_json(path, default={}))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False, indent=2)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(data)
        handle.flush()
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


def get_stats_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """Return a stable stats snapshot with defaults for missing fields."""
    stats = state.get("stats", {})
    if not isinstance(stats, dict):
        stats = {}
    return {
        "papers_collected": stats.get("papers_collected", 0),
        "evidence_rows": stats.get("evidence_rows", 0),
        "mock_samples_generated": stats.get("mock_samples_generated", 0),
        "last_success": state.get("last_success", "-"),
        "last_error": state.get("last_error"),
    }


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def append_note(state: dict[str, Any], text: str, limit: int = 40) -> None:
    notes = state.get("notes")
    if not isinstance(notes, list):
        notes = []

    safe_limit = max(1, int(limit))
    notes.append(f"[{now_isoseconds()}] {text}")
    state["notes"] = notes[-safe_limit:]
