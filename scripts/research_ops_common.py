#!/usr/bin/env python3
"""Shared helpers for continuous research operations scripts."""

from __future__ import annotations

import datetime as dt
import json
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ops" / "research_state.json"


def now_isoseconds() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def read_json(path: Path, default: Any | None = None) -> Any:
    fallback = {} if default is None else default
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False, indent=2)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(data)
        handle.flush()
        temp_path = Path(handle.name)

    temp_path.replace(path)


def load_research_state() -> dict[str, Any]:
    state = read_json(STATE_PATH, default={})
    return state if isinstance(state, dict) else {}


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
