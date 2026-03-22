#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import json
import math
import re
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


def is_truthy(value) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def normalize_title(value) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", str(value or "").strip().lower())).strip()


def top_items(mapping: dict, limit: int = 8) -> list[dict]:
    ranked = sorted(mapping.items(), key=lambda x: (-int(x[1]), x[0]))
    return [{"name": key, "count": value} for key, value in ranked[:limit]]


def normalized_entropy(mapping: dict[str, int]) -> float:
    counts = [int(v or 0) for v in mapping.values() if int(v or 0) > 0]
    if not counts:
        return 0.0
    total = sum(counts)
    if total <= 0:
        return 0.0
    probs = [c / total for c in counts]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
    return round(entropy / max_entropy, 4) if max_entropy > 0 else 0.0


def normalized_hhi(mapping: dict[str, int]) -> float:
    counts = [int(v or 0) for v in mapping.values() if int(v or 0) > 0]
    if not counts:
        return 0.0
    total = sum(counts)
    if total <= 0:
        return 0.0
    probs = [c / total for c in counts]
    return round(sum(p * p for p in probs), 4)


def effective_query_count(mapping: dict[str, int]) -> float:
    counts = [int(v or 0) for v in mapping.values() if int(v or 0) > 0]
    if not counts:
        return 0.0
    total = sum(counts)
    if total <= 0:
        return 0.0
    probs = [c / total for c in counts]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    return round(2 ** entropy, 4)


