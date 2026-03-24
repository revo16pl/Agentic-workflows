#!/usr/bin/env python3
"""Compute strict quality gates for content planning sprint."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


THRESHOLDS = {
    "keywords_min_per_company": 60,
    "serp_min_per_company": 30,
    "serp_unique_domains_min": 8,
    "paa_min_per_company": 10,
    "trends_min_queries_per_company": 5,
    "approved_min_per_company": 4,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate planning quality hard gates.")
    parser.add_argument("--sprint", type=Path, required=True, help="Planning sprint path.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def normalize_company(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def bool_pass(flag: bool) -> str:
    return "PASS" if flag else "FAIL"


def main() -> int:
    args = parse_args()
    sprint = args.sprint.resolve()
    dataset_path = sprint / "planning_dataset.json"
    backlog_path = sprint / "content_plan_backlog.csv"
    candidates_path = sprint / "content_plan_candidates.csv"

    if not dataset_path.exists():
        print(f"ERROR: missing dataset: {dataset_path}")
        return 1

    payload = load_json(dataset_path)
    backlog = load_csv(backlog_path)
    candidates = load_csv(candidates_path)

    keywords = payload.get("keywords", []) if isinstance(payload.get("keywords"), list) else []
    serp = payload.get("serp_results", []) if isinstance(payload.get("serp_results"), list) else []
    paa = payload.get("paa_questions", []) if isinstance(payload.get("paa_questions"), list) else []
    trends = payload.get("trend_points", []) if isinstance(payload.get("trend_points"), list) else []

    companies = sorted(
        {
            normalize_company(str(r.get("company", "")))
            for r in keywords + serp + paa + trends
            if normalize_company(str(r.get("company", "")))
        }
    )

    per_company: dict[str, dict[str, Any]] = {}

    keyword_dataset_ok = True
    serp_dataset_ok = True
    paa_dataset_ok = True
    trends_dataset_ok = True
    backlog_min_ok = True

    for company in companies:
        company_keywords = [r for r in keywords if normalize_company(str(r.get("company", ""))) == company]
        company_serp = [r for r in serp if normalize_company(str(r.get("company", ""))) == company]
        company_paa = [r for r in paa if normalize_company(str(r.get("company", ""))) == company]
        company_trends = [r for r in trends if normalize_company(str(r.get("company", ""))) == company]
        company_backlog = [r for r in backlog if normalize_company(str(r.get("company", ""))) == company]

        keyword_with_volume = [r for r in company_keywords if int(r.get("avg_monthly_searches", 0) or 0) > 0]
        serp_domains = {
            str(r.get("domain", "")).strip().lower()
            for r in company_serp
            if str(r.get("domain", "")).strip()
        }
        trend_queries = {
            str(r.get("query", "")).strip().lower()
            for r in company_trends
            if str(r.get("query", "")).strip()
        }

        company_keyword_ok = len(keyword_with_volume) >= THRESHOLDS["keywords_min_per_company"]
        company_serp_ok = len(company_serp) >= THRESHOLDS["serp_min_per_company"] and len(serp_domains) >= THRESHOLDS["serp_unique_domains_min"]
        company_paa_ok = len(company_paa) >= THRESHOLDS["paa_min_per_company"]
        company_trends_ok = len(trend_queries) >= THRESHOLDS["trends_min_queries_per_company"]
        company_backlog_ok = len(company_backlog) >= THRESHOLDS["approved_min_per_company"]

        keyword_dataset_ok = keyword_dataset_ok and company_keyword_ok
        serp_dataset_ok = serp_dataset_ok and company_serp_ok
        paa_dataset_ok = paa_dataset_ok and company_paa_ok
        trends_dataset_ok = trends_dataset_ok and company_trends_ok
        backlog_min_ok = backlog_min_ok and company_backlog_ok

        per_company[company] = {
            "keyword_rows_with_volume": len(keyword_with_volume),
            "serp_rows": len(company_serp),
            "serp_unique_domains": len(serp_domains),
            "paa_rows": len(company_paa),
            "trend_queries": len(trend_queries),
            "approved_topics": len(company_backlog),
            "keyword_dataset_pass": company_keyword_ok,
            "serp_dataset_pass": company_serp_ok,
            "paa_dataset_pass": company_paa_ok,
            "trends_dataset_pass": company_trends_ok,
            "backlog_minimum_pass": company_backlog_ok,
        }

    cluster_quality_ok = True
    for row in backlog:
        secondary = [x.strip() for x in str(row.get("secondary_keywords", "")).split("|") if x.strip()]
        required = all(
            [
                str(row.get("primary_keyword", "")).strip(),
                str(row.get("intent", "")).strip(),
                str(row.get("target_service_url", "")).strip(),
                str(row.get("cta_type", "")).strip(),
            ]
        )
        if not required or len(secondary) < 8:
            cluster_quality_ok = False
            break

    gates = {
        "keyword_dataset_pass": keyword_dataset_ok,
        "serp_dataset_pass": serp_dataset_ok,
        "paa_dataset_pass": paa_dataset_ok,
        "trends_dataset_pass": trends_dataset_ok,
        "cluster_quality_pass": cluster_quality_ok,
        "backlog_minimum_pass": backlog_min_ok,
    }
    gates["planning_hard_block_pass"] = all(gates.values())

    output = {
        "version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        **gates,
        "metrics": {
            "thresholds": THRESHOLDS,
            "companies": companies,
            "per_company": per_company,
            "global": {
                "candidate_topics": len(candidates),
                "approved_topics": len(backlog),
                "keyword_rows": len(keywords),
                "serp_rows": len(serp),
                "paa_rows": len(paa),
                "trend_rows": len(trends),
            },
        },
    }

    gate_path = sprint / "planning_gate.json"
    gate_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_lines = [
        "# content_plan_report.md",
        "",
        "## Planning hard gates",
        *(f"- {name}: {bool_pass(flag)}" for name, flag in gates.items()),
        "",
        "## Global metrics",
        f"- candidate_topics: {output['metrics']['global']['candidate_topics']}",
        f"- approved_topics: {output['metrics']['global']['approved_topics']}",
        f"- keyword_rows: {output['metrics']['global']['keyword_rows']}",
        f"- serp_rows: {output['metrics']['global']['serp_rows']}",
        f"- paa_rows: {output['metrics']['global']['paa_rows']}",
        f"- trend_rows: {output['metrics']['global']['trend_rows']}",
        "",
        "## Per-company metrics",
    ]
    for company, metrics in per_company.items():
        report_lines.extend(
            [
                f"### {company}",
                f"- keyword_rows_with_volume: {metrics['keyword_rows_with_volume']}",
                f"- serp_rows: {metrics['serp_rows']} (unique domains: {metrics['serp_unique_domains']})",
                f"- paa_rows: {metrics['paa_rows']}",
                f"- trend_queries: {metrics['trend_queries']}",
                f"- approved_topics: {metrics['approved_topics']}",
                f"- keyword_dataset_pass: {bool_pass(metrics['keyword_dataset_pass'])}",
                f"- serp_dataset_pass: {bool_pass(metrics['serp_dataset_pass'])}",
                f"- paa_dataset_pass: {bool_pass(metrics['paa_dataset_pass'])}",
                f"- trends_dataset_pass: {bool_pass(metrics['trends_dataset_pass'])}",
                f"- backlog_minimum_pass: {bool_pass(metrics['backlog_minimum_pass'])}",
                "",
            ]
        )

    (sprint / "content_plan_report.md").write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8")

    print(json.dumps({"ok": gates["planning_hard_block_pass"], "planning_gate": str(gate_path), "gates": gates}, ensure_ascii=False, indent=2))
    return 0 if gates["planning_hard_block_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
