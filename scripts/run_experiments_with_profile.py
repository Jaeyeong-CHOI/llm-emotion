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


def _append_profile_arg(cli: list[str], flag: str, value: object, raw_key: str) -> None:
    """Append profile-derived args to a CLI token list.

    Supported shapes:
    - bool: emit flag when True
    - list/tuple: flatten preserving order
    - scalar str/int/float/Path: emit as "--key value"
    """

    if isinstance(value, bool):
        if value:
            cli.append(flag)
        return

    if value is None:
        return

    if isinstance(value, (list, tuple)):
        for item in value:
            _append_profile_arg(cli, flag, item, raw_key)
        return

    if isinstance(value, (str, int, float, Path)):
        cli.extend([flag, str(value)])
        return

    raise TypeError(f"Unsupported profile arg type for --{raw_key}: {type(value).__name__}")


def _resolve_profile_path(raw_path: str) -> Path:
    profile_path = (ROOT / raw_path).resolve()

    if not str(profile_path).endswith(".json"):
        raise ValueError(f"Profile must be a .json file: {raw_path}")

    ops_root = (ROOT / "ops").resolve()
    if not profile_path.is_relative_to(ops_root):
        raise ValueError(
            f"Profile path must stay under repository ops directory: {raw_path}"
        )

    current = profile_path
    while True:
        if current.is_symlink():
            raise ValueError(f"Profile path is symlink unsafe: {current}")
        if current == current.parent:
            break
        current = current.parent

    if not profile_path.exists():
        raise FileNotFoundError(f"profile not found: {profile_path}")

    return profile_path


def to_cli(args: dict[str, object]) -> list[str]:
    cli: list[str] = []
    for key, value in args.items():
        flag = f"--{key.replace('_', '-')}"
        _append_profile_arg(cli, flag, value, key)
    return cli


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="ops/runner_guardrail_profile.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("passthrough", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    try:
        profile_path = _resolve_profile_path(args.profile)
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except (ValueError, FileNotFoundError) as exc:
        raise RuntimeError(str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid profile JSON: {profile_path}") from exc
    if not isinstance(profile, dict):
        raise RuntimeError("profile root must be object")

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
