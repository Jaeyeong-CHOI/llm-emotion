#!/usr/bin/env python3
"""screening quality gate 결과를 읽어 우선순위 triage 계획을 생성한다."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from research_ops_common import read_json, write_json


@dataclass
class Gate:
    name: str
    status: str
    observed: object
    threshold: str


@dataclass
class Hotspot:
    key: str
    value: object


def load_report(path: Path) -> tuple[list[Gate], list[Hotspot]]:
    data = read_json(path, default={})
    if not isinstance(data, dict):
        data = {}

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
    raw_hotspots = data.get("hotspots") or {}
    hotspots: list[Hotspot] = []
    if isinstance(raw_hotspots, dict):
        hotspots = [Hotspot(key=str(k), value=v) for k, v in raw_hotspots.items()]
    elif isinstance(raw_hotspots, list):
        for idx, row in enumerate(raw_hotspots):
            if isinstance(row, dict) and "key" in row:
                hotspots.append(Hotspot(key=str(row.get("key")), value=row.get("value")))
            else:
                hotspots.append(Hotspot(key=f"hotspot_{idx}", value=row))
    return gates, hotspots


def priority_for(gate_name: str) -> tuple[int, str]:
    n = gate_name
    if "manual_qc_review_traceable_known_query_unknown_year" in n:
        return (1, "선행연구 스크리닝 품질")
    if "prompt_bank" in n or "scenario" in n:
        return (2, "프롬프트 뱅크 균형")
    if "temperature" in n or "planned_sample" in n or "timeout" in n:
        return (3, "실험 러너 안정성")
    return (4, "기타 품질 게이트")


def _to_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _parse_threshold(threshold: str) -> tuple[str, float | None]:
    text = (threshold or "").strip()
    if not text:
        return "", None
    for op in (">=", "<=", ">", "<", "="):
        if text.startswith(op):
            return op, _to_float(text[len(op) :].strip())
    return "", _to_float(text)


def severity_score(observed: object, threshold: str) -> float:
    op, target = _parse_threshold(threshold)
    obs = _to_float(observed)
    if target is None or obs is None:
        return 0.5
    if op in {">=", ">"}:
        gap = max(0.0, target - obs)
        return round(gap / max(abs(target), 1e-6), 4)
    if op in {"<=", "<"}:
        gap = max(0.0, obs - target)
        return round(gap / max(abs(target), 1e-6), 4)
    return 0.5


def top_hotspot_hint(hotspots: list[Hotspot], gate_name: str) -> str:
    n = gate_name
    if "unknown_year" in n:
        key = "review_unknown_year_queries"
    elif "duplicate_title" in n:
        key = "duplicate_title_examples"
    elif "screening_reason" in n:
        key = "top_screening_reasons"
    elif "risk_reason" in n:
        key = "top_qc_risk_reasons"
    else:
        key = ""

    if key:
        for hotspot in hotspots:
            if hotspot.key == key:
                value = hotspot.value
                if isinstance(value, list) and value:
                    return f"{key} 상위: {value[0]}"
                if isinstance(value, dict) and value:
                    first_key = next(iter(value))
                    return f"{key} 상위: {first_key}={value[first_key]}"
    return "핫스팟 근거를 확인해 수동 점검"


def build_actions(failed_gates: Iterable[Gate], hotspots: list[Hotspot]) -> list[dict]:
    out = []
    for gate in failed_gates:
        p_rank, p_label = priority_for(gate.name)
        sev = severity_score(gate.observed, gate.threshold)
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
                "severity_score": sev,
                "gate": gate.name,
                "observed": gate.observed,
                "threshold": gate.threshold,
                "hotspot_hint": top_hotspot_hint(hotspots, gate.name),
                "recommended_action": action,
            }
        )
    out.sort(key=lambda x: (x["priority_rank"], -x["severity_score"], x["gate"]))
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

    lines.append("| priority | severity | gate | observed | threshold | hotspot | action |")
    lines.append("|---|---:|---|---:|---|---|---|")
    for row in actions:
        lines.append(
            f"| {row['priority']} | {row['severity_score']} | `{row['gate']}` | `{row['observed']}` | `{row['threshold']}` | {row['hotspot_hint']} | {row['recommended_action']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_path", default="results/screening_quality_report.json")
    ap.add_argument("--out", dest="out_json", default="results/screening_triage_plan.json")
    ap.add_argument("--out-md", dest="out_md", default="results/screening_triage_plan.md")
    args = ap.parse_args()

    input_path = Path(args.input_path)
    gates, hotspots = load_report(input_path)
    failed = [g for g in gates if g.status.lower() not in {"pass", "ok"}]
    actions = build_actions(failed, hotspots)

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

    write_json(out_json, payload)
    out_md.write_text(render_markdown(actions), encoding="utf-8")
    print(f"[ok] wrote {out_json} and {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