def js_divergence(lhs: dict[str, int], rhs: dict[str, int]) -> float:
    keys = {k for k, v in lhs.items() if int(v or 0) > 0} | {k for k, v in rhs.items() if int(v or 0) > 0}
    if not keys:
        return 0.0
    lhs_total = sum(int(lhs.get(k, 0) or 0) for k in keys)
    rhs_total = sum(int(rhs.get(k, 0) or 0) for k in keys)
    if lhs_total <= 0 or rhs_total <= 0:
        return 0.0

    def _kl(a: dict[str, float], b: dict[str, float]) -> float:
        return sum(pa * math.log2(pa / max(pb, 1e-12)) for k, pa in a.items() if pa > 0 for pb in [b.get(k, 1e-12)])

    p = {k: int(lhs.get(k, 0) or 0) / lhs_total for k in keys}
    q = {k: int(rhs.get(k, 0) or 0) / rhs_total for k in keys}
    m = {k: 0.5 * (p[k] + q[k]) for k in keys}
    return round(0.5 * _kl(p, m) + 0.5 * _kl(q, m), 4)


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
            f"- balanced_label_bins: `{payload['summary']['balanced_label_bins']}`",
            f"- balanced_confidence_bins: `{payload['summary']['balanced_confidence_bins']}`",
            f"- balanced_group_bins: `{payload['summary']['balanced_group_bins']}`",
            f"- balanced_label_dominance: `{payload['summary']['balanced_label_dominance']}`",
            f"- balanced_include_rows: `{payload['summary']['balanced_include_rows']}`",
            f"- balanced_review_rows: `{payload['summary']['balanced_review_rows']}`",
            f"- balanced_min_per_label_target: `{payload['summary']['balanced_min_per_label_target']}`",
            f"- balanced_min_per_label_missing: `{payload['summary']['balanced_min_per_label_missing']}`",
            f"- risk_reason_diversity: `{payload['summary']['risk_reason_diversity']}`",
            f"- top_risk_reason_share: `{payload['summary']['top_risk_reason_share']}`",
            f"- screening_reason_diversity: `{payload['summary']['screening_reason_diversity']}`",
            f"- top_screening_reason_share: `{payload['summary']['top_screening_reason_share']}`",
            f"- screening_reason_entropy: `{payload['summary']['screening_reason_entropy']}`",
            f"- manual_qc_query_entropy: `{payload['summary']['manual_qc_query_entropy']}`",
            f"- manual_qc_review_query_entropy: `{payload['summary']['manual_qc_review_query_entropy']}`",
            f"- manual_qc_review_traceable_known_query_rows: `{payload['summary']['manual_qc_review_traceable_known_query_rows']}`",
            f"- manual_qc_review_traceable_known_query_share: `{payload['summary']['manual_qc_review_traceable_known_query_share']}`",
            f"- manual_qc_review_traceable_unknown_query_rows: `{payload['summary']['manual_qc_review_traceable_unknown_query_rows']}`",
            f"- manual_qc_review_traceable_unknown_query_share: `{payload['summary']['manual_qc_review_traceable_unknown_query_share']}`",
            f"- manual_qc_review_query_traceability_share: `{payload['summary']['manual_qc_review_query_traceability_share']}`",
            f"- manual_qc_review_traceable_known_query_entropy: `{payload['summary']['manual_qc_review_traceable_known_query_entropy']}`",
            f"- manual_qc_review_traceable_known_query_coverage: `{payload['summary']['manual_qc_review_traceable_known_query_coverage']}`",
            f"- manual_qc_review_traceable_known_query_hhi: `{payload['summary']['manual_qc_review_traceable_known_query_hhi']}`",
            f"- manual_qc_review_traceable_known_query_top_share: `{payload['summary']['manual_qc_review_traceable_known_query_top_share']}`",
            f"- manual_qc_review_traceable_known_query_top2_share: `{payload['summary']['manual_qc_review_traceable_known_query_top2_share']}`",
            f"- manual_qc_review_traceable_known_query_top3_share: `{payload['summary']['manual_qc_review_traceable_known_query_top3_share']}`",
            f"- manual_qc_review_traceable_known_query_js_divergence: `{payload['summary']['manual_qc_review_traceable_known_query_js_divergence']}`",
            f"- manual_qc_review_traceable_known_query_tail_share: `{payload['summary']['manual_qc_review_traceable_known_query_tail_share']}`",
            f"- manual_qc_review_traceable_known_query_effective_count: `{payload['summary']['manual_qc_review_traceable_known_query_effective_count']}`",
            f"- manual_qc_review_traceable_known_query_bottom_share: `{payload['summary']['manual_qc_review_traceable_known_query_bottom_share']}`",
            f"- manual_qc_review_traceable_known_query_bottom2_share: `{payload['summary']['manual_qc_review_traceable_known_query_bottom2_share']}`",
            f"- manual_qc_review_traceable_known_query_top_bottom_gap: `{payload['summary']['manual_qc_review_traceable_known_query_top_bottom_gap']}`",
            f"- manual_qc_review_traceable_known_query_group_entropy: `{payload['summary']['manual_qc_review_traceable_known_query_group_entropy']}`",
            f"- manual_qc_review_traceable_known_query_group_coverage: `{payload['summary']['manual_qc_review_traceable_known_query_group_coverage']}`",
            f"- manual_qc_review_traceable_known_query_group_top_share: `{payload['summary']['manual_qc_review_traceable_known_query_group_top_share']}`",
            f"- manual_qc_review_traceable_known_query_group_top2_share: `{payload['summary']['manual_qc_review_traceable_known_query_group_top2_share']}`",
            f"- manual_qc_review_traceable_known_query_group_tail_share: `{payload['summary']['manual_qc_review_traceable_known_query_group_tail_share']}`",
            f"- manual_qc_review_traceable_known_query_group_js_divergence: `{payload['summary']['manual_qc_review_traceable_known_query_group_js_divergence']}`",
            f"- manual_qc_review_traceable_known_query_unknown_group_share: `{payload['summary']['manual_qc_review_traceable_known_query_unknown_group_share']}`",
            f"- manual_qc_review_traceable_known_query_year_js_divergence: `{payload['summary']['manual_qc_review_traceable_known_query_year_js_divergence']}`",
            f"- manual_qc_risk_reason_entropy: `{payload['summary']['manual_qc_risk_reason_entropy']}`",
            f"- manual_qc_review_reason_entropy: `{payload['summary']['manual_qc_review_reason_entropy']}`",
            f"- review_to_include_ratio: `{payload['summary']['review_to_include_ratio']}`",
            f"- manual_qc_include_rows: `{payload['summary']['manual_qc_include_rows']}`",
            f"- manual_qc_review_rows: `{payload['summary']['manual_qc_review_rows']}`",
            f"- manual_qc_review_share: `{payload['summary']['manual_qc_review_share']}`",
            f"- manual_qc_review_confidence_bins: `{payload['summary']['manual_qc_review_confidence_bins']}`",
            f"- manual_qc_review_confidence_entropy: `{payload['summary']['manual_qc_review_confidence_entropy']}`",
            f"- traceable_reason_rows: `{payload['summary']['traceable_reason_rows']}`",
            f"- screening_reason_traceability_share: `{payload['summary']['screening_reason_traceability_share']}`",
            f"- include_traceable_reason_rows: `{payload['summary']['include_traceable_reason_rows']}`",
            f"- include_reason_traceability_share: `{payload['summary']['include_reason_traceability_share']}`",
            f"- review_traceable_reason_rows: `{payload['summary']['review_traceable_reason_rows']}`",
            f"- review_reason_traceability_share: `{payload['summary']['review_reason_traceability_share']}`",
            f"- include_bridge_signal_rows: `{payload['summary']['include_bridge_signal_rows']}`",
            f"- include_bridge_signal_share: `{payload['summary']['include_bridge_signal_share']}`",
            f"- review_bridge_signal_rows: `{payload['summary']['review_bridge_signal_rows']}`",
            f"- review_bridge_signal_share: `{payload['summary']['review_bridge_signal_share']}`",
            f"- review_bridge_traceable_rows: `{payload['summary']['review_bridge_traceable_rows']}`",
            f"- review_bridge_traceability_share: `{payload['summary']['review_bridge_traceability_share']}`",
            f"- review_bridge_traceability_given_bridge_share: `{payload['summary']['review_bridge_traceability_given_bridge_share']}`",
            f"- review_bridge_traceable_known_query_rows: `{payload['summary']['review_bridge_traceable_known_query_rows']}`",
            f"- review_bridge_traceable_known_query_share: `{payload['summary']['review_bridge_traceable_known_query_share']}`",
            f"- review_bridge_traceable_unknown_query_rows: `{payload['summary']['review_bridge_traceable_unknown_query_rows']}`",
            f"- review_bridge_traceable_unknown_query_share: `{payload['summary']['review_bridge_traceable_unknown_query_share']}`",
            f"- review_counterexample_rows: `{payload['summary']['review_counterexample_rows']}`",
            f"- review_counterexample_share: `{payload['summary']['review_counterexample_share']}`",
            f"- review_counterexample_traceable_rows: `{payload['summary']['review_counterexample_traceable_rows']}`",
            f"- review_counterexample_traceability_share: `{payload['summary']['review_counterexample_traceability_share']}`",
            f"- review_bridge_counterexample_coupled_rows: `{payload['summary']['review_bridge_counterexample_coupled_rows']}`",
            f"- review_bridge_counterexample_coupled_share: `{payload['summary']['review_bridge_counterexample_coupled_share']}`",
            f"- review_bridge_counterexample_traceable_coupled_rows: `{payload['summary']['review_bridge_counterexample_traceable_coupled_rows']}`",
            f"- review_bridge_counterexample_traceable_coupled_share: `{payload['summary']['review_bridge_counterexample_traceable_coupled_share']}`",
            f"- review_bridge_counterexample_traceability_given_coupled_share: `{payload['summary']['review_bridge_counterexample_traceability_given_coupled_share']}`",
            f"- review_bridge_counterexample_traceability_gap_share: `{payload['summary']['review_bridge_counterexample_traceability_gap_share']}`",
            f"- review_counterexample_without_bridge_rows: `{payload['summary']['review_counterexample_without_bridge_rows']}`",
            f"- review_counterexample_without_bridge_share: `{payload['summary']['review_counterexample_without_bridge_share']}`",
            f"- review_evidence_link_decay_rows: `{payload['summary']['review_evidence_link_decay_rows']}`",
            f"- review_evidence_link_decay_share: `{payload['summary']['review_evidence_link_decay_share']}`",
            f"- manual_qc_bridge_signal_rows: `{payload['summary']['manual_qc_bridge_signal_rows']}`",
            f"- manual_qc_bridge_signal_share: `{payload['summary']['manual_qc_bridge_signal_share']}`",
            f"- manual_qc_label_counts: `{payload['summary']['manual_qc_label_counts']}`",
            f"- manual_qc_source_group_diversity: `{payload['summary']['manual_qc_source_group_diversity']}`",
            f"- manual_qc_single_query_share: `{payload['summary']['manual_qc_single_query_share']}`",
            f"- manual_qc_unknown_query_share: `{payload['summary']['manual_qc_unknown_query_share']}`",
            f"- manual_qc_review_source_group_diversity: `{payload['summary']['manual_qc_review_source_group_diversity']}`",
            f"- manual_qc_review_group_dominance: `{payload['summary']['manual_qc_review_group_dominance']}`",
            f"- manual_qc_year_diversity: `{payload['summary']['manual_qc_year_diversity']}`",
            f"- manual_qc_single_year_share: `{payload['summary']['manual_qc_single_year_share']}`",
            f"- manual_qc_year_entropy: `{payload['summary']['manual_qc_year_entropy']}`",
            f"- manual_qc_dedup_label_conflict_rows: `{payload['summary']['manual_qc_dedup_label_conflict_rows']}`",
            f"- manual_qc_dedup_label_conflict_share: `{payload['summary']['manual_qc_dedup_label_conflict_share']}`",
            f"- manual_qc_dedup_score_range_alert_rows: `{payload['summary']['manual_qc_dedup_score_range_alert_rows']}`",
            f"- manual_qc_dedup_score_range_alert_share: `{payload['summary']['manual_qc_dedup_score_range_alert_share']}`",
            f"- manual_qc_duplicate_title_rows: `{payload['summary']['manual_qc_duplicate_title_rows']}`",
            f"- manual_qc_duplicate_title_share: `{payload['summary']['manual_qc_duplicate_title_share']}`",
            f"- empty_screening_reason_share: `{payload['summary']['empty_screening_reason_share']}`",
            f"- manual_qc_label_dominance: `{payload['summary']['manual_qc_label_dominance']}`",
            f"- manual_qc_high_risk_rows: `{payload['summary']['manual_qc_high_risk_rows']}`",
            f"- manual_qc_high_risk_share: `{payload['summary']['manual_qc_high_risk_share']}`",
            f"- review_weak_evidence_rows: `{payload['summary']['review_weak_evidence_rows']}`",
            f"- review_weak_evidence_share: `{payload['summary']['review_weak_evidence_share']}`",
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
    ap.add_argument("--min-balanced-label-bins", type=int, default=2)
    ap.add_argument("--min-balanced-confidence-bins", type=int, default=3)
    ap.add_argument("--min-balanced-group-bins", type=int, default=3)
    ap.add_argument("--max-balanced-label-dominance", type=float, default=0.8)
    ap.add_argument("--min-balanced-include-rows", type=int, default=2)
    ap.add_argument("--min-balanced-review-rows", type=int, default=6)
    ap.add_argument("--min-balanced-min-per-label", type=int, default=2)
    ap.add_argument("--max-query-drift-candidates", type=int, default=30)
    ap.add_argument("--min-risk-reason-diversity", type=int, default=5)
    ap.add_argument("--max-top-risk-reason-share", type=float, default=0.55)
    ap.add_argument("--max-review-to-include-ratio", type=float, default=5.0)
    ap.add_argument("--max-manual-qc-high-risk-share", type=float, default=0.85)
    ap.add_argument("--min-manual-qc-include-rows", type=int, default=2)
    ap.add_argument("--max-manual-qc-label-dominance", type=float, default=0.75)
    ap.add_argument("--min-manual-qc-review-share", type=float, default=0.25)
    ap.add_argument("--max-manual-qc-review-share", type=float, default=0.85)
    ap.add_argument("--min-screening-reason-diversity", type=int, default=6)
    ap.add_argument("--max-top-screening-reason-share", type=float, default=0.65)
    ap.add_argument("--min-manual-qc-source-groups", type=int, default=3)
    ap.add_argument("--max-manual-qc-single-query-share", type=float, default=0.45)
    ap.add_argument("--max-empty-screening-reason-share", type=float, default=0.1)
    ap.add_argument("--min-screening-reason-entropy", type=float, default=0.55)
    ap.add_argument("--min-manual-qc-query-entropy", type=float, default=0.5)
    ap.add_argument("--min-manual-qc-review-query-entropy", type=float, default=0.45)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-share", type=float, default=0.55)
    ap.add_argument("--max-manual-qc-review-traceable-unknown-query-share", type=float, default=0.15)
    ap.add_argument("--min-manual-qc-review-query-traceability-share", type=float, default=0.75)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-entropy", type=float, default=0.45)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-coverage", type=int, default=3)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-hhi", type=float, default=0.35)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-top-share", type=float, default=0.7)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-top2-share", type=float, default=0.9)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-top3-share", type=float, default=0.95)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-js-divergence", type=float, default=0.35)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-tail-share", type=float, default=0.15)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-bottom2-share", type=float, default=0.08)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-effective-count", type=float, default=3.0)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-top-bottom-gap", type=float, default=0.55)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-group-entropy", type=float, default=0.45)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-group-coverage", type=int, default=2)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-group-top-share", type=float, default=0.75)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-group-top2-share", type=float, default=0.9)
    ap.add_argument("--min-manual-qc-review-traceable-known-query-group-tail-share", type=float, default=0.1)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-group-js-divergence", type=float, default=0.35)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-unknown-group-share", type=float, default=0.2)
    ap.add_argument("--max-manual-qc-review-traceable-known-query-year-js-divergence", type=float, default=0.25)
    ap.add_argument("--min-review-bridge-traceable-known-query-share", type=float, default=0.6)
    ap.add_argument("--max-review-bridge-traceable-unknown-query-share", type=float, default=0.2)
    ap.add_argument("--min-manual-qc-risk-reason-entropy", type=float, default=0.45)
    ap.add_argument("--min-manual-qc-review-reason-entropy", type=float, default=0.35)
    ap.add_argument("--min-manual-qc-review-confidence-bins", type=int, default=2)
    ap.add_argument("--min-manual-qc-review-confidence-entropy", type=float, default=0.4)
    ap.add_argument("--min-screening-reason-traceability-share", type=float, default=0.6)
    ap.add_argument("--min-include-reason-traceability-share", type=float, default=0.7)
    ap.add_argument("--min-review-reason-traceability-share", type=float, default=0.7)
    ap.add_argument("--min-include-bridge-signal-share", type=float, default=0.0)
    ap.add_argument("--min-review-bridge-signal-share", type=float, default=0.0)
    ap.add_argument("--min-review-bridge-traceability-share", type=float, default=0.0)
    ap.add_argument("--min-review-bridge-traceability-given-bridge-share", type=float, default=0.0)
    ap.add_argument("--min-review-counterexample-share", type=float, default=0.0)
    ap.add_argument("--min-manual-qc-bridge-signal-share", type=float, default=0.2)
    ap.add_argument("--max-manual-qc-unknown-query-share", type=float, default=0.20)
    ap.add_argument("--min-manual-qc-review-counterexample-traceability-share", type=float, default=0.55)
    ap.add_argument("--min-review-bridge-counterexample-coupled-share", type=float, default=0.15)
    ap.add_argument("--min-review-bridge-counterexample-traceable-share", type=float, default=0.1)
    ap.add_argument("--min-review-bridge-counterexample-traceability-given-coupled-share", type=float, default=0.55)
    ap.add_argument("--max-review-bridge-counterexample-traceability-gap-share", type=float, default=0.45)
    ap.add_argument("--max-review-counterexample-without-bridge-share", type=float, default=0.35)
    ap.add_argument("--max-manual-qc-review-evidence-link-decay-share", type=float, default=0.45)
    ap.add_argument("--min-manual-qc-review-source-groups", type=int, default=2)
    ap.add_argument("--max-manual-qc-review-group-dominance", type=float, default=0.7)
    ap.add_argument("--min-manual-qc-year-diversity", type=int, default=3)
    ap.add_argument("--max-manual-qc-single-year-share", type=float, default=0.5)
    ap.add_argument("--min-manual-qc-year-entropy", type=float, default=0.45)
    ap.add_argument("--max-manual-qc-dedup-label-conflict-share", type=float, default=0.2)
    ap.add_argument("--min-dedup-score-range-alert", type=float, default=1.0)
    ap.add_argument("--max-manual-qc-dedup-score-range-alert-share", type=float, default=0.2)
    ap.add_argument("--max-manual-qc-duplicate-title-share", type=float, default=0.2)
    ap.add_argument("--max-review-weak-evidence-share", type=float, default=0.35)
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
    balanced_min_per_label = report.get("manual_qc_queue_balanced_min_per_label") or {}
    drift_term_gaps = report.get("query_drift_term_gaps") or {}

    deduped_records = int(report.get("deduped_records", 0) or 0)
    low_confidence_count = int(confidence.get("low", 0) or 0)
    single_source_only = int(stability.get("single_source_only", 0) or 0)
    zero_hit_terms = len(alias_coverage.get("zero_hit_terms") or [])
    gate_failures_near_threshold = int(triage_risk.get("gate_failures_near_threshold", 0) or 0)
    query_drift_candidate_count = int(drift_term_gaps.get("candidate_count", 0) or 0)
    balanced_by_label = balanced_summary.get("by_label") or {}
    balanced_by_confidence = balanced_summary.get("by_confidence") or {}
    balanced_by_group = balanced_summary.get("by_group") or {}
    balanced_include_rows = int(balanced_by_label.get("include", 0) or 0)
    balanced_review_rows = int(balanced_by_label.get("review", 0) or 0)
    balanced_min_per_label_target = int(balanced_min_per_label.get("target_min_per_label", 0) or 0)
    if balanced_min_per_label_target <= 0:
        balanced_min_per_label_target = args.min_balanced_min_per_label
    balanced_min_per_label_missing = balanced_min_per_label.get("missing_labels") or [
        label
        for label in ("include", "review", "exclude")
        if int(balanced_by_label.get(label, 0) or 0) < balanced_min_per_label_target
    ]
    balanced_min_per_label_satisfied = bool(balanced_min_per_label.get("satisfied", not balanced_min_per_label_missing))
    risk_reason_diversity = sum(1 for _, v in risk_reason_summary.items() if int(v or 0) > 0)
    nonzero_label_bins = sum(1 for _, v in balanced_by_label.items() if int(v or 0) > 0)
    nonzero_confidence_bins = sum(1 for _, v in balanced_by_confidence.items() if int(v or 0) > 0)
    nonzero_group_bins = sum(1 for _, v in balanced_by_group.items() if int(v or 0) > 0)
    total_balanced_label = sum(int(v or 0) for v in balanced_by_label.values())
    max_balanced_label_share = (
        round(max((int(v or 0) for v in balanced_by_label.values()), default=0) / total_balanced_label, 4)
        if total_balanced_label > 0
        else 0.0
    )
    include_count = int(labels.get("include", 0) or 0)
    review_count = int(labels.get("review", 0) or 0)
    manual_qc_label_counts: dict[str, int] = {}
    screening_reason_counts: dict[str, int] = {}
    review_screening_reason_counts: dict[str, int] = {}
    review_confidence_counts: dict[str, int] = {}
    manual_qc_source_group_counts: dict[str, int] = {}
    manual_qc_source_query_counts: dict[str, int] = {}
    manual_qc_review_source_query_counts: dict[str, int] = {}
    manual_qc_review_traceable_known_query_counts: dict[str, int] = {}
    manual_qc_review_traceable_known_query_group_counts: dict[str, int] = {}
    manual_qc_review_traceable_known_query_year_counts: dict[str, int] = {}
    manual_qc_year_counts: dict[str, int] = {}
    manual_qc_title_counts: dict[str, int] = {}
    manual_qc_review_source_group_counts: dict[str, int] = {}
    empty_screening_reason_rows = 0
    dedup_label_conflict_rows = 0
    dedup_score_range_alert_rows = 0
    bridge_signal_rows = 0
    include_bridge_signal_rows = 0
    review_bridge_signal_rows = 0
    review_bridge_traceable_rows = 0
    review_bridge_traceable_known_query_rows = 0
    review_bridge_traceable_unknown_query_rows = 0
    review_counterexample_rows = 0
    review_counterexample_traceable_rows = 0
    review_bridge_counterexample_coupled_rows = 0
    review_bridge_counterexample_traceable_coupled_rows = 0
    review_counterexample_without_bridge_rows = 0
    review_evidence_link_decay_rows = 0
    review_weak_evidence_rows = 0
    include_traceable_reason_rows = 0
    review_traceable_reason_rows = 0
    review_traceable_known_query_rows = 0
    review_traceable_known_query_unknown_group_rows = 0
    review_traceable_unknown_query_rows = 0
    traceability_tokens = ("include_hits=", "title_hits=", "query_overlap=", "bridge_sentence_hits=", "high_priority=")
    for row in manual_qc_rows:
        label = str(row.get("label") or "").strip().lower() or "unknown"
        manual_qc_label_counts[label] = manual_qc_label_counts.get(label, 0) + 1
        if is_truthy(row.get("dedup_label_conflict")):
            dedup_label_conflict_rows += 1
        dedup_score_range = float(row.get("dedup_score_range") or 0.0)
        if dedup_score_range >= args.min_dedup_score_range_alert:
            dedup_score_range_alert_rows += 1
        reason_field = str(row.get("screening_reasons") or "")
        row_is_traceable = any(token in reason_field for token in traceability_tokens)
        if not reason_field.strip():
            empty_screening_reason_rows += 1
        has_bridge_signal = "bridge_sentence_hits=" in reason_field
        if has_bridge_signal:
            bridge_signal_rows += 1
        if label == "include" and has_bridge_signal:
            include_bridge_signal_rows += 1
        if label == "review" and has_bridge_signal:
            review_bridge_signal_rows += 1
            if row_is_traceable:
                review_bridge_traceable_rows += 1
                source_query_for_bridge = str(row.get("source_query") or "").strip().lower() or "unknown"
                if source_query_for_bridge == "unknown":
                    review_bridge_traceable_unknown_query_rows += 1
                else:
                    review_bridge_traceable_known_query_rows += 1
        if label == "include" and row_is_traceable:
            include_traceable_reason_rows += 1
        if label == "review" and row_is_traceable:
            review_traceable_reason_rows += 1
        has_counterexample_signal = label == "review" and "counterexample" in reason_field.lower()
        if has_counterexample_signal:
            review_counterexample_rows += 1
            if row_is_traceable:
                review_counterexample_traceable_rows += 1
            if not has_bridge_signal:
                review_counterexample_without_bridge_rows += 1
        if label == "review" and has_bridge_signal and has_counterexample_signal:
            review_bridge_counterexample_coupled_rows += 1
            if row_is_traceable:
                review_bridge_counterexample_traceable_coupled_rows += 1
        if label == "review":
            has_evidence_link = ("query_overlap=" in reason_field) or ("title_hits=" in reason_field) or ("include_hits=" in reason_field)
            if not has_evidence_link:
                review_evidence_link_decay_rows += 1
            evidence_signal_count = sum(
                1
                for token in ("include_hits=", "title_hits=", "query_overlap=", "bridge_sentence_hits=")
                if token in reason_field
            )
            if evidence_signal_count <= 1:
                review_weak_evidence_rows += 1
        source_group = str(row.get("source_group") or "").strip().lower() or "unknown"
        source_query = str(row.get("source_query") or "").strip().lower() or "unknown"
        year = str(row.get("year") or "").strip() or "unknown"
        title_key = normalize_title(row.get("title") or "")
        if title_key:
            manual_qc_title_counts[title_key] = manual_qc_title_counts.get(title_key, 0) + 1
        if label == "review" and row_is_traceable and source_query != "unknown":
            review_traceable_known_query_rows += 1
            if source_group == "unknown":
                review_traceable_known_query_unknown_group_rows += 1
            manual_qc_review_traceable_known_query_counts[source_query] = (
                manual_qc_review_traceable_known_query_counts.get(source_query, 0) + 1
            )
            manual_qc_review_traceable_known_query_group_counts[source_group] = (
                manual_qc_review_traceable_known_query_group_counts.get(source_group, 0) + 1
            )
            manual_qc_review_traceable_known_query_year_counts[year] = (
                manual_qc_review_traceable_known_query_year_counts.get(year, 0) + 1
            )
        if label == "review" and row_is_traceable and source_query == "unknown":
            review_traceable_unknown_query_rows += 1
        review_confidence = str(row.get("confidence") or "").strip().lower() or "unknown"
        manual_qc_source_group_counts[source_group] = manual_qc_source_group_counts.get(source_group, 0) + 1
        manual_qc_source_query_counts[source_query] = manual_qc_source_query_counts.get(source_query, 0) + 1
        manual_qc_year_counts[year] = manual_qc_year_counts.get(year, 0) + 1
        if label == "review":
            manual_qc_review_source_group_counts[source_group] = manual_qc_review_source_group_counts.get(source_group, 0) + 1
            manual_qc_review_source_query_counts[source_query] = manual_qc_review_source_query_counts.get(source_query, 0) + 1
        tokens = [token.strip().lower() for token in reason_field.replace("|", ";").split(";") if token.strip()]
        seen = set()
        for token in tokens:
            if token in seen:
                continue
            screening_reason_counts[token] = screening_reason_counts.get(token, 0) + 1
            if label == "review":
                review_screening_reason_counts[token] = review_screening_reason_counts.get(token, 0) + 1
            seen.add(token)
        if label == "review":
            review_confidence_counts[review_confidence] = review_confidence_counts.get(review_confidence, 0) + 1
    manual_qc_include_rows = int(manual_qc_label_counts.get("include", 0) or 0)
    manual_qc_review_rows = int(manual_qc_label_counts.get("review", 0) or 0)
    manual_qc_review_share = pct(manual_qc_review_rows, len(manual_qc_rows))
    manual_qc_label_dominance = (
        round(max(manual_qc_label_counts.values(), default=0) / max(1, len(manual_qc_rows)), 4)
        if manual_qc_rows
        else 0.0
    )
    manual_qc_source_group_diversity = sum(1 for _, v in manual_qc_source_group_counts.items() if int(v or 0) > 0)
    manual_qc_review_source_group_diversity = sum(
        1 for _, v in manual_qc_review_source_group_counts.items() if int(v or 0) > 0
    )
    manual_qc_year_diversity = sum(1 for _, v in manual_qc_year_counts.items() if int(v or 0) > 0)
    manual_qc_single_year_share = (
        round(max(manual_qc_year_counts.values(), default=0) / max(1, len(manual_qc_rows)), 4)
        if manual_qc_rows
        else 0.0
    )
    manual_qc_year_entropy = normalized_entropy(manual_qc_year_counts)
    manual_qc_dedup_label_conflict_share = pct(dedup_label_conflict_rows, len(manual_qc_rows))
    manual_qc_dedup_score_range_alert_share = pct(dedup_score_range_alert_rows, len(manual_qc_rows))
    duplicate_title_rows = sum(count for count in manual_qc_title_counts.values() if count > 1)
    manual_qc_duplicate_title_share = pct(duplicate_title_rows, len(manual_qc_rows))
    manual_qc_single_query_share = (
        round(max(manual_qc_source_query_counts.values(), default=0) / max(1, len(manual_qc_rows)), 4)
        if manual_qc_rows
        else 0.0
    )
    empty_screening_reason_share = pct(empty_screening_reason_rows, len(manual_qc_rows))
    traceable_reason_rows = sum(
        1
        for row in manual_qc_rows
        if any(token in str(row.get("screening_reasons") or "") for token in traceability_tokens)
    )
    screening_reason_traceability_share = pct(traceable_reason_rows, len(manual_qc_rows))
    include_reason_traceability_share = pct(include_traceable_reason_rows, manual_qc_include_rows)
    review_reason_traceability_share = pct(review_traceable_reason_rows, manual_qc_review_rows)
    include_bridge_signal_share = pct(include_bridge_signal_rows, manual_qc_include_rows)
    review_bridge_signal_share = pct(review_bridge_signal_rows, manual_qc_review_rows)
    review_bridge_traceability_share = pct(review_bridge_traceable_rows, manual_qc_review_rows)
    review_bridge_traceability_given_bridge_share = pct(review_bridge_traceable_rows, review_bridge_signal_rows)
    review_bridge_traceable_known_query_share = pct(
        review_bridge_traceable_known_query_rows,
        review_bridge_traceable_rows,
    )
    review_bridge_traceable_unknown_query_share = pct(
        review_bridge_traceable_unknown_query_rows,
        review_bridge_traceable_rows,
    )
    review_counterexample_share = pct(review_counterexample_rows, manual_qc_review_rows)
    review_counterexample_traceability_share = pct(review_counterexample_traceable_rows, review_counterexample_rows)
    review_bridge_counterexample_coupled_share = pct(review_bridge_counterexample_coupled_rows, manual_qc_review_rows)
    review_bridge_counterexample_traceable_coupled_share = pct(
        review_bridge_counterexample_traceable_coupled_rows,
        manual_qc_review_rows,
    )
    review_bridge_counterexample_traceability_given_coupled_share = pct(
        review_bridge_counterexample_traceable_coupled_rows,
        review_bridge_counterexample_coupled_rows,
    )
    review_bridge_counterexample_traceability_gap_share = pct(
        review_bridge_counterexample_coupled_rows - review_bridge_counterexample_traceable_coupled_rows,
        review_bridge_counterexample_coupled_rows,
    )
    review_counterexample_without_bridge_share = pct(
        review_counterexample_without_bridge_rows,
        review_counterexample_rows,
    )
    review_evidence_link_decay_share = pct(review_evidence_link_decay_rows, manual_qc_review_rows)
    review_weak_evidence_share = pct(review_weak_evidence_rows, manual_qc_review_rows)
    manual_qc_bridge_signal_share = pct(bridge_signal_rows, len(manual_qc_rows))
    unknown_query_rows = int(manual_qc_source_query_counts.get("unknown", 0) or 0)
    manual_qc_unknown_query_share = pct(unknown_query_rows, len(manual_qc_rows))
    manual_qc_review_group_dominance = (
        round(max(manual_qc_review_source_group_counts.values(), default=0) / max(1, manual_qc_review_rows), 4)
        if manual_qc_review_rows
        else 0.0
    )
    screening_reason_entropy = normalized_entropy(screening_reason_counts)
    manual_qc_query_entropy = normalized_entropy(manual_qc_source_query_counts)
    manual_qc_review_query_entropy = normalized_entropy(manual_qc_review_source_query_counts)
    manual_qc_risk_reason_entropy = normalized_entropy(risk_reason_summary)
    manual_qc_review_reason_entropy = normalized_entropy(review_screening_reason_counts)
    manual_qc_review_confidence_bins = sum(1 for _, v in review_confidence_counts.items() if int(v or 0) > 0)
    manual_qc_review_confidence_entropy = normalized_entropy(review_confidence_counts)
    manual_qc_review_traceable_known_query_share = pct(review_traceable_known_query_rows, manual_qc_review_rows)
    manual_qc_review_traceable_unknown_query_share = pct(review_traceable_unknown_query_rows, manual_qc_review_rows)
    manual_qc_review_query_traceability_share = pct(review_traceable_known_query_rows, review_traceable_reason_rows)
    manual_qc_review_traceable_known_query_entropy = normalized_entropy(manual_qc_review_traceable_known_query_counts)
    manual_qc_review_traceable_known_query_coverage = sum(
        1 for _, v in manual_qc_review_traceable_known_query_counts.items() if int(v or 0) > 0
    )
    manual_qc_review_traceable_known_query_hhi = normalized_hhi(manual_qc_review_traceable_known_query_counts)
    manual_qc_review_traceable_known_query_top_share = (
        round(max(manual_qc_review_traceable_known_query_counts.values(), default=0) / max(1, review_traceable_known_query_rows), 4)
        if review_traceable_known_query_rows
        else 0.0
    )
    manual_qc_review_traceable_known_query_top2_share = (
        round(
            sum(sorted((int(v or 0) for v in manual_qc_review_traceable_known_query_counts.values()), reverse=True)[:2])
            / max(1, review_traceable_known_query_rows),
            4,
        )
        if review_traceable_known_query_rows
        else 0.0
    )
    manual_qc_review_traceable_known_query_top3_share = (
        round(
            sum(sorted((int(v or 0) for v in manual_qc_review_traceable_known_query_counts.values()), reverse=True)[:3])
            / max(1, review_traceable_known_query_rows),
            4,
        )
        if review_traceable_known_query_rows
        else 0.0
    )
    manual_qc_review_traceable_known_query_bottom_share = (
        round(min(manual_qc_review_traceable_known_query_counts.values(), default=0) / max(1, review_traceable_known_query_rows), 4)
        if manual_qc_review_traceable_known_query_counts
        else 0.0
    )
    manual_qc_review_traceable_known_query_bottom2_share = (
        round(
            sum(sorted((int(v or 0) for v in manual_qc_review_traceable_known_query_counts.values()))[:2])
            / max(1, review_traceable_known_query_rows),
            4,
        )
        if review_traceable_known_query_rows
        else 0.0
    )
    manual_qc_review_traceable_known_query_tail_share = round(
        max(0.0, 1.0 - manual_qc_review_traceable_known_query_top2_share),
        4,
    )
    manual_qc_review_traceable_known_query_effective_count = effective_query_count(
        manual_qc_review_traceable_known_query_counts
    )
    manual_qc_review_traceable_known_query_top_bottom_gap = round(
        manual_qc_review_traceable_known_query_top_share - manual_qc_review_traceable_known_query_bottom_share,
        4,
    )
    manual_qc_review_traceable_known_query_group_entropy = normalized_entropy(
        manual_qc_review_traceable_known_query_group_counts
    )
    manual_qc_review_traceable_known_query_group_coverage = sum(
        1 for _, v in manual_qc_review_traceable_known_query_group_counts.items() if int(v or 0) > 0
    )
    manual_qc_review_traceable_known_query_group_top_share = (
        round(max(manual_qc_review_traceable_known_query_group_counts.values(), default=0) / max(1, review_traceable_known_query_rows), 4)
        if review_traceable_known_query_rows
        else 0.0
    )
    manual_qc_review_traceable_known_query_group_top2_share = (
        round(
            sum(sorted((int(v or 0) for v in manual_qc_review_traceable_known_query_group_counts.values()), reverse=True)[:2])
            / max(1, review_traceable_known_query_rows),
            4,
        )
        if review_traceable_known_query_rows
        else 0.0
    )
    manual_qc_review_traceable_known_query_group_tail_share = round(
        max(0.0, 1.0 - manual_qc_review_traceable_known_query_group_top2_share),
        4,
    )
    manual_qc_review_traceable_known_query_group_js_divergence = js_divergence(
        manual_qc_review_traceable_known_query_group_counts,
        manual_qc_source_group_counts,
    )
    manual_qc_review_traceable_known_query_unknown_group_share = pct(
        review_traceable_known_query_unknown_group_rows,
        review_traceable_known_query_rows,
    )
    manual_qc_review_traceable_known_query_year_js_divergence = js_divergence(
        manual_qc_review_traceable_known_query_year_counts,
        manual_qc_year_counts,
    )
    global_known_query_counts = {
        k: int(v or 0)
        for k, v in manual_qc_source_query_counts.items()
        if str(k).strip().lower() != "unknown" and int(v or 0) > 0
    }
    manual_qc_review_traceable_known_query_js_divergence = js_divergence(
        manual_qc_review_traceable_known_query_counts,
        global_known_query_counts,
    )
    review_to_include_ratio = round(review_count / max(1, include_count), 4)
    high_risk_qc_rows = sum(1 for row in manual_qc_rows if float(row.get("risk_score") or 0.0) >= 5.0)
    manual_qc_high_risk_share = pct(high_risk_qc_rows, len(manual_qc_rows))
    total_risk_reason_hits = sum(int(v or 0) for v in risk_reason_summary.values())
    top_risk_reason_share = (
        round(max((int(v or 0) for v in risk_reason_summary.values()), default=0) / total_risk_reason_hits, 4)
        if total_risk_reason_hits > 0
        else 0.0
    )
    screening_reason_diversity = sum(1 for _, v in screening_reason_counts.items() if int(v or 0) > 0)
    total_screening_reason_hits = sum(int(v or 0) for v in screening_reason_counts.values())
    top_screening_reason_share = (
        round(max((int(v or 0) for v in screening_reason_counts.values()), default=0) / total_screening_reason_hits, 4)
        if total_screening_reason_hits > 0
        else 0.0
    )

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
        {
            "name": "balanced_label_bins_floor",
            "status": "pass" if nonzero_label_bins >= args.min_balanced_label_bins else "fail",
            "observed": nonzero_label_bins,
            "threshold": f">={args.min_balanced_label_bins}",
        },
        {
            "name": "balanced_confidence_bins_floor",
            "status": "pass" if nonzero_confidence_bins >= args.min_balanced_confidence_bins else "fail",
            "observed": nonzero_confidence_bins,
            "threshold": f">={args.min_balanced_confidence_bins}",
        },
        {
            "name": "balanced_group_bins_floor",
            "status": "pass" if nonzero_group_bins >= args.min_balanced_group_bins else "fail",
            "observed": nonzero_group_bins,
            "threshold": f">={args.min_balanced_group_bins}",
        },
        {
            "name": "balanced_label_dominance_ceiling",
            "status": "pass" if max_balanced_label_share <= args.max_balanced_label_dominance else "fail",
            "observed": max_balanced_label_share,
            "threshold": f"<={args.max_balanced_label_dominance}",
        },
        {
            "name": "balanced_include_rows_floor",
            "status": "pass" if balanced_include_rows >= args.min_balanced_include_rows else "fail",
            "observed": balanced_include_rows,
            "threshold": f">={args.min_balanced_include_rows}",
        },
        {
            "name": "balanced_review_rows_floor",
            "status": "pass" if balanced_review_rows >= args.min_balanced_review_rows else "fail",
            "observed": balanced_review_rows,
            "threshold": f">={args.min_balanced_review_rows}",
        },
        {
            "name": "balanced_min_per_label_floor",
            "status": "pass" if balanced_min_per_label_satisfied and balanced_min_per_label_target >= args.min_balanced_min_per_label else "fail",
            "observed": {
                "target": balanced_min_per_label_target,
                "missing_labels": balanced_min_per_label_missing,
            },
            "threshold": f"satisfied target>={args.min_balanced_min_per_label}",
        },
        {
            "name": "query_drift_candidates_ceiling",
            "status": "pass" if query_drift_candidate_count <= args.max_query_drift_candidates else "fail",
            "observed": query_drift_candidate_count,
            "threshold": f"<={args.max_query_drift_candidates}",
        },
        {
            "name": "risk_reason_diversity_floor",
            "status": "pass" if risk_reason_diversity >= args.min_risk_reason_diversity else "fail",
            "observed": risk_reason_diversity,
            "threshold": f">={args.min_risk_reason_diversity}",
        },
        {
            "name": "top_risk_reason_share_ceiling",
            "status": "pass" if top_risk_reason_share <= args.max_top_risk_reason_share else "fail",
            "observed": top_risk_reason_share,
            "threshold": f"<={args.max_top_risk_reason_share}",
        },
        {
            "name": "screening_reason_diversity_floor",
            "status": "pass" if screening_reason_diversity >= args.min_screening_reason_diversity else "fail",
            "observed": screening_reason_diversity,
            "threshold": f">={args.min_screening_reason_diversity}",
        },
        {
            "name": "top_screening_reason_share_ceiling",
            "status": "pass" if top_screening_reason_share <= args.max_top_screening_reason_share else "fail",
            "observed": top_screening_reason_share,
            "threshold": f"<={args.max_top_screening_reason_share}",
        },
        {
            "name": "screening_reason_entropy_floor",
            "status": "pass" if screening_reason_entropy >= args.min_screening_reason_entropy else "fail",
            "observed": screening_reason_entropy,
            "threshold": f">={args.min_screening_reason_entropy}",
        },
        {
            "name": "manual_qc_query_entropy_floor",
            "status": "pass" if manual_qc_query_entropy >= args.min_manual_qc_query_entropy else "fail",
            "observed": manual_qc_query_entropy,
            "threshold": f">={args.min_manual_qc_query_entropy}",
        },
        {
            "name": "manual_qc_review_query_entropy_floor",
            "status": "pass"
            if manual_qc_review_query_entropy >= args.min_manual_qc_review_query_entropy
            else "fail",
            "observed": manual_qc_review_query_entropy,
            "threshold": f">={args.min_manual_qc_review_query_entropy}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_share_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_share
            >= args.min_manual_qc_review_traceable_known_query_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_share,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_share}",
        },
        {
            "name": "manual_qc_review_traceable_unknown_query_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_unknown_query_share
            <= args.max_manual_qc_review_traceable_unknown_query_share
            else "fail",
            "observed": manual_qc_review_traceable_unknown_query_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_unknown_query_share}",
        },
        {
            "name": "manual_qc_review_query_traceability_share_floor",
            "status": "pass"
            if manual_qc_review_query_traceability_share
            >= args.min_manual_qc_review_query_traceability_share
            else "fail",
            "observed": manual_qc_review_query_traceability_share,
            "threshold": f">={args.min_manual_qc_review_query_traceability_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_entropy_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_entropy
            >= args.min_manual_qc_review_traceable_known_query_entropy
            else "fail",
            "observed": manual_qc_review_traceable_known_query_entropy,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_entropy}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_coverage_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_coverage
            >= args.min_manual_qc_review_traceable_known_query_coverage
            else "fail",
            "observed": manual_qc_review_traceable_known_query_coverage,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_coverage}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_hhi_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_hhi
            <= args.max_manual_qc_review_traceable_known_query_hhi
            else "fail",
            "observed": manual_qc_review_traceable_known_query_hhi,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_hhi}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_top_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_top_share
            <= args.max_manual_qc_review_traceable_known_query_top_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_top_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_top_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_top2_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_top2_share
            <= args.max_manual_qc_review_traceable_known_query_top2_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_top2_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_top2_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_top3_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_top3_share
            <= args.max_manual_qc_review_traceable_known_query_top3_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_top3_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_top3_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_js_divergence_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_js_divergence
            <= args.max_manual_qc_review_traceable_known_query_js_divergence
            else "fail",
            "observed": manual_qc_review_traceable_known_query_js_divergence,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_js_divergence}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_tail_share_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_tail_share
            >= args.min_manual_qc_review_traceable_known_query_tail_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_tail_share,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_tail_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_bottom2_share_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_bottom2_share
            >= args.min_manual_qc_review_traceable_known_query_bottom2_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_bottom2_share,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_bottom2_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_effective_count_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_effective_count
            >= args.min_manual_qc_review_traceable_known_query_effective_count
            else "fail",
            "observed": manual_qc_review_traceable_known_query_effective_count,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_effective_count}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_top_bottom_gap_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_top_bottom_gap
            <= args.max_manual_qc_review_traceable_known_query_top_bottom_gap
            else "fail",
            "observed": manual_qc_review_traceable_known_query_top_bottom_gap,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_top_bottom_gap}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_group_entropy_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_group_entropy
            >= args.min_manual_qc_review_traceable_known_query_group_entropy
            else "fail",
            "observed": manual_qc_review_traceable_known_query_group_entropy,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_group_entropy}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_group_coverage_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_group_coverage
            >= args.min_manual_qc_review_traceable_known_query_group_coverage
            else "fail",
            "observed": manual_qc_review_traceable_known_query_group_coverage,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_group_coverage}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_group_top_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_group_top_share
            <= args.max_manual_qc_review_traceable_known_query_group_top_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_group_top_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_group_top_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_group_top2_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_group_top2_share
            <= args.max_manual_qc_review_traceable_known_query_group_top2_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_group_top2_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_group_top2_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_group_tail_share_floor",
            "status": "pass"
            if manual_qc_review_traceable_known_query_group_tail_share
            >= args.min_manual_qc_review_traceable_known_query_group_tail_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_group_tail_share,
            "threshold": f">={args.min_manual_qc_review_traceable_known_query_group_tail_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_group_js_divergence_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_group_js_divergence
            <= args.max_manual_qc_review_traceable_known_query_group_js_divergence
            else "fail",
            "observed": manual_qc_review_traceable_known_query_group_js_divergence,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_group_js_divergence}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_unknown_group_share_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_unknown_group_share
            <= args.max_manual_qc_review_traceable_known_query_unknown_group_share
            else "fail",
            "observed": manual_qc_review_traceable_known_query_unknown_group_share,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_unknown_group_share}",
        },
        {
            "name": "manual_qc_review_traceable_known_query_year_js_divergence_ceiling",
            "status": "pass"
            if manual_qc_review_traceable_known_query_year_js_divergence
            <= args.max_manual_qc_review_traceable_known_query_year_js_divergence
            else "fail",
            "observed": manual_qc_review_traceable_known_query_year_js_divergence,
            "threshold": f"<={args.max_manual_qc_review_traceable_known_query_year_js_divergence}",
        },
        {
            "name": "review_bridge_traceable_known_query_share_floor",
            "status": "pass"
            if review_bridge_traceable_known_query_share >= args.min_review_bridge_traceable_known_query_share
            else "fail",
            "observed": review_bridge_traceable_known_query_share,
            "threshold": f">={args.min_review_bridge_traceable_known_query_share}",
        },
        {
            "name": "review_bridge_traceable_unknown_query_share_ceiling",
            "status": "pass"
            if review_bridge_traceable_unknown_query_share <= args.max_review_bridge_traceable_unknown_query_share
            else "fail",
            "observed": review_bridge_traceable_unknown_query_share,
            "threshold": f"<={args.max_review_bridge_traceable_unknown_query_share}",
        },
        {
            "name": "manual_qc_risk_reason_entropy_floor",
            "status": "pass" if manual_qc_risk_reason_entropy >= args.min_manual_qc_risk_reason_entropy else "fail",
            "observed": manual_qc_risk_reason_entropy,
            "threshold": f">={args.min_manual_qc_risk_reason_entropy}",
        },
        {
            "name": "manual_qc_review_reason_entropy_floor",
            "status": "pass"
            if manual_qc_review_reason_entropy >= args.min_manual_qc_review_reason_entropy
            else "fail",
            "observed": manual_qc_review_reason_entropy,
            "threshold": f">={args.min_manual_qc_review_reason_entropy}",
        },
        {
            "name": "manual_qc_review_confidence_bins_floor",
            "status": "pass"
            if manual_qc_review_confidence_bins >= args.min_manual_qc_review_confidence_bins
            else "fail",
            "observed": manual_qc_review_confidence_bins,
            "threshold": f">={args.min_manual_qc_review_confidence_bins}",
        },
        {
            "name": "manual_qc_review_confidence_entropy_floor",
            "status": "pass"
            if manual_qc_review_confidence_entropy >= args.min_manual_qc_review_confidence_entropy
            else "fail",
            "observed": manual_qc_review_confidence_entropy,
            "threshold": f">={args.min_manual_qc_review_confidence_entropy}",
        },
        {
            "name": "screening_reason_traceability_share_floor",
            "status": "pass"
            if screening_reason_traceability_share >= args.min_screening_reason_traceability_share
            else "fail",
            "observed": screening_reason_traceability_share,
            "threshold": f">={args.min_screening_reason_traceability_share}",
        },
        {
            "name": "include_reason_traceability_share_floor",
            "status": "pass"
            if include_reason_traceability_share >= args.min_include_reason_traceability_share
            else "fail",
            "observed": include_reason_traceability_share,
            "threshold": f">={args.min_include_reason_traceability_share}",
        },
        {
            "name": "review_reason_traceability_share_floor",
            "status": "pass"
            if review_reason_traceability_share >= args.min_review_reason_traceability_share
            else "fail",
            "observed": review_reason_traceability_share,
            "threshold": f">={args.min_review_reason_traceability_share}",
        },
        {
            "name": "include_bridge_signal_share_floor",
            "status": "pass" if include_bridge_signal_share >= args.min_include_bridge_signal_share else "fail",
            "observed": include_bridge_signal_share,
            "threshold": f">={args.min_include_bridge_signal_share}",
        },
        {
            "name": "review_bridge_signal_share_floor",
            "status": "pass" if review_bridge_signal_share >= args.min_review_bridge_signal_share else "fail",
            "observed": review_bridge_signal_share,
            "threshold": f">={args.min_review_bridge_signal_share}",
        },
        {
            "name": "review_bridge_traceability_share_floor",
            "status": "pass"
            if review_bridge_traceability_share >= args.min_review_bridge_traceability_share
            else "fail",
            "observed": review_bridge_traceability_share,
            "threshold": f">={args.min_review_bridge_traceability_share}",
        },
        {
            "name": "review_bridge_traceability_given_bridge_share_floor",
            "status": "pass"
            if review_bridge_traceability_given_bridge_share >= args.min_review_bridge_traceability_given_bridge_share
            else "fail",
            "observed": review_bridge_traceability_given_bridge_share,
            "threshold": f">={args.min_review_bridge_traceability_given_bridge_share}",
        },
        {
            "name": "review_counterexample_share_floor",
            "status": "pass" if review_counterexample_share >= args.min_review_counterexample_share else "fail",
            "observed": review_counterexample_share,
            "threshold": f">={args.min_review_counterexample_share}",
        },
        {
            "name": "review_counterexample_traceability_share_floor",
            "status": "pass"
            if review_counterexample_traceability_share >= args.min_manual_qc_review_counterexample_traceability_share
            else "fail",
            "observed": review_counterexample_traceability_share,
            "threshold": f">={args.min_manual_qc_review_counterexample_traceability_share}",
        },
        {
            "name": "review_bridge_counterexample_coupled_share_floor",
            "status": "pass"
            if review_bridge_counterexample_coupled_share >= args.min_review_bridge_counterexample_coupled_share
            else "fail",
            "observed": review_bridge_counterexample_coupled_share,
            "threshold": f">={args.min_review_bridge_counterexample_coupled_share}",
        },
        {
            "name": "review_bridge_counterexample_traceable_share_floor",
            "status": "pass"
            if review_bridge_counterexample_traceable_coupled_share >= args.min_review_bridge_counterexample_traceable_share
            else "fail",
            "observed": review_bridge_counterexample_traceable_coupled_share,
            "threshold": f">={args.min_review_bridge_counterexample_traceable_share}",
        },
        {
            "name": "review_bridge_counterexample_traceability_given_coupled_share_floor",
            "status": "pass"
            if review_bridge_counterexample_traceability_given_coupled_share
            >= args.min_review_bridge_counterexample_traceability_given_coupled_share
            else "fail",
            "observed": review_bridge_counterexample_traceability_given_coupled_share,
            "threshold": f">={args.min_review_bridge_counterexample_traceability_given_coupled_share}",
        },
        {
            "name": "review_bridge_counterexample_traceability_gap_share_ceiling",
            "status": "pass"
            if review_bridge_counterexample_traceability_gap_share <= args.max_review_bridge_counterexample_traceability_gap_share
            else "fail",
            "observed": review_bridge_counterexample_traceability_gap_share,
            "threshold": f"<={args.max_review_bridge_counterexample_traceability_gap_share}",
        },
        {
            "name": "review_counterexample_without_bridge_share_ceiling",
            "status": "pass"
            if review_counterexample_without_bridge_share <= args.max_review_counterexample_without_bridge_share
            else "fail",
            "observed": review_counterexample_without_bridge_share,
            "threshold": f"<={args.max_review_counterexample_without_bridge_share}",
        },
        {
            "name": "review_evidence_link_decay_share_ceiling",
            "status": "pass"
            if review_evidence_link_decay_share <= args.max_manual_qc_review_evidence_link_decay_share
            else "fail",
            "observed": review_evidence_link_decay_share,
            "threshold": f"<={args.max_manual_qc_review_evidence_link_decay_share}",
        },
        {
            "name": "review_weak_evidence_share_ceiling",
            "status": "pass"
            if review_weak_evidence_share <= args.max_review_weak_evidence_share
            else "fail",
            "observed": review_weak_evidence_share,
            "threshold": f"<={args.max_review_weak_evidence_share}",
        },
        {
            "name": "manual_qc_bridge_signal_share_floor",
            "status": "pass" if manual_qc_bridge_signal_share >= args.min_manual_qc_bridge_signal_share else "fail",
            "observed": manual_qc_bridge_signal_share,
            "threshold": f">={args.min_manual_qc_bridge_signal_share}",
        },
        {
            "name": "manual_qc_year_diversity_floor",
            "status": "pass" if manual_qc_year_diversity >= args.min_manual_qc_year_diversity else "fail",
            "observed": manual_qc_year_diversity,
            "threshold": f">={args.min_manual_qc_year_diversity}",
        },
        {
            "name": "manual_qc_single_year_share_ceiling",
            "status": "pass" if manual_qc_single_year_share <= args.max_manual_qc_single_year_share else "fail",
            "observed": manual_qc_single_year_share,
            "threshold": f"<={args.max_manual_qc_single_year_share}",
        },
        {
            "name": "manual_qc_year_entropy_floor",
            "status": "pass" if manual_qc_year_entropy >= args.min_manual_qc_year_entropy else "fail",
            "observed": manual_qc_year_entropy,
            "threshold": f">={args.min_manual_qc_year_entropy}",
        },
        {
            "name": "manual_qc_unknown_query_share_ceiling",
            "status": "pass" if manual_qc_unknown_query_share <= args.max_manual_qc_unknown_query_share else "fail",
            "observed": manual_qc_unknown_query_share,
            "threshold": f"<={args.max_manual_qc_unknown_query_share}",
        },
        {
            "name": "manual_qc_dedup_label_conflict_share_ceiling",
            "status": "pass"
            if manual_qc_dedup_label_conflict_share <= args.max_manual_qc_dedup_label_conflict_share
            else "fail",
            "observed": manual_qc_dedup_label_conflict_share,
            "threshold": f"<={args.max_manual_qc_dedup_label_conflict_share}",
        },
        {
            "name": "manual_qc_dedup_score_range_alert_share_ceiling",
            "status": "pass"
            if manual_qc_dedup_score_range_alert_share <= args.max_manual_qc_dedup_score_range_alert_share
            else "fail",
            "observed": manual_qc_dedup_score_range_alert_share,
            "threshold": (
                f"<={args.max_manual_qc_dedup_score_range_alert_share} "
                f"(alert if dedup_score_range>={args.min_dedup_score_range_alert})"
            ),
        },
        {
            "name": "manual_qc_duplicate_title_share_ceiling",
            "status": "pass"
            if manual_qc_duplicate_title_share <= args.max_manual_qc_duplicate_title_share
            else "fail",
            "observed": manual_qc_duplicate_title_share,
            "threshold": f"<={args.max_manual_qc_duplicate_title_share}",
        },
        {
            "name": "manual_qc_source_group_diversity_floor",
            "status": "pass" if manual_qc_source_group_diversity >= args.min_manual_qc_source_groups else "fail",
            "observed": manual_qc_source_group_diversity,
            "threshold": f">={args.min_manual_qc_source_groups}",
        },
        {
            "name": "manual_qc_review_source_group_diversity_floor",
            "status": "pass"
            if manual_qc_review_source_group_diversity >= args.min_manual_qc_review_source_groups
            else "fail",
            "observed": manual_qc_review_source_group_diversity,
            "threshold": f">={args.min_manual_qc_review_source_groups}",
        },
        {
            "name": "manual_qc_review_group_dominance_ceiling",
            "status": "pass"
            if manual_qc_review_group_dominance <= args.max_manual_qc_review_group_dominance
            else "fail",
            "observed": manual_qc_review_group_dominance,
            "threshold": f"<={args.max_manual_qc_review_group_dominance}",
        },
        {
            "name": "manual_qc_single_query_share_ceiling",
            "status": "pass" if manual_qc_single_query_share <= args.max_manual_qc_single_query_share else "fail",
            "observed": manual_qc_single_query_share,
            "threshold": f"<={args.max_manual_qc_single_query_share}",
        },
        {
            "name": "empty_screening_reason_share_ceiling",
            "status": "pass" if empty_screening_reason_share <= args.max_empty_screening_reason_share else "fail",
            "observed": empty_screening_reason_share,
            "threshold": f"<={args.max_empty_screening_reason_share}",
        },
        {
            "name": "review_to_include_ratio_ceiling",
            "status": "pass" if review_to_include_ratio <= args.max_review_to_include_ratio else "fail",
            "observed": review_to_include_ratio,
            "threshold": f"<={args.max_review_to_include_ratio}",
        },
        {
            "name": "manual_qc_include_rows_floor",
            "status": "pass" if manual_qc_include_rows >= args.min_manual_qc_include_rows else "fail",
            "observed": manual_qc_include_rows,
            "threshold": f">={args.min_manual_qc_include_rows}",
        },
        {
            "name": "manual_qc_review_share_band",
            "status": "pass"
            if args.min_manual_qc_review_share <= manual_qc_review_share <= args.max_manual_qc_review_share
            else "fail",
            "observed": manual_qc_review_share,
            "threshold": f">={args.min_manual_qc_review_share} and <={args.max_manual_qc_review_share}",
        },
        {
            "name": "manual_qc_label_dominance_ceiling",
            "status": "pass" if manual_qc_label_dominance <= args.max_manual_qc_label_dominance else "fail",
            "observed": manual_qc_label_dominance,
            "threshold": f"<={args.max_manual_qc_label_dominance}",
        },
        {
            "name": "manual_qc_high_risk_share_ceiling",
            "status": "pass" if manual_qc_high_risk_share <= args.max_manual_qc_high_risk_share else "fail",
            "observed": manual_qc_high_risk_share,
            "threshold": f"<={args.max_manual_qc_high_risk_share}",
        },
    ]

    fail_count = sum(1 for gate in gates if gate["status"] == "fail")
    quality_score = round(max(0.0, 100.0 - fail_count * 15.0 - zero_hit_terms * 1.5), 2)
    status = "pass" if fail_count == 0 else "review"

    hotspots = [
        {"label": "top_qc_risk_reasons", "value": top_items(risk_reason_summary, limit=5)},
        {"label": "top_screening_reasons", "value": top_items(screening_reason_counts, limit=6)},
        {"label": "balanced_qc_by_label", "value": balanced_summary.get("by_label") or {}},
        {"label": "manual_qc_label_counts", "value": manual_qc_label_counts},
        {"label": "manual_qc_source_groups", "value": top_items(manual_qc_source_group_counts, limit=6)},
        {"label": "manual_qc_source_queries", "value": top_items(manual_qc_source_query_counts, limit=6)},
        {"label": "manual_qc_dedup_stability", "value": {
            "label_conflict_rows": dedup_label_conflict_rows,
            "label_conflict_share": manual_qc_dedup_label_conflict_share,
            "score_range_alert_rows": dedup_score_range_alert_rows,
            "score_range_alert_share": manual_qc_dedup_score_range_alert_share,
            "duplicate_title_rows": duplicate_title_rows,
            "duplicate_title_share": manual_qc_duplicate_title_share,
            "score_range_alert_threshold": args.min_dedup_score_range_alert,
        }},
        {"label": "manual_qc_duplicate_titles", "value": top_items({k: v for k, v in manual_qc_title_counts.items() if v > 1}, limit=6)},
        {"label": "manual_qc_review_confidence_distribution", "value": top_items(review_confidence_counts, limit=5)},
        {"label": "manual_qc_review_traceable_known_query", "value": {
            "rows": review_traceable_known_query_rows,
            "share": manual_qc_review_traceable_known_query_share,
        }},
        {"label": "manual_qc_review_traceable_unknown_query", "value": {
            "rows": review_traceable_unknown_query_rows,
            "share": manual_qc_review_traceable_unknown_query_share,
        }},
        {"label": "manual_qc_review_query_traceability", "value": {
            "known_query_rows": review_traceable_known_query_rows,
            "traceable_review_rows": review_traceable_reason_rows,
            "share": manual_qc_review_query_traceability_share,
            "known_query_entropy": manual_qc_review_traceable_known_query_entropy,
            "known_query_coverage": manual_qc_review_traceable_known_query_coverage,
            "known_query_hhi": manual_qc_review_traceable_known_query_hhi,
            "known_query_top_share": manual_qc_review_traceable_known_query_top_share,
            "known_query_top2_share": manual_qc_review_traceable_known_query_top2_share,
            "known_query_top3_share": manual_qc_review_traceable_known_query_top3_share,
            "known_query_tail_share": manual_qc_review_traceable_known_query_tail_share,
            "known_query_effective_count": manual_qc_review_traceable_known_query_effective_count,
            "known_query_bottom_share": manual_qc_review_traceable_known_query_bottom_share,
            "known_query_bottom2_share": manual_qc_review_traceable_known_query_bottom2_share,
            "known_query_top_bottom_gap": manual_qc_review_traceable_known_query_top_bottom_gap,
            "known_query_group_entropy": manual_qc_review_traceable_known_query_group_entropy,
            "known_query_group_coverage": manual_qc_review_traceable_known_query_group_coverage,
            "known_query_group_top_share": manual_qc_review_traceable_known_query_group_top_share,
            "known_query_group_top2_share": manual_qc_review_traceable_known_query_group_top2_share,
            "known_query_group_tail_share": manual_qc_review_traceable_known_query_group_tail_share,
            "known_query_group_js_divergence": manual_qc_review_traceable_known_query_group_js_divergence,
            "known_query_unknown_group_share": manual_qc_review_traceable_known_query_unknown_group_share,
            "known_query_year_js_divergence": manual_qc_review_traceable_known_query_year_js_divergence,
        }},
        {"label": "review_bridge_known_query_traceability", "value": {
            "known_query_rows": review_bridge_traceable_known_query_rows,
            "unknown_query_rows": review_bridge_traceable_unknown_query_rows,
            "known_query_share": review_bridge_traceable_known_query_share,
            "unknown_query_share": review_bridge_traceable_unknown_query_share,
        }},
        {"label": "label_traceability_share", "value": {
            "include": include_reason_traceability_share,
            "review": review_reason_traceability_share,
            "overall": screening_reason_traceability_share,
        }},
        {"label": "review_bridge_counterexample_coupling", "value": {
            "coupled_rows": review_bridge_counterexample_coupled_rows,
            "coupled_share": review_bridge_counterexample_coupled_share,
            "traceable_coupled_rows": review_bridge_counterexample_traceable_coupled_rows,
            "traceable_coupled_share": review_bridge_counterexample_traceable_coupled_share,
            "counterexample_without_bridge_rows": review_counterexample_without_bridge_rows,
            "counterexample_without_bridge_share": review_counterexample_without_bridge_share,
            "weak_evidence_rows": review_weak_evidence_rows,
            "weak_evidence_share": review_weak_evidence_share,
        }},
        {"label": "manual_qc_year_distribution", "value": top_items(manual_qc_year_counts, limit=8)},
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
            "include_count": include_count,
            "review_count": review_count,
            "exclude_count": int(labels.get("exclude", 0) or 0),
            "manual_qc_rows": len(manual_qc_rows),
            "single_source_only": single_source_only,
            "single_source_share": pct(single_source_only, deduped_records),
            "low_confidence_count": low_confidence_count,
            "low_confidence_share": pct(low_confidence_count, deduped_records),
            "zero_hit_terms": zero_hit_terms,
            "gate_failures_near_threshold": gate_failures_near_threshold,
            "query_drift_candidate_count": query_drift_candidate_count,
            "balanced_label_bins": nonzero_label_bins,
            "balanced_confidence_bins": nonzero_confidence_bins,
            "balanced_group_bins": nonzero_group_bins,
            "balanced_label_dominance": max_balanced_label_share,
            "balanced_include_rows": balanced_include_rows,
            "balanced_review_rows": balanced_review_rows,
            "balanced_min_per_label_target": balanced_min_per_label_target,
            "balanced_min_per_label_missing": balanced_min_per_label_missing,
            "risk_reason_diversity": risk_reason_diversity,
            "top_risk_reason_share": top_risk_reason_share,
            "screening_reason_diversity": screening_reason_diversity,
            "top_screening_reason_share": top_screening_reason_share,
            "screening_reason_entropy": screening_reason_entropy,
            "manual_qc_query_entropy": manual_qc_query_entropy,
            "manual_qc_review_query_entropy": manual_qc_review_query_entropy,
            "manual_qc_review_traceable_known_query_rows": review_traceable_known_query_rows,
            "manual_qc_review_traceable_known_query_share": manual_qc_review_traceable_known_query_share,
            "manual_qc_review_traceable_unknown_query_rows": review_traceable_unknown_query_rows,
            "manual_qc_review_traceable_unknown_query_share": manual_qc_review_traceable_unknown_query_share,
            "manual_qc_review_query_traceability_share": manual_qc_review_query_traceability_share,
            "manual_qc_review_traceable_known_query_entropy": manual_qc_review_traceable_known_query_entropy,
            "manual_qc_review_traceable_known_query_coverage": manual_qc_review_traceable_known_query_coverage,
            "manual_qc_review_traceable_known_query_hhi": manual_qc_review_traceable_known_query_hhi,
            "manual_qc_review_traceable_known_query_top_share": manual_qc_review_traceable_known_query_top_share,
            "manual_qc_review_traceable_known_query_top2_share": manual_qc_review_traceable_known_query_top2_share,
            "manual_qc_review_traceable_known_query_top3_share": manual_qc_review_traceable_known_query_top3_share,
            "manual_qc_review_traceable_known_query_js_divergence": manual_qc_review_traceable_known_query_js_divergence,
            "manual_qc_review_traceable_known_query_tail_share": manual_qc_review_traceable_known_query_tail_share,
            "manual_qc_review_traceable_known_query_effective_count": manual_qc_review_traceable_known_query_effective_count,
            "manual_qc_review_traceable_known_query_bottom_share": manual_qc_review_traceable_known_query_bottom_share,
            "manual_qc_review_traceable_known_query_bottom2_share": manual_qc_review_traceable_known_query_bottom2_share,
            "manual_qc_review_traceable_known_query_top_bottom_gap": manual_qc_review_traceable_known_query_top_bottom_gap,
            "manual_qc_review_traceable_known_query_group_entropy": manual_qc_review_traceable_known_query_group_entropy,
            "manual_qc_review_traceable_known_query_group_coverage": manual_qc_review_traceable_known_query_group_coverage,
            "manual_qc_review_traceable_known_query_group_top_share": manual_qc_review_traceable_known_query_group_top_share,
            "manual_qc_review_traceable_known_query_group_top2_share": manual_qc_review_traceable_known_query_group_top2_share,
            "manual_qc_review_traceable_known_query_group_tail_share": manual_qc_review_traceable_known_query_group_tail_share,
            "manual_qc_review_traceable_known_query_group_js_divergence": manual_qc_review_traceable_known_query_group_js_divergence,
            "manual_qc_review_traceable_known_query_unknown_group_share": manual_qc_review_traceable_known_query_unknown_group_share,
            "manual_qc_review_traceable_known_query_year_js_divergence": manual_qc_review_traceable_known_query_year_js_divergence,
            "manual_qc_risk_reason_entropy": manual_qc_risk_reason_entropy,
            "manual_qc_review_reason_entropy": manual_qc_review_reason_entropy,
            "review_to_include_ratio": review_to_include_ratio,
            "manual_qc_include_rows": manual_qc_include_rows,
            "manual_qc_review_rows": manual_qc_review_rows,
            "manual_qc_review_share": manual_qc_review_share,
            "manual_qc_review_confidence_bins": manual_qc_review_confidence_bins,
            "manual_qc_review_confidence_entropy": manual_qc_review_confidence_entropy,
            "traceable_reason_rows": traceable_reason_rows,
            "screening_reason_traceability_share": screening_reason_traceability_share,
            "include_traceable_reason_rows": include_traceable_reason_rows,
            "include_reason_traceability_share": include_reason_traceability_share,
            "review_traceable_reason_rows": review_traceable_reason_rows,
            "review_reason_traceability_share": review_reason_traceability_share,
            "include_bridge_signal_rows": include_bridge_signal_rows,
            "include_bridge_signal_share": include_bridge_signal_share,
            "review_bridge_signal_rows": review_bridge_signal_rows,
            "review_bridge_signal_share": review_bridge_signal_share,
            "review_bridge_traceable_rows": review_bridge_traceable_rows,
            "review_bridge_traceability_share": review_bridge_traceability_share,
            "review_bridge_traceability_given_bridge_share": review_bridge_traceability_given_bridge_share,
            "review_bridge_traceable_known_query_rows": review_bridge_traceable_known_query_rows,
            "review_bridge_traceable_known_query_share": review_bridge_traceable_known_query_share,
            "review_bridge_traceable_unknown_query_rows": review_bridge_traceable_unknown_query_rows,
            "review_bridge_traceable_unknown_query_share": review_bridge_traceable_unknown_query_share,
            "review_counterexample_rows": review_counterexample_rows,
            "review_counterexample_share": review_counterexample_share,
            "review_counterexample_traceable_rows": review_counterexample_traceable_rows,
            "review_counterexample_traceability_share": review_counterexample_traceability_share,
            "review_bridge_counterexample_coupled_rows": review_bridge_counterexample_coupled_rows,
            "review_bridge_counterexample_coupled_share": review_bridge_counterexample_coupled_share,
            "review_bridge_counterexample_traceable_coupled_rows": review_bridge_counterexample_traceable_coupled_rows,
            "review_bridge_counterexample_traceable_coupled_share": review_bridge_counterexample_traceable_coupled_share,
            "review_bridge_counterexample_traceability_given_coupled_share": review_bridge_counterexample_traceability_given_coupled_share,
            "review_bridge_counterexample_traceability_gap_share": review_bridge_counterexample_traceability_gap_share,
            "review_counterexample_without_bridge_rows": review_counterexample_without_bridge_rows,
            "review_counterexample_without_bridge_share": review_counterexample_without_bridge_share,
            "review_evidence_link_decay_rows": review_evidence_link_decay_rows,
            "review_evidence_link_decay_share": review_evidence_link_decay_share,
            "manual_qc_bridge_signal_rows": bridge_signal_rows,
            "manual_qc_bridge_signal_share": manual_qc_bridge_signal_share,
            "manual_qc_review_confidence_counts": review_confidence_counts,
            "manual_qc_label_counts": manual_qc_label_counts,
            "manual_qc_source_group_diversity": manual_qc_source_group_diversity,
            "manual_qc_source_group_counts": manual_qc_source_group_counts,
            "manual_qc_single_query_share": manual_qc_single_query_share,
            "manual_qc_source_query_counts": manual_qc_source_query_counts,
            "manual_qc_review_source_query_counts": manual_qc_review_source_query_counts,
            "manual_qc_review_source_group_diversity": manual_qc_review_source_group_diversity,
            "manual_qc_review_source_group_counts": manual_qc_review_source_group_counts,
            "manual_qc_review_group_dominance": manual_qc_review_group_dominance,
            "manual_qc_unknown_query_share": manual_qc_unknown_query_share,
            "manual_qc_year_diversity": manual_qc_year_diversity,
            "manual_qc_single_year_share": manual_qc_single_year_share,
            "manual_qc_year_entropy": manual_qc_year_entropy,
            "manual_qc_year_counts": manual_qc_year_counts,
            "manual_qc_dedup_label_conflict_rows": dedup_label_conflict_rows,
            "manual_qc_dedup_label_conflict_share": manual_qc_dedup_label_conflict_share,
            "manual_qc_dedup_score_range_alert_rows": dedup_score_range_alert_rows,
            "manual_qc_dedup_score_range_alert_share": manual_qc_dedup_score_range_alert_share,
            "manual_qc_duplicate_title_rows": duplicate_title_rows,
            "manual_qc_duplicate_title_share": manual_qc_duplicate_title_share,
            "empty_screening_reason_rows": empty_screening_reason_rows,
            "empty_screening_reason_share": empty_screening_reason_share,
            "manual_qc_label_dominance": manual_qc_label_dominance,
            "manual_qc_high_risk_rows": high_risk_qc_rows,
            "manual_qc_high_risk_share": manual_qc_high_risk_share,
            "review_weak_evidence_rows": review_weak_evidence_rows,
            "review_weak_evidence_share": review_weak_evidence_share,
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
