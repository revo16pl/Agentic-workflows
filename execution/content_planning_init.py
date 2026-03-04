#!/usr/bin/env python3
"""Initialize a bi-weekly content planning sprint workspace."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANNING_ROOT = PROJECT_ROOT / "Agentic Articles" / "planning"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize content planning sprint folder.")
    parser.add_argument("--sprint-date", default=dt.date.today().isoformat(), help="Sprint date (YYYY-MM-DD).")
    parser.add_argument("--companies", required=True, help='Comma separated companies, e.g. "studio balans,druga firma".')
    parser.add_argument("--planning-root", type=Path, default=DEFAULT_PLANNING_ROOT)
    parser.add_argument("--force", action="store_true", help="Overwrite existing template files.")
    return parser.parse_args()


def write_text(path: Path, content: str, force: bool = False) -> None:
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def write_csv(path: Path, headers: list[str], force: bool = False) -> None:
    if path.exists() and not force:
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()


def main() -> int:
    args = parse_args()
    companies = [item.strip() for item in args.companies.split(",") if item.strip()]
    if not companies:
        print("ERROR: provide at least one company in --companies")
        return 1

    sprint_dir = args.planning_root / f"{args.sprint_date}_sprint"
    research_inputs = sprint_dir / "research_inputs"
    templates_dir = research_inputs / "templates"

    sprint_dir.mkdir(parents=True, exist_ok=True)
    research_inputs.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)

    planning_brief = (
        "# planning_brief.md\n\n"
        "## Sprint metadata\n"
        f"- sprint_date: {args.sprint_date}\n"
        "- cadence: bi-weekly\n"
        f"- companies: {', '.join(companies)}\n"
        "- owner: \n"
        "- target_articles_per_company: 4\n"
        "\n"
        "## Business priorities\n"
        "- Priority services this sprint:\n"
        "- Main KPI (lead_gen / traffic / authority):\n"
        "- Priority locations:\n"
        "\n"
        "## Data collection checklist\n"
        "- [ ] Keyword Planner export per company\n"
        "- [ ] SERP top10 snapshot for at least 3 seed queries per company\n"
        "- [ ] PAA questions export\n"
        "- [ ] Google Trends snapshot (12m)\n"
        "\n"
        "## Notes\n"
        "- This sprint uses free-first, manual data exports only.\n"
    )
    write_text(sprint_dir / "planning_brief.md", planning_brief, force=args.force)

    write_csv(
        templates_dir / "keywords_template.csv",
        ["company", "keyword", "avg_monthly_searches", "competition", "source"],
        force=args.force,
    )
    write_csv(
        templates_dir / "serp_template.csv",
        ["company", "query", "rank", "title", "url", "snippet", "domain", "source_tool"],
        force=args.force,
    )
    write_csv(
        templates_dir / "paa_template.csv",
        ["company", "query", "question", "source_tool"],
        force=args.force,
    )
    write_csv(
        templates_dir / "trends_template.csv",
        ["company", "query", "period", "value", "source_tool"],
        force=args.force,
    )

    write_csv(
        sprint_dir / "content_plan_candidates.csv",
        [
            "topic_id",
            "company",
            "topic_cluster_name",
            "article_title_working",
            "primary_keyword",
            "secondary_keywords",
            "avg_monthly_searches_sum",
            "intent",
            "trend_direction",
            "serp_competition_level",
            "content_gap_note",
            "demand_score",
            "intent_fit_score",
            "business_fit_score",
            "priority_score",
            "recommended_length_min",
            "recommended_length_max",
            "target_service_url",
            "cta_type",
            "status",
        ],
        force=args.force,
    )
    write_csv(
        sprint_dir / "content_plan_backlog.csv",
        [
            "topic_id",
            "company",
            "topic_cluster_name",
            "article_title_working",
            "primary_keyword",
            "secondary_keywords",
            "avg_monthly_searches_sum",
            "intent",
            "trend_direction",
            "serp_competition_level",
            "content_gap_note",
            "demand_score",
            "intent_fit_score",
            "business_fit_score",
            "priority_score",
            "recommended_length_min",
            "recommended_length_max",
            "target_service_url",
            "cta_type",
            "status",
        ],
        force=args.force,
    )
    write_csv(
        sprint_dir / "run_queue.csv",
        [
            "queue_row_id",
            "topic_id",
            "company",
            "topic_cluster_name",
            "article_title_working",
            "primary_keyword",
            "target_length_words",
            "intent",
            "target_service_url",
            "cta_type",
            "workflow_b_ready",
            "reason_if_no",
            "source_sprint",
        ],
        force=args.force,
    )

    gate_payload = {
        "version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "keyword_dataset_pass": False,
        "serp_dataset_pass": False,
        "paa_dataset_pass": False,
        "trends_dataset_pass": False,
        "cluster_quality_pass": False,
        "backlog_minimum_pass": False,
        "planning_hard_block_pass": False,
        "metrics": {
            "companies": companies,
            "per_company": {},
            "global": {},
        },
    }
    write_text(
        sprint_dir / "planning_gate.json",
        json.dumps(gate_payload, ensure_ascii=False, indent=2) + "\n",
        force=args.force,
    )
    write_text(
        sprint_dir / "content_plan_report.md",
        "# content_plan_report.md\n\nRun `content_planning_gate.py` to generate this report.\n",
        force=args.force,
    )

    print(json.dumps({"ok": True, "sprint_dir": str(sprint_dir), "companies": companies}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
