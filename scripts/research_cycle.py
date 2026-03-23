#!/usr/bin/env python3
import json
import os
import subprocess
from collections.abc import Sequence

from research_ops_common import (
    ROOT,
    append_note,
    count_lines,
    load_research_state,
    now_iso_seconds,
    save_research_state,
)

PYTHON_CMD = "python3"
DEFAULT_STEP_TIMEOUT_SECONDS = int(os.environ.get("LLM_EMOTION_STEP_TIMEOUT_SECONDS", "900"))


def run(cmd: Sequence[str], timeout_seconds: int = DEFAULT_STEP_TIMEOUT_SECONDS):
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    return p.returncode, p.stdout, p.stderr


def _py(step_name: str, *args: str) -> list[str]:
    """Build a python command list with a stable interpreter prefix."""

    return [PYTHON_CMD, step_name, *args]


def run_step(state: dict, name: str, cmd: Sequence[str]):
    try:
        code, out, err = run(cmd)
    except subprocess.TimeoutExpired as exc:
        state["last_error"] = {
            "step": name,
            "code": 124,
            "stderr": f"timeout after {exc.timeout}s",
        }
        append_note(state, f"FAILED {name}: timeout after {exc.timeout}s")
        save_research_state(state)
        print(f"[FAIL] {name} timeout after {exc.timeout}s")
        return 124, "", f"timeout after {exc.timeout}s"

    if code != 0:
        state["last_error"] = {
            "step": name,
            "code": code,
            "stderr": err[-1500:],
        }
        append_note(state, f"FAILED {name}: code={code}")
        save_research_state(state)
        print(f"[FAIL] {name}\n{err}")
        return code, out, err

    append_note(state, f"OK {name}")
    return code, out, err


def run_steps(state: dict, steps: list[tuple[str, list[str]]]) -> bool:
    """Run all requested steps in order; return False on first failure."""

    for name, cmd in steps:
        code, _, _ = run_step(state, name, cmd)
        if code != 0:
            return False

    return True


def collect_screening_label_stats(refs_path):
    include_n = 0
    review_n = 0
    malformed_rows = 0

    if not refs_path.exists():
        return include_n, review_n, malformed_rows

    with refs_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                malformed_rows += 1
                continue
            if row.get("screening_label") == "include":
                include_n += 1
            elif row.get("screening_label") == "review":
                review_n += 1

    return include_n, review_n, malformed_rows


def main():
    state = load_research_state()
    now = now_iso_seconds()
    state["last_run"] = now

    steps = [
        (
            "literature_search",
            _py(
                "scripts/search_openalex.py",
                "--config",
                "queries/search_queries.json",
                "--screening-rules",
                "queries/screening_rules.json",
                "--out",
                "refs/openalex_results.jsonl",
            ),
        ),
        (
            "evidence_table",
            _py(
                "scripts/build_evidence_table.py",
                "--in",
                "refs/openalex_results.jsonl",
                "--out",
                "docs/evidence-table.md",
            ),
        ),
        (
            "mock_generate",
            _py(
                "scripts/generate_dataset.py",
                "--out",
                "data/raw/mock_generations.jsonl",
                "--n",
                "10",
                "--seed",
                "42",
                "--prompt-bank",
                "prompts/prompt_bank_ko.json",
            ),
        ),
        (
            "mock_analyze",
            _py(
                "scripts/analyze_regret_markers.py",
                "--in",
                "data/raw/mock_generations.jsonl",
                "--out",
                "results/mock_metrics.json",
            ),
        ),
        ("snapshot_cron_status", _py("scripts/snapshot_cron_status.py")),
        ("update_live_status", _py("scripts/update_live_status.py")),
        ("append_brief_log", _py("scripts/update_brief_log.py")),
    ]

    if not run_steps(state, steps):
        return 1

    report_path = ROOT / "results" / "screening_quality_report.json"
    if not report_path.exists():
        append_note(state, "OK screening_triage_plan: [skip] screening_quality_report.json not found")
    else:
        triage_code, triage_out, _ = run_step(
            state,
            "screening_triage_plan",
            _py(
                "scripts/build_screening_triage_plan.py",
                "--in",
                "results/screening_quality_report.json",
                "--out",
                "results/screening_triage_plan.json",
                "--out-md",
                "results/screening_triage_plan.md",
            ),
        )
        if triage_code != 0:
            return 1

        # Preserve previous custom success note behavior.
        append_note(
            state,
            "OK screening_triage_plan" if triage_out.strip() == "" else triage_out.strip(),
        )

    state["last_success"] = now
    state["last_error"] = None
    stats = state.setdefault("stats", {})
    stats["papers_collected"] = count_lines(ROOT / "refs" / "openalex_results.jsonl")
    stats["evidence_rows"] = max(0, count_lines(ROOT / "docs" / "evidence-table.md") - 4)
    stats["mock_samples_generated"] = count_lines(ROOT / "data" / "raw" / "mock_generations.jsonl")

    refs_path = ROOT / "refs" / "openalex_results.jsonl"
    include_n, review_n, malformed_rows = collect_screening_label_stats(refs_path)
    stats["screen_include"] = include_n
    stats["screen_review"] = review_n
    if malformed_rows:
        append_note(state, f"WARN screening parse skipped malformed_rows={malformed_rows}")

    save_research_state(state)
    print("[OK] research cycle complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
