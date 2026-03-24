#!/usr/bin/env python3
"""Research dataset quality gates for Agentic Articles v3."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from article_workflow_state import set_gate, set_many_gates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check v3 research quality gates.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--manifest", default="research_evidence_manifest.json")
    parser.add_argument("--report", default="research_quality_report.md")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _all_pulled_at(payload: dict[str, Any]) -> list[datetime]:
    values: list[datetime] = []

    def collect(items: Any) -> None:
        if not isinstance(items, list):
            return
        for item in items:
            if isinstance(item, dict):
                raw = str(item.get("pulled_at", "")).strip()
                if raw:
                    parsed = _parse_iso(raw)
                    if parsed:
                        values.append(parsed.astimezone(timezone.utc))

    collect(payload.get("keyword_metrics", []))
    collect(payload.get("serp_results", []))
    collect(payload.get("paa_questions", []))
    collect(payload.get("trend_points", []))
    collect(payload.get("sources", []))
    return values


def _domain(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).netloc or "").lower()


def evaluate(payload: dict[str, Any]) -> tuple[dict[str, bool], dict[str, Any]]:
    keyword_metrics = payload.get("keyword_metrics", []) if isinstance(payload.get("keyword_metrics"), list) else []
    serp_results = payload.get("serp_results", []) if isinstance(payload.get("serp_results"), list) else []
    trend_points = payload.get("trend_points", []) if isinstance(payload.get("trend_points"), list) else []
    competitor_matrix = payload.get("competitor_matrix", []) if isinstance(payload.get("competitor_matrix"), list) else []
    content_gaps = payload.get("content_gaps", []) if isinstance(payload.get("content_gaps"), list) else []

    minimum = payload.get("minimum_dataset", {}) if isinstance(payload.get("minimum_dataset"), dict) else {}

    def min_value(key: str, default: int) -> int:
        raw = minimum.get(key, default)
        try:
            return int(raw)
        except (TypeError, ValueError):
            return default

    required_keyword_metrics = min_value("keyword_metrics", 40)
    required_serp_results = min_value("serp_results", min_value("serp_top10_urls", 30))
    required_trend_queries = min_value("trend_queries", 5)
    required_points_per_trend_query = min_value("trend_points_per_query", 12)
    required_competitor_matrix = min_value("competitor_matrix", 10)
    required_content_gaps = min_value("content_gaps", 5)
    required_serp_domains = min_value("serp_unique_domains", 8)
    required_keyword_numeric_ratio = float(minimum.get("keyword_numeric_ratio", 0.80))
    freshness_days = min_value("freshness_days", 7)
    providers_status = payload.get("providers_status", {}) if isinstance(payload.get("providers_status"), dict) else {}
    keyword_provider_status = str(providers_status.get("keyword_metrics", "ok")).strip().lower()
    trend_provider_status = str(providers_status.get("trends", "ok")).strip().lower()
    effective_keyword_numeric_ratio = required_keyword_numeric_ratio
    if keyword_provider_status in {"fallback", "failed"}:
        effective_keyword_numeric_ratio = 0.0

    numeric_keyword_count = 0
    for row in keyword_metrics:
        if not isinstance(row, dict):
            continue
        val = row.get("avg_monthly_searches")
        if isinstance(val, (int, float)):
            numeric_keyword_count += 1

    total_keywords = len(keyword_metrics)
    numeric_ratio = (numeric_keyword_count / total_keywords) if total_keywords else 0.0

    unique_domains = len({_domain(str(x.get("url", ""))) for x in serp_results if isinstance(x, dict) and x.get("url")})

    trend_queries = {}
    for row in trend_points:
        if not isinstance(row, dict):
            continue
        q = str(row.get("query", "")).strip()
        if not q:
            continue
        trend_queries[q] = trend_queries.get(q, 0) + 1

    trend_queries_legacy = payload.get("trend_queries", []) if isinstance(payload.get("trend_queries"), list) else []
    legacy_count = len([x for x in trend_queries_legacy if str(x).strip()])
    trend_query_count = max(len(trend_queries), legacy_count)
    min_points_per_query = min(trend_queries.values()) if trend_queries else 0
    effective_points_per_query = required_points_per_trend_query
    if trend_provider_status in {"fallback", "failed"}:
        effective_points_per_query = 0

    matrix_gaps: set[str] = set(str(x).strip() for x in content_gaps if str(x).strip())
    for row in competitor_matrix:
        if not isinstance(row, dict):
            continue
        for gap in row.get("content_gaps", []) if isinstance(row.get("content_gaps"), list) else []:
            if str(gap).strip():
                matrix_gaps.add(str(gap).strip())

    now = datetime.now(timezone.utc)
    pulled_at_values = _all_pulled_at(payload)
    freshness_ok = bool(pulled_at_values) and all(now - dt <= timedelta(days=freshness_days) for dt in pulled_at_values)

    gates = {
        "keyword_metrics_coverage_pass": total_keywords >= required_keyword_metrics and numeric_ratio >= effective_keyword_numeric_ratio,
        "serp_dataset_quality_pass": len(serp_results) >= required_serp_results and unique_domains >= required_serp_domains,
        "trends_dataset_quality_pass": trend_query_count >= required_trend_queries and min_points_per_query >= effective_points_per_query,
        "competitor_matrix_pass": len(competitor_matrix) >= required_competitor_matrix and len(matrix_gaps) >= required_content_gaps,
        "research_data_freshness_pass": freshness_ok,
    }
    gates["research_hard_block_pass"] = all(gates.values())

    metrics = {
        "keyword_metrics_count": total_keywords,
        "keyword_numeric_ratio": round(numeric_ratio, 4),
        "serp_results_count": len(serp_results),
        "serp_unique_domains": unique_domains,
        "trend_query_count": trend_query_count,
        "trend_min_points_per_query": min_points_per_query,
        "competitor_matrix_count": len(competitor_matrix),
        "content_gaps_count": len(matrix_gaps),
        "freshness_days_threshold": freshness_days,
        "pulled_at_values_count": len(pulled_at_values),
        "required_keyword_metrics": required_keyword_metrics,
        "required_keyword_numeric_ratio": required_keyword_numeric_ratio,
        "effective_keyword_numeric_ratio": effective_keyword_numeric_ratio,
        "keyword_provider_status": keyword_provider_status,
        "required_serp_results": required_serp_results,
        "required_serp_domains": required_serp_domains,
        "required_trend_queries": required_trend_queries,
        "required_points_per_trend_query": required_points_per_trend_query,
        "effective_points_per_trend_query": effective_points_per_query,
        "trend_provider_status": trend_provider_status,
        "required_competitor_matrix": required_competitor_matrix,
        "required_content_gaps": required_content_gaps,
    }
    return gates, metrics


def write_report(path: Path, gates: dict[str, bool], metrics: dict[str, Any]) -> None:
    lines = ["# research_quality_report.md", "", "## Gates"]
    lines.extend([f"- {name}: {'PASS' if passed else 'FAIL'}" for name, passed in gates.items()])
    lines.extend(["", "## Metrics"])
    lines.extend([f"- {name}: {value}" for name, value in metrics.items()])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    manifest_path = workspace / args.manifest
    if not manifest_path.exists():
        print(f"ERROR: Missing manifest: {manifest_path}")
        return 1

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {manifest_path}: {exc}")
        return 1

    if not isinstance(payload, dict):
        print(f"ERROR: {manifest_path} must contain JSON object")
        return 1

    gates, metrics = evaluate(payload)

    set_many_gates(
        workspace=workspace,
        gates={
            "keyword_metrics_coverage_pass": gates["keyword_metrics_coverage_pass"],
            "serp_dataset_quality_pass": gates["serp_dataset_quality_pass"],
            "trends_dataset_quality_pass": gates["trends_dataset_quality_pass"],
            "competitor_matrix_pass": gates["competitor_matrix_pass"],
            "research_data_freshness_pass": gates["research_data_freshness_pass"],
        },
        source="check_research_quality.py",
        severity="hard",
        details={
            "keyword_metrics_coverage_pass": (
                f"count={metrics['keyword_metrics_count']}, "
                f"numeric_ratio={metrics['keyword_numeric_ratio']}, "
                f"required_numeric_ratio={metrics['effective_keyword_numeric_ratio']}, "
                f"provider_status={metrics['keyword_provider_status']}"
            ),
            "serp_dataset_quality_pass": f"serp_results={metrics['serp_results_count']}, unique_domains={metrics['serp_unique_domains']}",
            "trends_dataset_quality_pass": (
                f"queries={metrics['trend_query_count']}, "
                f"min_points={metrics['trend_min_points_per_query']}, "
                f"required_points={metrics['effective_points_per_trend_query']}, "
                f"provider_status={metrics['trend_provider_status']}"
            ),
            "competitor_matrix_pass": f"rows={metrics['competitor_matrix_count']}, gaps={metrics['content_gaps_count']}",
            "research_data_freshness_pass": f"pulled_at_values={metrics['pulled_at_values_count']}, threshold_days={metrics['freshness_days_threshold']}",
        },
    )
    set_gate(
        workspace=workspace,
        name="research_hard_block_pass",
        passed=gates["research_hard_block_pass"],
        source="check_research_quality.py",
        severity="hard",
        details="Derived from all v3 research hard gates.",
    )

    report_path = workspace / args.report
    write_report(report_path, gates, metrics)

    output = {"ok": gates["research_hard_block_pass"], "gates": gates, "metrics": metrics, "report_path": str(report_path)}
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"Research quality report: {report_path}")
        for name, passed in gates.items():
            print(f"- {name}: {'PASS' if passed else 'FAIL'}")

    return 0 if gates["research_hard_block_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
