#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ops" / "cron_runtime_status.json"

# 기본: 설정값이 있으면 우선 사용
CONTINUOUS_NAME_DEFAULT = "llm-emotion-continuous-research"
LIVE_REPORT_NAME_DEFAULT = "llm-emotion-important-live-report"

# legacy hard-coded fallback IDs (for quick back-compat)
CONTINUOUS_ID_FALLBACK = "33f59b94-c1e7-44f7-ac2b-f2490043bcc6"
LIVE_REPORT_ID_FALLBACK = "36361127-9526-4c77-a742-e83d6b4d701e"


def run_cron_list() -> str:
    p = subprocess.run(
        "openclaw cron list --json",
        cwd=ROOT,
        shell=True,
        text=True,
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "openclaw cron list failed")
    return p.stdout


def find_by_id_or_name(jobs, env_id_key, fallback_id, name_key):
    explicit_id = os.getenv(env_id_key)
    if explicit_id:
        return jobs.get(explicit_id), explicit_id, "env"

    # primary by name
    for j in jobs.values():
        if (j.get("name") or "") == name_key:
            return j, j.get("id"), f"name:{name_key}"

    # substring fallback by contains
    contains_matches = [
        j for j in jobs.values()
        if name_key and name_key in (j.get("name") or "")
    ]
    if len(contains_matches) == 1:
        j = contains_matches[0]
        return j, j.get("id"), f"fuzzy:{name_key}"

    # final fallback: kept for compatibility if names changed
    return jobs.get(fallback_id), fallback_id, "fallback-id"


def pack(job, resolved_id):
    if not job:
        return {"status": "missing", "enabled": False, "resolved_id": resolved_id}
    st = job.get("state", {})
    return {
        "name": job.get("name"),
        "resolved_id": resolved_id,
        "enabled": bool(job.get("enabled", False)),
        "status": "enabled" if job.get("enabled", False) else "disabled",
        "lastRunStatus": st.get("lastRunStatus"),
        "lastRunAtMs": st.get("lastRunAtMs"),
        "consecutiveErrors": st.get("consecutiveErrors"),
        "nextRunAtMs": st.get("nextRunAtMs"),
    }


def main():
    try:
        raw = run_cron_list()
        data = json.loads(raw)
    except Exception as e:
        error = str(e)
        print(error)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({
            "continuous": {"status": "missing", "enabled": False},
            "live_report": {"status": "missing", "enabled": False},
            "error": error,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit(1)

    jobs_by_id = {j.get("id"): j for j in data.get("jobs", [])}

    cjob, cresolved, cmethod = find_by_id_or_name(
        jobs_by_id,
        "LLM_EMOTION_CONTINUOUS_CRON_ID",
        CONTINUOUS_ID_FALLBACK,
        CONTINUOUS_NAME_DEFAULT,
    )
    ljob, lresolved, lmethod = find_by_id_or_name(
        jobs_by_id,
        "LLM_EMOTION_LIVE_CRON_ID",
        LIVE_REPORT_ID_FALLBACK,
        LIVE_REPORT_NAME_DEFAULT,
    )

    out = {
        "continuous": pack(cjob, cresolved),
        "live_report": pack(ljob, lresolved),
        "_meta": {
            "resolved": {
                "continuous": cmethod,
                "live_report": lmethod,
            }
        }
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"continuous match: {cmethod} ({cresolved})")
    print(f"live_report match: {lmethod} ({lresolved})")


if __name__ == "__main__":
    main()
