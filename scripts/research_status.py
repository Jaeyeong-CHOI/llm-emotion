#!/usr/bin/env python3
from typing import Any

from research_ops_common import display_value, get_stats_snapshot, load_research_state



def main() -> None:
    state = load_research_state()
    snapshot = get_stats_snapshot(state)

    print("# Research Status")
    print(f"- last_run: {display_value(state.get('last_run'))}")
    print(f"- last_success: {display_value(snapshot.get('last_success'))}")
    print(f"- papers_collected: {display_value(snapshot.get('papers_collected'))}")
    print(f"- evidence_rows: {display_value(snapshot.get('evidence_rows'))}")
    print(f"- mock_samples_generated: {display_value(snapshot.get('mock_samples_generated'))}")

    if snapshot.get("last_error"):
        print(f"- last_error: {display_value(snapshot.get('last_error'))}")

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
