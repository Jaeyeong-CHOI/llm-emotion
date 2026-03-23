#!/usr/bin/env python3
"""Append compact progress summary to paper/logs/brief_log.md."""

from datetime import datetime

from research_ops_common import ROOT, get_stats_snapshot, read_json_dict

state_path = ROOT / "ops" / "research_state.json"
cron_path = ROOT / "ops" / "cron_runtime_status.json"
log_path = ROOT / "paper" / "logs" / "brief_log.md"


def main():
    state = read_json_dict(state_path)
    cron = read_json_dict(cron_path)

    snapshot = get_stats_snapshot(state)
    continuous = (cron.get("continuous") or {}).get("status", "unknown")
    live = (cron.get("live_report") or {}).get("status", "unknown")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"- [{now}] papers={snapshot['papers_collected']} | evidence={snapshot['evidence_rows']} | "
        f"samples={snapshot['mock_samples_generated']} | continuous={continuous} | live={live} | "
        f"last_success={snapshot['last_success']}"
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# llm-emotion Brief Log\n\n", encoding="utf-8")

    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(f"[brief-log] appended: {line}")


if __name__ == "__main__":
    main()
