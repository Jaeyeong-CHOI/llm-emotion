#!/usr/bin/env python3
import json
import subprocess
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "ops" / "research_state.json"


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def append_note(state, text):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    state.setdefault("notes", []).append(f"[{ts}] {text}")
    state["notes"] = state["notes"][-30:]


def main():
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    now = datetime.datetime.now().isoformat(timespec="seconds")
    state["last_run"] = now

    steps = [
        ("literature_search", "python3 scripts/search_openalex.py --config queries/search_queries.json --out refs/openalex_results.jsonl"),
        ("evidence_table", "python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md"),
        ("mock_generate", "python3 scripts/generate_dataset.py --out data/raw/mock_generations.jsonl --n 10"),
        ("mock_analyze", "python3 scripts/analyze_regret_markers.py --in data/raw/mock_generations.jsonl --out results/mock_metrics.json"),
    ]

    for name, cmd in steps:
        code, out, err = run(cmd)
        if code != 0:
            state["last_error"] = {"step": name, "code": code, "stderr": err[-1500:]}
            append_note(state, f"FAILED {name}: code={code}")
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[FAIL] {name}\n{err}")
            return 1
        append_note(state, f"OK {name}")

    state["last_success"] = now
    state["last_error"] = None
    state.setdefault("stats", {})["papers_collected"] = count_lines(ROOT / "refs" / "openalex_results.jsonl")
    state["stats"]["evidence_rows"] = max(0, count_lines(ROOT / "docs" / "evidence-table.md") - 4)
    state["stats"]["mock_samples_generated"] = count_lines(ROOT / "data" / "raw" / "mock_generations.jsonl")

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] research cycle complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
