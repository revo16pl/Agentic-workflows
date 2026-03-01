#!/usr/bin/env python3
"""
Create a workspace for one article run in Agentic Articles workflow.

Usage:
    python3 execution/article_workflow_init.py \
      --topic "Zalety treningu EMS w Niepolomicach" \
      --company "studio balans"
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKSPACE_ROOT = PROJECT_ROOT / "Agentic Articles" / "workspace"
DEFAULT_DOCS_ROOT = PROJECT_ROOT / "Agentic Articles" / "docs"

REQUIRED_ARTIFACTS = [
    "article_brief.md",
    "article_research_pack.md",
    "research_evidence_manifest.json",
    "quality_gate.json",
    "article_draft_v1.md",
    "qa_report.md",
    "article_draft_v2.md",
    "publish_ready.md",
]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return slug or "article"


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")


def ensure_run_context_defaults(path: Path, topic: str, company: str) -> None:
    """Backfill required v3.0 fields without overwriting existing run context."""
    defaults = {
        "topic": topic,
        "company": company,
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "workflow_version": "v3.0",
        "data_mode": "external_only",
        "skills_required": "content-strategy, copywriting, copy-editing, seo-audit, schema-markup, ai-seo",
        "skills_loaded": "",
        "skills_applied": "",
        "research_providers_loaded": "",
        "research_fetch_started_at": "",
        "research_fetch_finished_at": "",
        "research_fetch_status": "",
    }

    if not path.exists():
        lines = ["# run_context.md", ""]
        lines.extend([f"- {key}: {value}" for key, value in defaults.items()])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    existing = path.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    lines = existing.splitlines()
    for raw in lines:
        line = raw.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        values[key.strip()] = value.strip()

    changed = False
    for key, value in defaults.items():
        if key not in values:
            lines.append(f"- {key}: {value}")
            changed = True

    # Always upgrade workflow version marker when missing/legacy.
    if values.get("workflow_version", "").strip() in {"", "v1", "v2.1"}:
        updated_lines: list[str] = []
        replaced = False
        for raw in lines:
            if raw.strip().startswith("- workflow_version:"):
                updated_lines.append("- workflow_version: v3.0")
                replaced = True
                changed = True
            else:
                updated_lines.append(raw)
        if not replaced:
            updated_lines.append("- workflow_version: v3.0")
            changed = True
        lines = updated_lines

    if changed:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def template_for(filename: str, topic: str, company: str, today: str) -> str:
    if filename == "article_research_pack.md":
        return (
            "# article_research_pack.md\n\n"
            "## Topic\n"
            f"- {topic}\n\n"
            "## 1) Intent Map\n"
            "- Dominant intent:\n"
            "- Secondary intent:\n"
            "- Intent-fit hypothesis:\n\n"
            "## 2) SERP Snapshot (Top 10)\n"
            "| # | URL | Title | Intent | Format | Notes |\n"
            "|---|---|---|---|---|---|\n"
            "| 1 |  |  |  |  |  |\n"
            "| 2 |  |  |  |  |  |\n"
            "| 3 |  |  |  |  |  |\n"
            "| 4 |  |  |  |  |  |\n"
            "| 5 |  |  |  |  |  |\n"
            "| 6 |  |  |  |  |  |\n"
            "| 7 |  |  |  |  |  |\n"
            "| 8 |  |  |  |  |  |\n"
            "| 9 |  |  |  |  |  |\n"
            "| 10 |  |  |  |  |  |\n\n"
            "## 3) Content Gaps\n"
            "1.\n"
            "2.\n"
            "3.\n"
            "4.\n"
            "5.\n\n"
            "## 3b) Evidence Contract (required)\n"
            "| Insight | source_tool | query_seed | url | date_range | pulled_at | locale | country | device | confidence |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "|  |  |  |  |  |  | pl-PL | PL | desktop |  |\n\n"
            "## 4) Fact Bank\n"
            "| Teza | Dowod | URL | Data publikacji/aktualizacji |\n"
            "|---|---|---|---|\n"
            "|  |  |  |  |\n\n"
            "## 5) Keyword Cluster\n"
            "- Primary keyword:\n"
            "- Secondary keywords (min 30):\n"
            "- Entities:\n"
            "- PAA questions (min 10):\n"
            "- Trend queries (min 5):\n\n"
            "## 6) Article Blueprint\n"
            "### H1\n"
            "- \n\n"
            "### Outline (H2/H3 + section goal + word budget)\n"
            "1.\n\n"
            "### Internal linking plan\n"
            "- \n\n"
            "### Schema recommendation\n"
            "- \n\n"
            "### Answer-first blocks\n"
            "- \n"
        )

    if filename == "research_evidence_manifest.json":
        return (
            "{\n"
            '  "version": "3.0",\n'
            '  "data_mode": "external_only",\n'
            f'  "topic": {json_string(topic)},\n'
            f'  "company": {json_string(company)},\n'
            f'  "generated_at": {json_string(today)},\n'
            '  "providers": {\n'
            '    "keyword_metrics": "google_ads_keyword_planner_api",\n'
            '    "serp": "serper",\n'
            '    "serp_fallback": "serpapi",\n'
            '    "trends": "pytrends"\n'
            "  },\n"
            '  "query_seeds": [],\n'
            '  "minimum_dataset": {\n'
            '    "serp_top10_urls": 10,\n'
            '    "keyword_phrases": 30,\n'
            '    "paa_questions": 10,\n'
            '    "trend_queries": 5,\n'
            '    "keyword_metrics": 40,\n'
            '    "serp_results": 30,\n'
            '    "competitor_matrix": 10\n'
            "  },\n"
            '  "keyword_metrics": [],\n'
            '  "serp_results": [],\n'
            '  "trend_points": [],\n'
            '  "competitor_matrix": [],\n'
            '  "content_gaps": [],\n'
            '  "serp_urls": [],\n'
            '  "keyword_phrases": [],\n'
            '  "paa_questions": [],\n'
            '  "trend_queries": [],\n'
            '  "sources": []\n'
            "}\n"
        )

    if filename == "quality_gate.json":
        return (
            "{\n"
            '  "version": "3.0",\n'
            f'  "updated_at": {json_string(today)},\n'
            '  "overall_pass": false,\n'
            '  "hard_gates": [],\n'
            '  "gates": {}\n'
            "}\n"
        )

    if filename == "article_draft_v1.md":
        return "# article_draft_v1.md\n\n"

    if filename == "article_draft_v2.md":
        return "# article_draft_v2.md\n\n"

    if filename == "publish_ready.md":
        return (
            "# publish_ready.md\n\n"
            "status: Draft\n"
            f"company: {company}\n"
            f"topic: {topic}\n"
            f"review_date: {today}\n"
            "reviewer: \n"
            "notes: \n"
        )

    if filename == "qa_report.md":
        qa_template = DEFAULT_DOCS_ROOT / "article_qa_checklist.md"
        if qa_template.exists():
            return qa_template.read_text(encoding="utf-8")
        return "# qa_report.md\n\n"

    return f"# {filename}\n\n"


def json_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def create_workspace(
    topic: str,
    company: str,
    date_str: str,
    workspace_root: Path,
    docs_root: Path,
    force: bool,
) -> Path:
    workspace_root.mkdir(parents=True, exist_ok=True)
    slug = slugify(topic)
    workspace_dir = workspace_root / f"{date_str}_{slug}"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    brief_template = docs_root / "article_brief_template.md"
    brief_path = workspace_dir / "article_brief.md"
    if brief_template.exists():
        brief_content = brief_template.read_text(encoding="utf-8")
    else:
        brief_content = "# article_brief.md\n\n"
    write_text(brief_path, brief_content, force=force)

    for artifact in REQUIRED_ARTIFACTS:
        artifact_path = workspace_dir / artifact
        if artifact == "article_brief.md":
            continue
        content = template_for(artifact, topic=topic, company=company, today=date_str)
        write_text(artifact_path, content, force=force)

    run_context_path = workspace_dir / "run_context.md"
    if force:
        run_context_content = (
            "# run_context.md\n\n"
            f"- topic: {topic}\n"
            f"- company: {company}\n"
            f"- created_at: {dt.datetime.now().isoformat(timespec='seconds')}\n"
            "- workflow_version: v3.0\n"
            "- data_mode: external_only\n"
            "- skills_required: content-strategy, copywriting, copy-editing, seo-audit, schema-markup, ai-seo\n"
            "- skills_loaded: \n"
            "- skills_applied: \n"
            "- research_providers_loaded: \n"
            "- research_fetch_started_at: \n"
            "- research_fetch_finished_at: \n"
            "- research_fetch_status: \n"
        )
        write_text(run_context_path, run_context_content, force=True)
    else:
        ensure_run_context_defaults(run_context_path, topic=topic, company=company)
    return workspace_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize workspace for Agentic Articles workflow.",
    )
    parser.add_argument("--topic", required=True, help="Article topic.")
    parser.add_argument(
        "--company",
        required=True,
        help='Company in natural language, e.g. "studio balans".',
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Workspace date prefix (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=DEFAULT_WORKSPACE_ROOT,
        help='Default: "Agentic Articles/workspace".',
    )
    parser.add_argument(
        "--docs-root",
        type=Path,
        default=DEFAULT_DOCS_ROOT,
        help='Default: "Agentic Articles/docs".',
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing artifact files if present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        print("ERROR: --date must be in YYYY-MM-DD format.", file=sys.stderr)
        return 1

    workspace_dir = create_workspace(
        topic=args.topic.strip(),
        company=args.company.strip(),
        date_str=args.date,
        workspace_root=args.workspace_root.resolve(),
        docs_root=args.docs_root.resolve(),
        force=args.force,
    )

    print(f"Workspace ready: {workspace_dir}")
    print("Artifacts:")
    for name in REQUIRED_ARTIFACTS:
        print(f"- {workspace_dir / name}")
    print(f"- {workspace_dir / 'run_context.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
