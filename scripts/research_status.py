#!/usr/bin/env python3
from typing import Any

from research_ops_common import get_stats_snapshot, load_research_state


def _display_value(value: Any, default: str = "-") -> str:
    """Return user-facing string with a stable placeholder for missing values."""
    return default if value is None else str(value)


def main() -> None:
    state = load_research_state()
    snapshot = get_stats_snapshot(state)

    print("# Research Status")
    print(f"- last_run: {_display_value(state.get('last_run'))}")
    print(f"- last_success: {_display_value(snapshot.get('last_success'))}")
    print(f"- papers_collected: {_display_value(snapshot.get('papers_collected'))}")
    print(f"- evidence_rows: {_display_value(snapshot.get('evidence_rows'))}")
    print(f"- mock_samples_generated: {_display_value(snapshot.get('mock_samples_generated'))}")

    if snapshot.get("last_error"):
        print(f"- last_error: {_display_value(snapshot.get('last_error'))}")

    notes = state.get("notes", [])
    if not isinstance(notes, list):
        notes = []

    recent_notes = notes[-5:]
    if recent_notes:
        print("- recent_notes:")
        for note in recent_notes:
            print(f"  - {note}")


if __name__ == "__main__":
    main()
