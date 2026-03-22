#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manual_qc_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def top_items(mapping: dict, limit: int = 8) -> list[dict]:
    ranked = sorted(mapping.items(), key=lambda x: (-int(x[1]), x[0]))
    return [{"name": key, "count": value} for key, value in ranked[:limit]]


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, payload: dict):
    lines = [
        f"# Screening Quality Check: {payload['run_label']}",
        "",
        f"- generated_at_utc: `{payload['generated_at_utc']}`",
        f"- report: `{payload['inputs']['report']}`",
        f"- audit: `{payload['inputs']['audit']}`",
        f"- manual_qc_csv: `{payload['inputs']['manual_qc_csv']}`",
        f"- status: `{payload['status']}`",
        f"- quality_score: `{payload['quality_score']}`",
        "",
        "## Gates",
    ]
    for gate in payload["gates"]:
        lines.append(
            f"- [{gate['status']}] {gate['name']}: observed=`{gate['observed']}` threshold=`{gate['threshold']}`"
        )
    lines.extend(
        [
            "",
            "## Summary",
            f"- deduped_records: `{payload['summary']['deduped_records']}`",
            f"- include_count: `{payload['summary']['include_count']}`",
            f"- review_count: `{payload['summary']['review_count']}`",
            f"- manual_qc_rows: `{payload['summary']['manual_qc_rows']}`",
            f"- single_source_share: `{payload['summary']['single_source_share']}`",
            f"- low_confidence_share: `{payload['summary']['low_confidence_share']}`",
            f"- query_drift_candidate_count: `{payload['summary']['query_drift_candidate_count']}`",
            "",
            "## Hotspots",
        ]
    )
    for item in payload["hotspots"]:
        lines.append(f"- {item['label']}: `{item['value']}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/lit_search_report.json")
    ap.add_argument("--audit", default="results/lit_screening_audit.json")
    ap.add_argument("--manual-qc-csv", default="results/manual_qc_queue.csv")
    ap.add_argument("--out", default="results/screening_quality_report.json")
    ap.add_argument("--out-md", default="results/screening_quality_report.md")
    ap.add_argument("--run-label", default="screening_quality_check")
    ap.add_argument("--min-deduped-records", type=int, default=200)
    ap.add_argument("--min-manual-qc-rows", type=int, default=20)
    ap.add_argument("--max-single-source-share", type=float, default=0.95)
    ap.add_argument("--max-low-confidence-share", type=float, default=0.9)
    ap.add_argument("--max-zero-hit-terms", type=int, default=6)
    ap.add_argument("--max-gate-failures-near-threshold", type=int, default=180)
    args = ap.parse_args()

    report_path = ROOT / args.report
    audit_path = ROOT / args.audit
    manual_qc_csv_path = ROOT / args.manual_qc_csv

    report = load_json(report_path)
    audit = load_json(audit_path)
    manual_qc_rows = load_manual_qc_csv(manual_qc_csv_path)

    labels = report.get("labels") or {}
    confidence = report.get("confidence") or {}
    triage_risk = report.get("triage_risk") or {}
    stability = report.get("screening_stability") or {}
    alias_coverage = report.get("alias_coverage") or {}
    risk_reason_summary = report.get("manual_qc_queue_risk_reason_summary") or {}
    balanced_summary = report.get("manual_qc_queue_balanced_summary") or {}
    drift_term_gaps = report.get("query_drift_term_gaps") or {}

    deduped_records = int(report.get("deduped_records", 0) or 0)
    low_confidence_count = int(confidence.get("low", 0) or 0)
    single_source_only = int(stability.get("single_source_only", 0) or 0)
    zero_hit_terms = len(alias_coverage.get("zero_hit_terms") or [])
    gate_failures_near_threshold = int(triage_risk.get("gate_failures_near_threshold", 0) or 0)
    query_drift_candidate_count = int(drift_term_gaps.get("candidate_count", 0) or 0)

    gates = [
        {
            "name": "deduped_records_floor",
            "status": "pass" if deduped_records >= args.min_deduped_records else "fail",
            "observed": deduped_records,
            "threshold": f">={args.min_deduped_records}",
        },
        {
            "name": "manual_qc_rows_floor",
            "status": "pass" if len(manual_qc_rows) >= args.min_manual_qc_rows else "fail",
            "observed": len(manual_qc_rows),
            "threshold": f">={args.min_manual_qc_rows}",
        },
        {
            "name": "single_source_share_ceiling",
            "status": "pass" if pct(single_source_only, deduped_records) <= args.max_single_source_share else "fail",
            "observed": pct(single_source_only, deduped_records),
            "threshold": f"<={args.max_single_source_share}",
        },
        {
            "name": "low_confidence_share_ceiling",
            "status": "pass" if pct(low_confidence_count, deduped_records) <= args.max_low_confidence_share else "fail",
            "observed": pct(low_confidence_count, deduped_records),
            "threshold": f"<={args.max_low_confidence_share}",
        },
        {
            "name": "zero_hit_terms_ceiling",
            "status": "pass" if zero_hit_terms <= args.max_zero_hit_terms else "fail",
            "observed": zero_hit_terms,
            "threshold": f"<={args.max_zero_hit_terms}",
        },
        {
            "name": "gate_failures_near_threshold_ceiling",
            "status": "pass"
            if gate_failures_near_threshold <= args.max_gate_failures_near_threshold
            else "fail",
            "observed": gate_failures_near_threshold,
            "threshold": f"<={args.max_gate_failures_near_threshold}",
        },
    ]

    fail_count = sum(1 for gate in gates if gate["status"] == "fail")
    quality_score = round(max(0.0, 100.0 - fail_count * 15.0 - zero_hit_terms * 1.5), 2)
    status = "pass" if fail_count == 0 else "review"

    hotspots = [
        {"label": "top_qc_risk_reasons", "value": top_items(risk_reason_summary, limit=5)},
        {"label": "balanced_qc_by_label", "value": balanced_summary.get("by_label") or {}},
        {"label": "balanced_qc_by_confidence", "value": balanced_summary.get("by_confidence") or {}},
        {"label": "top_borderline_review_risk", "value": top_items(triage_risk, limit=4)},
        {"label": "query_drift_term_suggestions", "value": (drift_term_gaps.get("term_suggestions") or [])[:8]},
        {"label": "zero_hit_terms", "value": (alias_coverage.get("zero_hit_terms") or [])[:8]},
    ]

    payload = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "run_label": args.run_label,
        "status": status,
        "quality_score": quality_score,
        "inputs": {
            "report": args.report,
            "audit": args.audit,
            "manual_qc_csv": args.manual_qc_csv,
        },
        "summary": {
            "deduped_records": deduped_records,
            "include_count": int(labels.get("include", 0) or 0),
            "review_count": int(labels.get("review", 0) or 0),
            "exclude_count": int(labels.get("exclude", 0) or 0),
            "manual_qc_rows": len(manual_qc_rows),
            "single_source_only": single_source_only,
            "single_source_share": pct(single_source_only, deduped_records),
            "low_confidence_count": low_confidence_count,
            "low_confidence_share": pct(low_confidence_count, deduped_records),
            "zero_hit_terms": zero_hit_terms,
            "gate_failures_near_threshold": gate_failures_near_threshold,
            "query_drift_candidate_count": query_drift_candidate_count,
            "audit_counts": audit.get("counts") or {},
        },
        "gates": gates,
        "hotspots": hotspots,
    }

    write_json(ROOT / args.out, payload)
    write_markdown(ROOT / args.out_md, payload)
    print(f"[OK] screening quality report -> {ROOT / args.out}")
    print(f"status={status} quality_score={quality_score} fail_count={fail_count}")


if __name__ == "__main__":
    main()
