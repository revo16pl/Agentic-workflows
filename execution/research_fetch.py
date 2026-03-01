#!/usr/bin/env python3
"""Fetch data-driven research artifacts for Agentic Articles v3."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from article_workflow_validate import parse_brief_metadata
from providers_google_ads import GoogleAdsProviderError, fetch_keyword_metrics
from providers_serp import SerpProviderError, fetch_serp_bundle
from providers_trends import TrendsProviderError, fetch_trends
from research_competitor_matrix import build_competitor_matrix


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch external research datasets (v3).")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--topic", default="")
    parser.add_argument("--company", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_env(project_root: Path) -> None:
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def read_brief(workspace: Path) -> dict[str, str]:
    brief_path = workspace / "article_brief.md"
    if not brief_path.exists():
        return {}
    return parse_brief_metadata(brief_path.read_text(encoding="utf-8"))


def update_run_context(workspace: Path, updates: dict[str, str]) -> None:
    path = workspace / "run_context.md"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else ["# run_context.md", ""]

    existing: dict[str, int] = {}
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if line.startswith("- ") and ":" in line:
            key = line[2:].split(":", 1)[0].strip()
            existing[key] = idx

    for key, value in updates.items():
        formatted = f"- {key}: {value}"
        if key in existing:
            lines[existing[key]] = formatted
        else:
            lines.append(formatted)

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def read_run_context(workspace: Path) -> dict[str, str]:
    path = workspace / "run_context.md"
    if not path.exists():
        return {}
    payload: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        payload[key.strip()] = value.strip()
    return payload


def google_suggest(query: str, locale: str = "pl-PL") -> list[str]:
    hl = locale.split("-")[0]
    response = requests.get(
        "https://suggestqueries.google.com/complete/search",
        params={"client": "firefox", "hl": hl, "q": query},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
        return [str(x).strip() for x in payload[1] if str(x).strip()]
    return []


def _topic_keywords(topic: str) -> list[str]:
    words = re.findall(r"\b[\w\-ąćęłńóśżźĄĆĘŁŃÓŚŻŹ]+\b", topic, flags=re.UNICODE)
    return words[:4]


def build_query_seeds(topic: str, city: str | None) -> list[dict[str, str]]:
    topic = topic.strip()
    base = [
        {"query": topic, "intent_hint": "core", "locale": "pl-PL", "geo": "PL"},
        {"query": f"{topic} efekty", "intent_hint": "problem", "locale": "pl-PL", "geo": "PL"},
        {
            "query": f"{topic} przeciwwskazania",
            "intent_hint": "risk",
            "locale": "pl-PL",
            "geo": "PL",
        },
    ]
    if city:
        base.append(
            {
                "query": f"{topic} {city}",
                "intent_hint": "local",
                "locale": "pl-PL",
                "geo": "PL",
            }
        )
    return base


def _source_entry(*, source_tool: str, query_seed: str, url: str, date_range: str) -> dict[str, str]:
    return {
        "source_tool": source_tool,
        "query_seed": query_seed,
        "url": url,
        "date_range": date_range,
        "pulled_at": now_iso(),
    }


def _domain(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).netloc or "").lower()


def compose_research_pack(
    *,
    topic: str,
    intent: str,
    serp_results: list[dict[str, Any]],
    keyword_metrics: list[dict[str, Any]],
    paa_questions: list[dict[str, Any]],
    trend_queries: list[str],
    competitor_gaps: list[str],
    company: str,
    city: str | None,
) -> str:
    top10 = serp_results[:10]
    secondary = [x["keyword"] for x in keyword_metrics[:60] if x.get("keyword")]
    entities = list(dict.fromkeys(_topic_keywords(topic) + ["kobido", "masaż twarzy", "skóra", "napięcie"]))

    lines: list[str] = []
    lines.append("# article_research_pack.md")
    lines.append("")
    lines.append("## Topic")
    lines.append(f"- {topic}")
    lines.append("")
    lines.append("## 1) Intent Map")
    lines.append(f"- Dominant intent: {intent}")
    lines.append("- Secondary intent: commercial + local")
    lines.append("- Intent-fit hypothesis: dane SERP i PAA wskazuja na potrzebe przewodnika answer-first z FAQ oraz lokalnym CTA.")
    lines.append("")
    lines.append("## 2) SERP Snapshot (Top 10)")
    lines.append("| # | URL | Title | Intent | Format | Notes |")
    lines.append("|---|---|---|---|---|---|")
    for idx, row in enumerate(top10, start=1):
        title = str(row.get("title", "")).replace("|", "-")
        url = str(row.get("url", ""))
        lines.append(f"| {idx} | {url} | {title} | {intent} | artykul | source: {row.get('source_tool', '')} |")

    lines.append("")
    lines.append("## 3) Content Gaps")
    for idx, gap in enumerate(competitor_gaps[:10], start=1):
        lines.append(f"{idx}. {gap}")
    if not competitor_gaps:
        lines.append("1. Brak wystarczajacych danych do automatycznego gap mappingu.")

    lines.append("")
    lines.append("## 4) Fact Bank")
    lines.append("| Teza | Dowod | URL | Data publikacji/aktualizacji |")
    lines.append("|---|---|---|---|")
    lines.append("| Kluczowe pytania uzytkowniczek skupiaja sie na efektach i bezpieczenstwie | PAA + SERP snapshot | wynik z manifestu research | pulled_at |")

    lines.append("")
    lines.append("## 5) Keyword Cluster")
    primary = secondary[0] if secondary else topic
    lines.append(f"- Primary keyword: {primary}")
    lines.append("- Secondary keywords (min 30):")
    for kw in secondary[:40]:
        lines.append(f"  - {kw}")
    lines.append("- Entities:")
    for entity in entities[:12]:
        lines.append(f"  - {entity}")
    lines.append("- PAA questions (min 10):")
    for q in [x.get("question", "") for x in paa_questions[:15] if x.get("question")]:
        lines.append(f"  - {q}")
    lines.append("- Trend queries (min 5):")
    for tq in trend_queries[:10]:
        lines.append(f"  - {tq}")

    lines.append("")
    lines.append("## 6) Article Blueprint")
    lines.append("### H1")
    lines.append(f"- {topic}: co daje, dla kogo i jak podejsc do pierwszej serii")
    lines.append("")
    lines.append("### Outline (H2/H3 + section goal + word budget)")
    lines.append("1. Co to jest i jak dziala (200)")
    lines.append("2. Najwazniejsze korzysci (700)")
    lines.append("3. Dla kogo i przeciwwskazania (300)")
    lines.append("4. FAQ answer-first (300)")
    lines.append("5. Podsumowanie + CTA (120)")
    lines.append("")
    lines.append("### Internal linking plan")
    lines.append(f"- Linki uslugowe firmy: {company}")
    if city:
        lines.append(f"- Kontekst lokalny: {city}")
    lines.append("")
    lines.append("### Schema recommendation")
    lines.append("- Article + FAQPage")
    lines.append("")
    lines.append("### Answer-first blocks")
    lines.append("- Czy to dziala po pierwszej sesji?")
    lines.append("- Ile sesji potrzeba?")
    lines.append("- Dla kogo to ma sens?")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    if not workspace.exists():
        print(f"ERROR: Workspace not found: {workspace}")
        return 1

    project_root = Path(__file__).resolve().parent.parent
    load_env(project_root)

    started_at = now_iso()
    update_run_context(
        workspace,
        {
            "research_providers_loaded": "google_ads_keyword_planner_api, serper, serpapi, pytrends, google_suggest",
            "research_fetch_started_at": started_at,
            "research_fetch_status": "running",
        },
    )

    brief_meta = read_brief(workspace)
    context_meta = read_run_context(workspace)
    topic = args.topic.strip() or brief_meta.get("topic", "").strip() or context_meta.get("topic", "").strip()
    company = args.company.strip() or brief_meta.get("company", "").strip() or context_meta.get("company", "").strip()
    city = brief_meta.get("primary_city_or_region")
    city = None if city in {None, "", "null", "None"} else str(city)
    locale = brief_meta.get("locale", "pl-PL")
    intent = brief_meta.get("target_intent", "informational")

    if not topic:
        print("ERROR: Missing topic. Provide --topic or fill topic in article_brief.md")
        update_run_context(workspace, {"research_fetch_status": "failed"})
        return 1

    query_seeds = build_query_seeds(topic=topic, city=city)

    try:
        suggest_terms: list[str] = []
        for seed in query_seeds[:4]:
            suggest_terms.extend(google_suggest(seed["query"], locale=locale))
        suggest_terms = list(dict.fromkeys(suggest_terms))

        serp_results: list[dict[str, Any]] = []
        paa_questions: list[dict[str, Any]] = []
        related_queries: list[str] = []
        serp_sources: list[dict[str, str]] = []

        for seed in query_seeds[:4]:
            bundle = fetch_serp_bundle(
                query=seed["query"],
                locale=seed["locale"],
                country_code=seed["geo"],
                num=10,
            )
            for row in bundle.organic:
                row["pulled_at"] = now_iso()
            for row in bundle.paa:
                row["pulled_at"] = now_iso()

            serp_results.extend(bundle.organic)
            paa_questions.extend(bundle.paa)
            related_queries.extend(bundle.related)
            serp_sources.append(
                _source_entry(
                    source_tool=bundle.provider,
                    query_seed=seed["query"],
                    url=f"{bundle.provider}:search",
                    date_range="snapshot on pull date",
                )
            )

        serp_results = sorted(
            serp_results,
            key=lambda x: (str(x.get("query", "")), int(x.get("rank", 9999)), str(x.get("url", ""))),
        )
        paa_questions = list({(x.get("query"), x.get("question")): x for x in paa_questions}.values())
        related_queries = list(dict.fromkeys([x.strip() for x in related_queries if x.strip()]))

        seed_keywords = list(
            dict.fromkeys(
                [x["query"] for x in query_seeds]
                + suggest_terms
                + related_queries
                + [x.get("question", "") for x in paa_questions]
            )
        )

        keyword_metrics = fetch_keyword_metrics(
            seed_keywords=seed_keywords[:120],
            locale=locale,
            country_code="PL",
            target_count=140,
        )
        pulled_at_keywords = now_iso()
        for item in keyword_metrics:
            item["pulled_at"] = pulled_at_keywords

        top_trend_queries = [x.get("keyword", "") for x in keyword_metrics[:8] if x.get("keyword")]
        if len(top_trend_queries) < 5:
            top_trend_queries.extend([x["query"] for x in query_seeds])
        top_trend_queries = list(dict.fromkeys([x.strip() for x in top_trend_queries if x.strip()]))[:8]

        trends_payload = fetch_trends(
            queries=top_trend_queries,
            locale=locale,
            geo="PL",
            timeframe="today 12-m",
            cache_path=workspace / ".cache" / "trends_cache.json",
        )
        trend_points = trends_payload.get("trend_points", []) if isinstance(trends_payload, dict) else []
        related_top = trends_payload.get("related_top_queries", []) if isinstance(trends_payload, dict) else []
        related_rising = trends_payload.get("related_rising_queries", []) if isinstance(trends_payload, dict) else []

        trend_queries = list(dict.fromkeys([*top_trend_queries, *related_top, *related_rising]))[:20]

        top_urls = [row.get("url", "") for row in serp_results[:20] if row.get("url")]
        competitor_matrix, competitor_gaps = build_competitor_matrix(
            urls=top_urls,
            city_or_region=city or "",
            company_name=company,
        )

        # Compatibility arrays (legacy checks/reporting).
        serp_urls = list(dict.fromkeys([row.get("url", "") for row in serp_results if row.get("url")]))[:30]
        keyword_phrases = [x.get("keyword", "") for x in keyword_metrics if x.get("keyword")]
        paa_questions_simple = [x.get("question", "") for x in paa_questions if x.get("question")]

        sources = [
            _source_entry(
                source_tool="google_ads_api",
                query_seed=", ".join([x["query"] for x in query_seeds[:3]]),
                url="google_ads:keyword_planner",
                date_range="snapshot on pull date",
            ),
            _source_entry(
                source_tool="google_suggest_api",
                query_seed=query_seeds[0]["query"],
                url="https://suggestqueries.google.com/complete/search",
                date_range="snapshot on pull date",
            ),
            _source_entry(
                source_tool="pytrends",
                query_seed=", ".join(top_trend_queries[:5]),
                url="https://trends.google.com/trends/",
                date_range="today 12-m",
            ),
        ]
        for entry in serp_sources:
            sources.append(
                _source_entry(
                    source_tool=entry["source_tool"],
                    query_seed=entry["query_seed"],
                    url=entry["url"],
                    date_range=entry["date_range"],
                )
            )

        manifest = {
            "version": "3.0",
            "data_mode": "external_only",
            "topic": topic,
            "company": company,
            "generated_at": datetime.now().date().isoformat(),
            "providers": {
                "keyword_metrics": "google_ads_keyword_planner_api",
                "serp": "serper",
                "serp_fallback": "serpapi",
                "trends": "pytrends",
            },
            "query_seeds": query_seeds,
            "minimum_dataset": {
                "serp_top10_urls": 10,
                "keyword_phrases": 30,
                "paa_questions": 10,
                "trend_queries": 5,
                "keyword_metrics": 40,
                "serp_results": 30,
                "competitor_matrix": 10,
            },
            "keyword_metrics": keyword_metrics,
            "serp_results": serp_results,
            "paa_questions": paa_questions,
            "trend_points": trend_points,
            "competitor_matrix": competitor_matrix,
            "content_gaps": competitor_gaps,
            # legacy compatibility fields still used in checks and docs
            "serp_urls": serp_urls,
            "keyword_phrases": keyword_phrases,
            "paa_questions_legacy": paa_questions_simple,
            "trend_queries": trend_queries,
            "sources": sources,
        }

        if args.dry_run:
            print(json.dumps({
                "ok": True,
                "topic": topic,
                "company": company,
                "query_seeds": len(query_seeds),
                "keyword_metrics": len(keyword_metrics),
                "serp_results": len(serp_results),
                "paa_questions": len(paa_questions),
                "trend_points": len(trend_points),
                "competitor_matrix": len(competitor_matrix),
            }, ensure_ascii=False, indent=2))
            update_run_context(
                workspace,
                {
                    "research_fetch_finished_at": now_iso(),
                    "research_fetch_status": "dry_run_ok",
                },
            )
            return 0

        manifest_path = workspace / "research_evidence_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        research_pack = compose_research_pack(
            topic=topic,
            intent=intent,
            serp_results=serp_results,
            keyword_metrics=keyword_metrics,
            paa_questions=paa_questions,
            trend_queries=trend_queries,
            competitor_gaps=competitor_gaps,
            company=company,
            city=city,
        )
        (workspace / "article_research_pack.md").write_text(research_pack, encoding="utf-8")

        update_run_context(
            workspace,
            {
                "research_fetch_finished_at": now_iso(),
                "research_fetch_status": "ok",
            },
        )

        print(
            json.dumps(
                {
                    "ok": True,
                    "workspace": str(workspace),
                    "manifest": str(manifest_path),
                    "serp_results": len(serp_results),
                    "keyword_metrics": len(keyword_metrics),
                    "paa_questions": len(paa_questions),
                    "trend_points": len(trend_points),
                    "competitor_matrix": len(competitor_matrix),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    except (GoogleAdsProviderError, SerpProviderError, TrendsProviderError, requests.RequestException) as exc:
        update_run_context(
            workspace,
            {
                "research_fetch_finished_at": now_iso(),
                "research_fetch_status": f"failed: {exc}",
            },
        )
        print(f"ERROR: research fetch failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
