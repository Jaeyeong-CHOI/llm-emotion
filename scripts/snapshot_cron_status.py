#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ops" / "cron_runtime_status.json"

CONTINUOUS_ID = "33f59b94-c1e7-44f7-ac2b-f2490043bcc6"
LIVE_REPORT_ID = "36361127-9526-4c77-a742-e83d6b4d701e"


def main():
    p = subprocess.run(
        "openclaw cron list --json",
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )
    if p.returncode != 0:
        raise SystemExit(p.stderr)

    data = json.loads(p.stdout)
    jobs = {j.get("id"): j for j in data.get("jobs", [])}

    def pack(job):
        if not job:
            return {"status": "missing"}
        st = job.get("state", {})
        return {
            "name": job.get("name"),
            "enabled": job.get("enabled"),
            "status": "enabled" if job.get("enabled") else "disabled",
            "lastRunStatus": st.get("lastRunStatus"),
            "lastRunAtMs": st.get("lastRunAtMs"),
            "consecutiveErrors": st.get("consecutiveErrors"),
            "nextRunAtMs": st.get("nextRunAtMs"),
        }

    out = {
        "continuous": pack(jobs.get(CONTINUOUS_ID)),
        "live_report": pack(jobs.get(LIVE_REPORT_ID)),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
