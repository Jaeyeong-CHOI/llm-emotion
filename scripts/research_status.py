#!/usr/bin/env python3
from research_ops_common import get_stats_snapshot, load_research_state

state = load_research_state()
snapshot = get_stats_snapshot(state)

print("# Research Status")
print(f"- last_run: {state.get('last_run')}")
print(f"- last_success: {snapshot['last_success']}")
print(f"- papers_collected: {snapshot['papers_collected']}")
print(f"- evidence_rows: {snapshot['evidence_rows']}")
print(f"- mock_samples_generated: {snapshot['mock_samples_generated']}")
if snapshot.get("last_error"):
    print(f"- last_error: {snapshot['last_error']}")

notes = state.get("notes", [])[-5:]
if notes:
    print("- recent_notes:")
    for n in notes:
        print(f"  - {n}")
