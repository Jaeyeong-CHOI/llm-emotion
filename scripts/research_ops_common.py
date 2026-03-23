#!/usr/bin/env python3
"""Shared helpers for continuous research operations scripts."""

from __future__ import annotations

import datetime as dt
import json
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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_research_state() -> dict[str, Any]:
    state = read_json(STATE_PATH, default={})
    return state if isinstance(state, dict) else {}


def save_research_state(state: dict[str, Any]) -> None:
    write_json(STATE_PATH, state)


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
