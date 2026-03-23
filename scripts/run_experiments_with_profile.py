#!/usr/bin/env python3
"""실험 러너 guardrail profile을 불러 run_experiments.py 실행을 단순화한다."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def to_cli(args: dict[str, object]) -> list[str]:
    cli: list[str] = []
    for key, value in args.items():
        flag = f"--{key.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                cli.append(flag)
            continue
        if value is None:
            continue
        if isinstance(value, list):
            for item in value:
                cli.extend([flag, str(item)])
            continue
        cli.extend([flag, str(value)])
    return cli


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="ops/runner_guardrail_profile.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("passthrough", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    profile_path = ROOT / args.profile
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    base_args = profile.get("run_experiments_args") or {}
    if not isinstance(base_args, dict):
        raise RuntimeError("run_experiments_args must be object")

    cmd = [sys.executable, "scripts/run_experiments.py", *to_cli(base_args)]
    if args.passthrough:
        extra = args.passthrough
        if extra and extra[0] == "--":
            extra = extra[1:]
        cmd.extend(extra)

    pretty = " ".join(shlex.quote(p) for p in cmd)
    print(f"[profile] {profile.get('name', 'unnamed')}")
    print(f"[cmd] {pretty}")
    if args.dry_run:
        return 0

    proc = subprocess.run(cmd, cwd=ROOT)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
