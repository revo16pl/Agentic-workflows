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
    parser.add_argument(
        "--content-profile",
        choices=["article", "service_page"],
        default="",
        help="Optional content profile override. Defaults to run_context value or article.",
    )
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


def build_query_seeds(topic: str, city: str | None, content_profile: str = "article") -> list[dict[str, str]]:
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
    if content_profile == "service_page":
        base.append(
            {
                "query": f"{topic} cena",
                "intent_hint": "commercial",
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


def _keyword_tokens(text: str) -> list[str]:
    return [
        token.strip().lower()
        for token in re.findall(r"\b[\w\-ąćęłńóśżźĄĆĘŁŃÓŚŻŹ]{3,}\b", text, flags=re.UNICODE)
        if token.strip()
    ]


def build_keyword_fallback(
    *,
    seed_keywords: list[str],
    serp_results: list[dict[str, Any]],
    paa_questions: list[dict[str, Any]],
    related_queries: list[str],
    suggest_terms: list[str],
    target_count: int,
    locale: str,
    country_code: str,
) -> list[dict[str, Any]]:
    phrases: list[str] = []
    phrases.extend([x.strip() for x in seed_keywords if x.strip()])
    phrases.extend([x.strip() for x in related_queries if x.strip()])
    phrases.extend([x.strip() for x in suggest_terms if x.strip()])

    for row in paa_questions:
        if not isinstance(row, dict):
            continue
        question = str(row.get("question", "")).strip()
        if question:
            phrases.append(question)

    for row in serp_results:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title", "")).strip()
        if title:
            phrases.extend(_keyword_tokens(title))

    cleaned: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        normalized = re.sub(r"\s+", " ", phrase.strip().lower())
        if len(normalized) < 3:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(phrase.strip())
        if len(cleaned) >= max(target_count, 60):
            break

    if not cleaned:
        cleaned = seed_keywords[:]

    pulled_at = now_iso()
    return [
        {
            "keyword": phrase,
            "avg_monthly_searches": None,
            "competition": "UNSPECIFIED",
            "top_of_page_bid_low_micros": None,
            "top_of_page_bid_high_micros": None,
            "source_tool": "fallback_keyword_proxy",
            "locale": locale,
            "country": country_code,
            "pulled_at": pulled_at,
        }
        for phrase in cleaned[: max(target_count, 40)]
    ]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def write_service_writer_packet_from_research(
    *,
    workspace: Path,
    topic: str,
    intent: str,
    company: str,
    context_meta: dict[str, str],
    content_gaps: list[str],
    serp_results: list[dict[str, Any]],
    keyword_metrics: list[dict[str, Any]],
    paa_questions: list[dict[str, Any]],
    trend_queries: list[str],
    research_confidence: str,
    fallback_reason: str,
) -> None:
    if context_meta.get("content_profile", "").strip().lower() != "service_page":
        return

    service_context = load_json(workspace / "service_page_context.json")
    company_snapshot = load_json(workspace / "company_profile_snapshot.json")
    packet_path = workspace / "service_page_writer_packet.md"

    tabs = service_context.get("tab_labels", []) if isinstance(service_context.get("tab_labels"), list) else []
    tab_labels = [str(item).strip() for item in tabs if str(item).strip()] or [
        "Wskazania",
        "Przeciwwskazania i bezpieczeństwo",
        "Zalecenia przed i po",
        "FAQ",
    ]

    subheading = service_context.get("subheading", {}) if isinstance(service_context.get("subheading"), dict) else {}
    source_chars = int(subheading.get("chars", 0) or 0)
    source_url = context_meta.get("source_url", "").strip()

    top_keywords = [str(item.get("keyword", "")).strip() for item in keyword_metrics if isinstance(item, dict)]
    top_keywords = [x for x in top_keywords if x][:8]
    top_questions = [str(item.get("question", "")).strip() for item in paa_questions if isinstance(item, dict)]
    top_questions = [x for x in top_questions if x][:4]
    top_domains = list(
        dict.fromkeys(
            [
                _domain(str(item.get("url", "")))
                for item in serp_results[:12]
                if isinstance(item, dict) and str(item.get("url", "")).strip()
            ]
        )
    )

    brand_voice = company_snapshot.get("brand_voice", {}) if isinstance(company_snapshot.get("brand_voice"), dict) else {}
    tone_rules = brand_voice.get("tone_rules", []) if isinstance(brand_voice.get("tone_rules"), list) else []
    avoid_rules = brand_voice.get("avoid_rules", []) if isinstance(brand_voice.get("avoid_rules"), list) else []
    excluded_claims = company_snapshot.get("excluded_claims", []) if isinstance(company_snapshot.get("excluded_claims"), list) else []
    legal_notes = company_snapshot.get("legal_notes", []) if isinstance(company_snapshot.get("legal_notes"), list) else []
    default_cta = company_snapshot.get("default_cta", {}) if isinstance(company_snapshot.get("default_cta"), dict) else {}
    allowed_links = (
        company_snapshot.get("allowed_service_links", [])
        if isinstance(company_snapshot.get("allowed_service_links"), list)
        else []
    )

    lines: list[str] = [
        "# service_page_writer_packet.md",
        "",
        "## Topic and intent summary",
        f"- Topic: {topic}",
        f"- Company: {company}",
        f"- URL source: {source_url}",
        f"- Dominująca intencja: {intent}",
        f"- Research confidence: {research_confidence}",
    ]
    if fallback_reason:
        lines.append(f"- Research fallback: {fallback_reason}")

    lines.extend(
        [
            "",
            "## Source page baseline (structure only)",
            f"- Subheading target length: ~{source_chars} chars",
            "- Zakładki CMS:",
        ]
    )
    lines.extend([f"  - {label}" for label in tab_labels])

    lines.extend(["", "## Top research insights"])
    lines.extend(
        [
            f"1. Najczęstsze frazy i warianty: {', '.join(top_keywords[:5]) if top_keywords else '(uzupełnij po research)'}",
            f"2. Widoczność domen konkurencyjnych: {', '.join(top_domains[:5]) if top_domains else '(uzupełnij po research)'}",
            f"3. Pytania użytkowniczek: {'; '.join(top_questions[:2]) if top_questions else '(uzupełnij po research)'}",
        ]
    )

    lines.extend(["", "## Content gaps to cover"])
    if content_gaps:
        for idx, gap in enumerate(content_gaps[:5], start=1):
            lines.append(f"{idx}. {gap}")
    else:
        lines.extend(["1. Brak wyraźnego answer-first otwarcia.", "2. Brak krótkich informacji bezpieczeństwa.", "3. Brak praktycznych zaleceń przed/po."])

    lines.extend(["", "## Brand voice rules", f"- Company profile id: {company_snapshot.get('company_profile_id', '')}"])
    lines.append("- Tone rules:")
    lines.extend([f"  - {str(rule).strip()}" for rule in tone_rules if str(rule).strip()] or ["  - (uzupełnij)"])
    lines.append("- Avoid rules:")
    lines.extend([f"  - {str(rule).strip()}" for rule in avoid_rules if str(rule).strip()] or ["  - (uzupełnij)"])

    lines.extend(["", "## Banned claims / compliance", "- Excluded claims:"])
    lines.extend([f"  - {str(item).strip()}" for item in excluded_claims if str(item).strip()] or ["  - (brak)"])
    lines.append("- Legal notes:")
    lines.extend([f"  - {str(item).strip()}" for item in legal_notes if str(item).strip()] or ["  - (brak)"])

    lines.extend(
        [
            "",
            "## CMS sections and quality checklist",
            "### Subheading",
            f"- 1-2 zdania, nowa treść, podobna długość (~{source_chars} znaków).",
            "",
            "### Opis",
            "- 3 krótkie akapity: problem -> działanie -> realistyczny efekt + bezpieczeństwo.",
            "- Brak lania wody, brak klisz i pustych obietnic.",
            "",
            "### Najważniejsze informacje",
            "- Każda zakładka musi mieć realne bullet points.",
            "- FAQ: min 2 pytania i krótkie odpowiedzi.",
            "- Zero placeholderów typu '-' lub '_Wpisz..._'.",
            "",
            "## Editorial QA protocol (obowiązkowe przed exportem)",
            "1. Zrób pierwszy pass tylko na logikę i sens zdań; usuń frazy, których normalny człowiek by nie powiedział.",
            "2. Zrób drugi pass na intent i strukturę: czy każda sekcja odpowiada na realne pytanie użytkowniczki.",
            "3. Zrób trzeci pass na copy: prostsze zdania, mniej klisz, pełne przepisanie dziwnych fragmentów.",
            "4. Po machine QA wróć do draftu, wdroż poprawki i dopiero wtedy oznacz post_machine_qa_revision_completed: yes.",
            "5. Udokumentuj poprawki w editorial_review.md i dopiero potem ustaw final_decision: approved.",
            "",
            "## CTA and links",
            f"- CTA (MoFu): {str(default_cta.get('mofu', '')).strip()}",
            "- Allowed service links:",
        ]
    )
    lines.extend([f"  - {str(link).strip()}" for link in allowed_links if str(link).strip()] or ["  - (brak)"])

    lines.extend(["", "## Trend / PAA hints", "- Trend queries:"])
    lines.extend([f"  - {item}" for item in trend_queries[:5]] or ["  - (brak)"])
    lines.append("- PAA questions:")
    lines.extend([f"  - {item}" for item in top_questions] or ["  - (brak)"])

    packet_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


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
    content_profile: str,
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
    if content_profile == "service_page":
        lines.append("### Format: service_page")
        lines.append("- Sekcje docelowe: Subheading, Opis, Najważniejsze informacje.")
        lines.append("- Dlugosc: krotki format, edukacyjny i lokalny.")
        lines.append("")
        lines.append("### Zakres sekcji")
        lines.append("1. Subheading: 1-2 zdania, intencja + lokalizacja.")
        lines.append("2. Opis: 3 akapity, konkret + bezpieczenstwo.")
        lines.append("3. Najważniejsze informacje: krótkie punkty per zakładka.")
        lines.append("")
        lines.append("### Internal linking plan")
        lines.append(f"- Linki uslugowe firmy: {company}")
        if city:
            lines.append(f"- Kontekst lokalny: {city}")
        lines.append("")
        lines.append("### Schema recommendation")
        lines.append("- Service + FAQPage")
        lines.append("")
        lines.append("### Answer-first blocks")
        lines.append("- Dla kogo ten zabieg ma sens?")
        lines.append("- Jak przygotować się do wizyty?")
        lines.append("- Kiedy skonsultować przeciwwskazania?")
    else:
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
            "research_fallback_reason": "",
            "research_confidence": "",
        },
    )

    brief_meta = read_brief(workspace)
    context_meta = read_run_context(workspace)
    topic = args.topic.strip() or brief_meta.get("topic", "").strip() or context_meta.get("topic", "").strip()
    company = args.company.strip() or brief_meta.get("company", "").strip() or context_meta.get("company", "").strip()
    content_profile = (
        args.content_profile.strip()
        or context_meta.get("content_profile", "").strip()
        or brief_meta.get("content_profile", "").strip()
        or "article"
    ).lower()
    if content_profile not in {"article", "service_page"}:
        content_profile = "article"
    city = brief_meta.get("primary_city_or_region")
    city = None if city in {None, "", "null", "None"} else str(city)
    locale = brief_meta.get("locale", "pl-PL")
    intent = brief_meta.get("target_intent", "informational")

    if not topic:
        print("ERROR: Missing topic. Provide --topic or fill topic in article_brief.md")
        update_run_context(workspace, {"research_fetch_status": "failed"})
        return 1

    query_seeds = build_query_seeds(topic=topic, city=city, content_profile=content_profile)

    minimum_dataset = (
        {
            "serp_top10_urls": 10,
            "keyword_phrases": 30,
            "paa_questions": 10,
            "trend_queries": 5,
            "keyword_metrics": 40,
            "serp_results": 30,
            "competitor_matrix": 10,
            "trend_points_per_query": 12,
            "content_gaps": 5,
            "serp_unique_domains": 8,
            "keyword_numeric_ratio": 0.8,
            "freshness_days": 7,
        }
        if content_profile == "article"
        else {
            "serp_top10_urls": 6,
            "keyword_phrases": 15,
            "paa_questions": 6,
            "trend_queries": 3,
            "keyword_metrics": 20,
            "serp_results": 12,
            "competitor_matrix": 5,
            "trend_points_per_query": 6,
            "content_gaps": 3,
            "serp_unique_domains": 4,
            "keyword_numeric_ratio": 0.7,
            "freshness_days": 14,
        }
    )
    seed_limit = 4 if content_profile == "article" else 3
    keyword_target_count = 140 if content_profile == "article" else 60
    trend_query_limit = 8 if content_profile == "article" else 5
    trend_query_cap = 20 if content_profile == "article" else 10
    top_urls_limit = 20 if content_profile == "article" else 12

    try:
        providers_status: dict[str, str] = {
            "keyword_metrics": "unknown",
            "serp": "unknown",
            "trends": "unknown",
            "competitor_matrix": "unknown",
        }
        research_confidence = "high"
        fallback_reason = ""

        suggest_terms: list[str] = []
        for seed in query_seeds[:seed_limit]:
            suggest_terms.extend(google_suggest(seed["query"], locale=locale))
        suggest_terms = list(dict.fromkeys(suggest_terms))

        serp_results: list[dict[str, Any]] = []
        paa_questions: list[dict[str, Any]] = []
        related_queries: list[str] = []
        serp_sources: list[dict[str, str]] = []

        for seed in query_seeds[:seed_limit]:
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
        providers_status["serp"] = "ok"

        serp_results = sorted(
            serp_results,
            key=lambda x: (str(x.get("query", "")), int(x.get("rank", 9999)), str(x.get("url", ""))),
        )
        paa_questions = list({(x.get("query"), x.get("question")): x for x in paa_questions}.values())
        related_queries = list(dict.fromkeys([x.strip() for x in related_queries if x.strip()]))
        if len(paa_questions) < 6:
            fallback_questions: list[dict[str, Any]] = []
            candidates = suggest_terms + related_queries + [seed["query"] for seed in query_seeds]
            for candidate in candidates:
                value = str(candidate).strip()
                if not value:
                    continue
                question = value if value.endswith("?") else f"Czy {value}?"
                fallback_questions.append(
                    {
                        "query": query_seeds[0]["query"],
                        "question": question,
                        "source_tool": "fallback_paa_proxy",
                        "pulled_at": now_iso(),
                    }
                )
                if len(fallback_questions) >= 8:
                    break
            paa_questions.extend(fallback_questions)
            paa_questions = list({(x.get("query"), x.get("question")): x for x in paa_questions}.values())
            if len(paa_questions) < 6:
                generic_templates = [
                    f"Jak przygotować się do zabiegu {topic}?",
                    f"Jakie są przeciwwskazania do {topic}?",
                    f"Ile trwa zabieg {topic}?",
                    f"Jak często wykonywać {topic}?",
                    f"Czy {topic} jest odpowiedni dla początkujących?",
                    f"Jakie są zalecenia po zabiegu {topic}?",
                ]
                for question in generic_templates:
                    paa_questions.append(
                        {
                            "query": query_seeds[0]["query"],
                            "question": question,
                            "source_tool": "fallback_paa_proxy",
                            "pulled_at": now_iso(),
                        }
                    )
                    paa_questions = list({(x.get("query"), x.get("question")): x for x in paa_questions}.values())
                    if len(paa_questions) >= 6:
                        break

        seed_keywords = list(
            dict.fromkeys(
                [x["query"] for x in query_seeds]
                + suggest_terms
                + related_queries
                + [x.get("question", "") for x in paa_questions]
            )
        )

        try:
            keyword_metrics = fetch_keyword_metrics(
                seed_keywords=seed_keywords[:120],
                locale=locale,
                country_code="PL",
                target_count=keyword_target_count,
            )
            pulled_at_keywords = now_iso()
            for item in keyword_metrics:
                item["pulled_at"] = pulled_at_keywords
            providers_status["keyword_metrics"] = "ok"
        except GoogleAdsProviderError as exc:
            fallback_reason = str(exc)
            research_confidence = "medium" if content_profile == "service_page" else "low"
            providers_status["keyword_metrics"] = "fallback"
            keyword_metrics = build_keyword_fallback(
                seed_keywords=seed_keywords[:120],
                serp_results=serp_results,
                paa_questions=paa_questions,
                related_queries=related_queries,
                suggest_terms=suggest_terms,
                target_count=keyword_target_count,
                locale=locale,
                country_code="PL",
            )

        top_trend_queries = [x.get("keyword", "") for x in keyword_metrics[:trend_query_limit] if x.get("keyword")]
        if len(top_trend_queries) < 5:
            top_trend_queries.extend([x["query"] for x in query_seeds])
        top_trend_queries = list(dict.fromkeys([x.strip() for x in top_trend_queries if x.strip()]))[:trend_query_limit]

        trend_points: list[dict[str, Any]] = []
        related_top: list[str] = []
        related_rising: list[str] = []
        try:
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
            if trend_points:
                providers_status["trends"] = "ok"
            else:
                providers_status["trends"] = "fallback"
                research_confidence = "medium" if research_confidence == "high" else research_confidence
        except TrendsProviderError:
            providers_status["trends"] = "fallback"
            research_confidence = "medium" if research_confidence == "high" else research_confidence

        trend_queries = list(dict.fromkeys([*top_trend_queries, *related_top, *related_rising]))[:trend_query_cap]
        if providers_status["trends"] == "fallback":
            minimum_dataset["trend_points_per_query"] = 0

        top_urls = [row.get("url", "") for row in serp_results[:top_urls_limit] if row.get("url")]
        competitor_matrix, competitor_gaps = build_competitor_matrix(
            urls=top_urls,
            city_or_region=city or "",
            company_name=company,
        )
        providers_status["competitor_matrix"] = "ok"

        # Compatibility arrays (legacy checks/reporting).
        serp_urls = list(dict.fromkeys([row.get("url", "") for row in serp_results if row.get("url")]))[:30]
        keyword_phrases = [x.get("keyword", "") for x in keyword_metrics if x.get("keyword")]
        paa_questions_simple = [x.get("question", "") for x in paa_questions if x.get("question")]

        sources = [
            _source_entry(
                source_tool="google_ads_api" if providers_status["keyword_metrics"] == "ok" else "fallback_keyword_proxy",
                query_seed=", ".join([x["query"] for x in query_seeds[:3]]),
                url="google_ads:keyword_planner"
                if providers_status["keyword_metrics"] == "ok"
                else "fallback:keyword_proxy",
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
            "content_profile": content_profile,
            "topic": topic,
            "company": company,
            "generated_at": datetime.now().date().isoformat(),
            "providers": {
                "keyword_metrics": "google_ads_keyword_planner_api",
                "serp": "serper",
                "serp_fallback": "serpapi",
                "trends": "pytrends",
            },
            "providers_status": providers_status,
            "query_seeds": query_seeds,
            "minimum_dataset": minimum_dataset,
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
            "data_quality_note": (
                f"Research completed with fallback for keyword metrics: {fallback_reason}"
                if fallback_reason
                else "Research completed with full provider coverage."
            ),
        }

        if args.dry_run:
            print(json.dumps({
                "ok": True,
                "topic": topic,
                "company": company,
                "research_confidence": research_confidence,
                "providers_status": providers_status,
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
                    "research_fetch_status": "dry_run_ok_with_fallback" if fallback_reason else "dry_run_ok",
                    "research_fallback_reason": fallback_reason,
                    "research_confidence": research_confidence,
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
            content_profile=content_profile,
        )
        (workspace / "article_research_pack.md").write_text(research_pack, encoding="utf-8")

        write_service_writer_packet_from_research(
            workspace=workspace,
            topic=topic,
            intent=intent,
            company=company,
            context_meta=context_meta,
            content_gaps=competitor_gaps,
            serp_results=serp_results,
            keyword_metrics=keyword_metrics,
            paa_questions=paa_questions,
            trend_queries=trend_queries,
            research_confidence=research_confidence,
            fallback_reason=fallback_reason,
        )

        update_run_context(
            workspace,
            {
                "research_fetch_finished_at": now_iso(),
                "research_fetch_status": "ok_with_fallback" if fallback_reason else "ok",
                "research_fallback_reason": fallback_reason,
                "research_confidence": research_confidence,
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
                    "research_confidence": research_confidence,
                    "providers_status": providers_status,
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
                "research_fallback_reason": "",
                "research_confidence": "low",
            },
        )
        print(f"ERROR: research fetch failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
