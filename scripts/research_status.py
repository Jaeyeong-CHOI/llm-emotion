#!/usr/bin/env python3
from typing import Any

from research_ops_common import get_stats_snapshot, load_research_state, render_markdown_rows


def main() -> None:
    state = load_research_state()
    snapshot = get_stats_snapshot(state)

    print("# Research Status")

    rows = [
        ("last_run", state.get("last_run")),
        ("last_success", snapshot.get("last_success")),
        ("papers_collected", snapshot.get("papers_collected")),
        ("evidence_rows", snapshot.get("evidence_rows")),
        ("mock_samples_generated", snapshot.get("mock_samples_generated")),
    ]
    print("\n".join(render_markdown_rows(rows)))

    if snapshot.get("last_error"):
        print(
            "\n".join(
                render_markdown_rows([("last_error", snapshot.get("last_error"))])
            )
        )

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
