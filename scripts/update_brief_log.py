#!/usr/bin/env python3
"""Append compact progress summary to paper/logs/brief_log.md."""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
state_path = ROOT / "ops" / "research_state.json"
cron_path = ROOT / "ops" / "cron_runtime_status.json"
log_path = ROOT / "paper" / "logs" / "brief_log.md"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def pick_stats(state):
    s = state.get("stats", {})
    return {
        "papers": s.get("papers_collected", 0),
        "evidence": s.get("evidence_rows", 0),
        "samples": s.get("mock_samples_generated", 0),
        "last_success": state.get("last_success", "-"),
        "last_error": state.get("last_error", None),
    }


def main():
    state = read_json(state_path)
    cron = read_json(cron_path)

    st = pick_stats(state)
    continuous = (cron.get("continuous") or {}).get("status", "unknown")
    live = (cron.get("live_report") or {}).get("status", "unknown")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"- [{now}] papers={st['papers']} | evidence={st['evidence']} | "
        f"samples={st['samples']} | continuous={continuous} | live={live} | "
        f"last_success={st['last_success']}"
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# llm-emotion Brief Log\n\n", encoding="utf-8")

    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(f"[brief-log] appended: {line}")


if __name__ == "__main__":
    main()
