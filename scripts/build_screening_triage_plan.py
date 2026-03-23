#!/usr/bin/env python3
"""screening quality gate 결과를 읽어 우선순위 triage 계획을 생성한다."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class Gate:
    name: str
    status: str
    observed: object
    threshold: str


def load_gates(path: Path) -> list[Gate]:
    data = json.loads(path.read_text(encoding="utf-8"))
    gates = []
    for row in data.get("gates", []):
        gates.append(
            Gate(
                name=str(row.get("name", "")),
                status=str(row.get("status", "unknown")),
                observed=row.get("observed"),
                threshold=str(row.get("threshold", "")),
            )
        )
    return gates


def priority_for(gate_name: str) -> tuple[int, str]:
    n = gate_name
    if "manual_qc_review_traceable_known_query_unknown_year" in n:
        return (1, "선행연구 스크리닝 품질")
    if "prompt_bank" in n or "scenario" in n:
        return (2, "프롬프트 뱅크 균형")
    if "temperature" in n or "planned_sample" in n or "timeout" in n:
        return (3, "실험 러너 안정성")
    return (4, "기타 품질 게이트")


def build_actions(failed_gates: Iterable[Gate]) -> list[dict]:
    out = []
    for gate in failed_gates:
        p_rank, p_label = priority_for(gate.name)
        if p_rank == 1:
            action = "manual_qc_queue.csv 재샘플링 + unknown-year provenance backfill"
        elif p_rank == 2:
            action = "countervoice/tail 시나리오 보강 후 prompt bank 회귀 점검"
        elif p_rank == 3:
            action = "preflight guardrail 강화 후 run-id 분할 재실행"
        else:
            action = "게이트 정의 재검토 및 임계치 근거 문서화"
        out.append(
            {
                "priority_rank": p_rank,
                "priority": p_label,
                "gate": gate.name,
                "observed": gate.observed,
                "threshold": gate.threshold,
                "recommended_action": action,
            }
        )
    out.sort(key=lambda x: (x["priority_rank"], x["gate"]))
    return out


def render_markdown(actions: list[dict]) -> str:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Screening Quality Triage Plan",
        "",
        f"- generated_at_utc: `{ts}`",
        f"- actionable_items: `{len(actions)}`",
        "",
    ]
    if not actions:
        lines.append("모든 gate가 통과해 triage 액션이 필요하지 않습니다.")
        return "\n".join(lines) + "\n"

    lines.append("| priority | gate | observed | threshold | action |")
    lines.append("|---|---|---:|---|---|")
    for row in actions:
        lines.append(
            f"| {row['priority']} | `{row['gate']}` | `{row['observed']}` | `{row['threshold']}` | {row['recommended_action']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_path", default="results/screening_quality_report.json")
    ap.add_argument("--out", dest="out_json", default="results/screening_triage_plan.json")
    ap.add_argument("--out-md", dest="out_md", default="results/screening_triage_plan.md")
    args = ap.parse_args()

    input_path = Path(args.input_path)
    gates = load_gates(input_path)
    failed = [g for g in gates if g.status.lower() not in {"pass", "ok"}]
    actions = build_actions(failed)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input": str(input_path),
        "failed_gate_count": len(failed),
        "actions": actions,
    }

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(actions), encoding="utf-8")
    print(f"[ok] wrote {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
