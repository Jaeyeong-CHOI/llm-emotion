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

# 우선순위:
# 1) env로 지정한 cron ID
# 2) 이름 정확 일치
# 3) 이름 포함 매칭(유일할 때만)
# 4) 하드코딩 fallback은 운영 환경 변경 시 오탐을 유발하므로 미사용

CONTINUOUS_ID_FALLBACK = None
LIVE_REPORT_ID_FALLBACK = None

CRON_TARGETS = [
    (
        "continuous",
        "LLM_EMOTION_CONTINUOUS_CRON_ID",
        CONTINUOUS_ID_FALLBACK,
        CONTINUOUS_NAME_DEFAULT,
    ),
    (
        "live_report",
        "LLM_EMOTION_LIVE_CRON_ID",
        LIVE_REPORT_ID_FALLBACK,
        LIVE_REPORT_NAME_DEFAULT,
    ),
]


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
        matched = jobs.get(explicit_id)
        if matched:
            return matched, explicit_id, "env"
        # If env var is stale, fall back to name matching for better resilience.
        # This keeps the system running when IDs are rotated or manually edited.

    # primary by name
    for j in jobs.values():
        if (j.get("name") or "") == name_key:
            return j, j.get("id"), f"name:{name_key}"

    # substring fallback by contains
    contains_matches = [
        j
        for j in jobs.values()
        if name_key and name_key in (j.get("name") or "")
    ]
    if len(contains_matches) == 1:
        j = contains_matches[0]
        return j, j.get("id"), f"fuzzy:{name_key}"

    # final fallback: legacy ID 기반 복구 경로는 의도적으로 비활성화
    # 이름 기반 매칭만으로 안정적으로 복구되며, 잘못된 고정 ID를 피한다.
    if fallback_id:
        fallback = jobs.get(fallback_id)
        if fallback:
            return fallback, fallback_id, "fallback-id"
    return None, None, "fallback-id"



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


def resolve_target(jobs_by_id, target_name, env_var, fallback_id, name):
    job, resolved_id, method = find_by_id_or_name(
        jobs_by_id,
        env_var,
        fallback_id,
        name,
    )
    return target_name, pack(job, resolved_id), resolved_id, method


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

    out = {}
    resolved = {}

    for target_name, env_var, fallback_id, name in CRON_TARGETS:
        key, snapshot, resolved_id, method = resolve_target(
            jobs_by_id,
            target_name,
            env_var,
            fallback_id,
            name,
        )
        out[key] = snapshot
        resolved[key] = method

    out["_meta"] = {
        "resolved": resolved,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    for name, method in resolved.items():
        print(f"{name} match: {method} ({out[name].get('resolved_id')})")


if __name__ == "__main__":
    main()
