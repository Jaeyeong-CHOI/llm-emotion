#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
state_path = ROOT / "ops" / "research_state.json"
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

print("# Research Status")
print(f"- last_run: {state.get('last_run')}")
print(f"- last_success: {state.get('last_success')}")
print(f"- papers_collected: {(state.get('stats') or {}).get('papers_collected')}")
print(f"- evidence_rows: {(state.get('stats') or {}).get('evidence_rows')}")
print(f"- mock_samples_generated: {(state.get('stats') or {}).get('mock_samples_generated')}")
if state.get("last_error"):
    print(f"- last_error: {state['last_error']}")

notes = state.get("notes", [])[-5:]
if notes:
    print("- recent_notes:")
    for n in notes:
        print(f"  - {n}")
