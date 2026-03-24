#!/usr/bin/env python3
"""Ingest manual research exports into normalized planning dataset."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


KEYWORD_ALIASES = {
    "company": ["company", "firma", "brand"],
    "keyword": ["keyword", "phrase", "fraza", "słowo kluczowe", "slowo kluczowe"],
    "avg_monthly_searches": [
        "avg_monthly_searches",
        "avg monthly searches",
        "monthly searches",
        "search volume",
        "volume",
        "searches",
        "średnia miesieczna liczba wyszukiwan",
        "srednia miesieczna liczba wyszukiwan",
        "wyszukiwania",
    ],
    "competition": ["competition", "konkurencja", "keyword difficulty", "difficulty", "kd"],
}

SERP_ALIASES = {
    "company": ["company", "firma", "brand"],
    "query": ["query", "zapytanie", "seed"],
    "rank": ["rank", "position", "pozycja"],
    "title": ["title", "tytul", "naglowek"],
    "url": ["url", "link"],
    "snippet": ["snippet", "opis"],
    "domain": ["domain", "domena"],
}

PAA_ALIASES = {
    "company": ["company", "firma", "brand"],
    "query": ["query", "zapytanie", "seed"],
    "question": ["question", "pytanie"],
}

TRENDS_ALIASES = {
    "company": ["company", "firma", "brand"],
    "query": ["query", "zapytanie", "fraza", "keyword"],
    "period": ["period", "date", "okres", "data"],
    "value": ["value", "score", "interest", "wartosc", "popularność", "popularnosc"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest manual content planning data exports.")
    parser.add_argument("--sprint", type=Path, required=True, help="Path to planning sprint directory.")
    return parser.parse_args()


def normalize_header(value: str) -> str:
    return value.strip().lower().replace("_", " ")


def pick_value(row: dict[str, str], aliases: list[str]) -> str:
    for key, value in row.items():
        key_norm = normalize_header(key)
        if key_norm in {normalize_header(alias) for alias in aliases}:
            return str(value).strip()
    return ""


def parse_number(value: str) -> int:
    cleaned = value.replace(" ", "").replace("\u00a0", "").replace(",", ".")
    cleaned = "".join(ch for ch in cleaned if ch.isdigit() or ch == ".")
    if not cleaned:
        return 0
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def infer_company_from_name(path: Path) -> str:
    stem = path.stem.lower()
    parts = stem.split("_")
    if parts and parts[0] in {"keyword", "keywords", "serp", "paa", "trend", "trends"}:
        parts = parts[1:]
    if parts and parts[-1].isdigit():
        parts = parts[:-1]
    if parts:
        return " ".join(parts).replace("-", " ").strip()
    return ""


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader if row]


def collect_csvs(root: Path, prefix: str) -> list[Path]:
    matches = []
    for p in sorted(root.glob("*.csv")):
        if p.name.lower().startswith(prefix):
            matches.append(p)
    return matches


def main() -> int:
    args = parse_args()
    sprint = args.sprint.resolve()
    research_inputs = sprint / "research_inputs"
    if not research_inputs.exists():
        print(f"ERROR: missing research_inputs directory: {research_inputs}")
        return 1

    keyword_files = collect_csvs(research_inputs, "keyword")
    serp_files = collect_csvs(research_inputs, "serp")
    paa_files = collect_csvs(research_inputs, "paa")
    trends_files = collect_csvs(research_inputs, "trend")

    if not any([keyword_files, serp_files, paa_files, trends_files]):
        print("ERROR: no CSV files found in research_inputs. Expected keywords/serp/paa/trends prefixed files.")
        return 1

    keywords: list[dict[str, Any]] = []
    serp_results: list[dict[str, Any]] = []
    paa_questions: list[dict[str, Any]] = []
    trend_points: list[dict[str, Any]] = []

    for path in keyword_files:
        company_hint = infer_company_from_name(path)
        for row in load_rows(path):
            keyword = pick_value(row, KEYWORD_ALIASES["keyword"])
            if not keyword:
                continue
            company = pick_value(row, KEYWORD_ALIASES["company"]) or company_hint or "unknown"
            keywords.append(
                {
                    "company": company,
                    "keyword": keyword,
                    "avg_monthly_searches": parse_number(pick_value(row, KEYWORD_ALIASES["avg_monthly_searches"])),
                    "competition": pick_value(row, KEYWORD_ALIASES["competition"]).upper() or "UNSPECIFIED",
                    "source_file": path.name,
                }
            )

    for path in serp_files:
        company_hint = infer_company_from_name(path)
        for row in load_rows(path):
            url = pick_value(row, SERP_ALIASES["url"])
            if not url:
                continue
            company = pick_value(row, SERP_ALIASES["company"]) or company_hint or "unknown"
            serp_results.append(
                {
                    "company": company,
                    "query": pick_value(row, SERP_ALIASES["query"]),
                    "rank": parse_number(pick_value(row, SERP_ALIASES["rank"])),
                    "title": pick_value(row, SERP_ALIASES["title"]),
                    "url": url,
                    "snippet": pick_value(row, SERP_ALIASES["snippet"]),
                    "domain": pick_value(row, SERP_ALIASES["domain"]),
                    "source_file": path.name,
                }
            )

    for path in paa_files:
        company_hint = infer_company_from_name(path)
        for row in load_rows(path):
            question = pick_value(row, PAA_ALIASES["question"])
            if not question:
                continue
            company = pick_value(row, PAA_ALIASES["company"]) or company_hint or "unknown"
            paa_questions.append(
                {
                    "company": company,
                    "query": pick_value(row, PAA_ALIASES["query"]),
                    "question": question,
                    "source_file": path.name,
                }
            )

    for path in trends_files:
        company_hint = infer_company_from_name(path)
        for row in load_rows(path):
            query = pick_value(row, TRENDS_ALIASES["query"])
            if not query:
                continue
            company = pick_value(row, TRENDS_ALIASES["company"]) or company_hint or "unknown"
            trend_points.append(
                {
                    "company": company,
                    "query": query,
                    "period": pick_value(row, TRENDS_ALIASES["period"]),
                    "value": parse_number(pick_value(row, TRENDS_ALIASES["value"])),
                    "source_file": path.name,
                }
            )

    payload = {
        "version": "1.0",
        "keywords": keywords,
        "serp_results": serp_results,
        "paa_questions": paa_questions,
        "trend_points": trend_points,
    }
    dataset_path = sprint / "planning_dataset.json"
    dataset_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "ok": True,
        "dataset_path": str(dataset_path),
        "keyword_rows": len(keywords),
        "serp_rows": len(serp_results),
        "paa_rows": len(paa_questions),
        "trend_rows": len(trend_points),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
