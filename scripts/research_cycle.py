#!/usr/bin/env python3
import json
import subprocess
from collections.abc import Sequence

from research_ops_common import (
    ROOT,
    append_note,
    count_lines,
    load_research_state,
    now_isoseconds,
    save_research_state,
)


def run(cmd: Sequence[str]):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def run_screening_triage_plan_step() -> tuple[int, str, str]:
    report_path = ROOT / "results" / "screening_quality_report.json"
    if not report_path.exists():
        return 0, "[skip] screening_quality_report.json not found\n", ""
    return run(
        [
            "python3",
            "scripts/build_screening_triage_plan.py",
            "--in",
            "results/screening_quality_report.json",
            "--out",
            "results/screening_triage_plan.json",
            "--out-md",
            "results/screening_triage_plan.md",
        ]
    )


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
    now = now_isoseconds()
    state["last_run"] = now

    steps = [
        (
            "literature_search",
            [
                "python3",
                "scripts/search_openalex.py",
                "--config",
                "queries/search_queries.json",
                "--screening-rules",
                "queries/screening_rules.json",
                "--out",
                "refs/openalex_results.jsonl",
            ],
        ),
        (
            "evidence_table",
            [
                "python3",
                "scripts/build_evidence_table.py",
                "--in",
                "refs/openalex_results.jsonl",
                "--out",
                "docs/evidence-table.md",
            ],
        ),
        ("mock_generate", ["python3", "scripts/generate_dataset.py", "--out", "data/raw/mock_generations.jsonl", "--n", "10", "--seed", "42", "--prompt-bank", "prompts/prompt_bank_ko.json"]),
        (
            "mock_analyze",
            [
                "python3",
                "scripts/analyze_regret_markers.py",
                "--in",
                "data/raw/mock_generations.jsonl",
                "--out",
                "results/mock_metrics.json",
            ],
        ),
        ("snapshot_cron_status", ["python3", "scripts/snapshot_cron_status.py"]),
        ("update_live_status", ["python3", "scripts/update_live_status.py"]),
        ("append_brief_log", ["python3", "scripts/update_brief_log.py"]),
    ]

    for name, cmd in steps:
        code, out, err = run(cmd)
        if code != 0:
            state["last_error"] = {"step": name, "code": code, "stderr": err[-1500:]}
            append_note(state, f"FAILED {name}: code={code}")
            save_research_state(state)
            print(f"[FAIL] {name}\n{err}")
            return 1
        append_note(state, f"OK {name}")

    triage_code, triage_out, triage_err = run_screening_triage_plan_step()
    if triage_code != 0:
        state["last_error"] = {
            "step": "screening_triage_plan",
            "code": triage_code,
            "stderr": triage_err[-1500:],
        }
        append_note(state, f"FAILED screening_triage_plan: code={triage_code}")
        save_research_state(state)
        print(f"[FAIL] screening_triage_plan\n{triage_err}")
        return 1
    append_note(state, "OK screening_triage_plan" if triage_out.strip() == "" else triage_out.strip())

    state["last_success"] = now
    state["last_error"] = None
    state.setdefault("stats", {})["papers_collected"] = count_lines(ROOT / "refs" / "openalex_results.jsonl")
    state["stats"]["evidence_rows"] = max(0, count_lines(ROOT / "docs" / "evidence-table.md") - 4)
    state["stats"]["mock_samples_generated"] = count_lines(ROOT / "data" / "raw" / "mock_generations.jsonl")

    refs_path = ROOT / "refs" / "openalex_results.jsonl"
    include_n, review_n, malformed_rows = collect_screening_label_stats(refs_path)
    state["stats"]["screen_include"] = include_n
    state["stats"]["screen_review"] = review_n
    if malformed_rows:
        append_note(state, f"WARN screening parse skipped malformed_rows={malformed_rows}")

    save_research_state(state)
    print("[OK] research cycle complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
