#!/usr/bin/env python3
"""Build topic clusters and scoring from normalized planning dataset."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


STOPWORDS = {
    "i",
    "oraz",
    "na",
    "w",
    "do",
    "dla",
    "z",
    "o",
    "czy",
    "jak",
    "co",
    "to",
    "jest",
    "się",
    "sie",
    "u",
    "od",
    "po",
    "przed",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cluster planning keywords into article topics.")
    parser.add_argument("--sprint", type=Path, required=True, help="Path to planning sprint directory.")
    parser.add_argument("--min-priority", type=float, default=60.0, help="Minimum priority score for approved status.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_company(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[\wąćęłńóśżźĄĆĘŁŃÓŚŻŹ-]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def infer_intent(keyword: str) -> str:
    text = keyword.lower()
    if any(x in text for x in ["niepołomice", "niepolomice", "kraków", "krakow", "wieliczka", "blisko"]):
        return "local"
    if any(x in text for x in ["cena", "opinie", "ranking", "vs", "porównanie", "porownanie"]):
        return "commercial"
    if any(x in text for x in ["umów", "umow", "rezerwacja", "gdzie"]):
        return "transactional"
    return "informational"


def recommended_lengths(intent: str) -> tuple[int, int]:
    if intent == "local":
        return 900, 1800
    if intent == "commercial":
        return 1200, 2200
    if intent == "transactional":
        return 900, 1500
    return 1400, 2600


def load_company_services(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\s*(.*?)```", text, flags=re.S)
    mapping: dict[str, list[str]] = {}
    for block in blocks:
        company_match = re.search(r'^company:\s*"([^"]+)"', block, flags=re.M)
        if not company_match:
            continue
        company = normalize_company(company_match.group(1))
        urls = re.findall(r'^\s*service_url:\s*"([^"]+)"', block, flags=re.M)
        if urls:
            mapping[company] = urls
    return mapping


def trend_direction(points: list[dict[str, Any]], keyword: str) -> str:
    kw = keyword.lower()
    values = [int(row.get("value", 0) or 0) for row in points if kw in str(row.get("query", "")).lower()]
    if len(values) < 2:
        return "flat"
    if values[-1] > values[0] + 5:
        return "up"
    if values[-1] < values[0] - 5:
        return "down"
    return "flat"


def demand_score(total_searches: int) -> float:
    if total_searches <= 0:
        return 0.0
    return min(5.0, round(math.log10(total_searches + 1) * 1.7, 2))


def infer_serp_competition(rows: list[dict[str, Any]]) -> str:
    domains = {str(r.get("domain", "")).strip().lower() for r in rows if str(r.get("domain", "")).strip()}
    if len(domains) >= 8:
        return "high"
    if len(domains) >= 4:
        return "medium"
    return "low"


def choose_cluster_key(keyword: str) -> str:
    tokens = tokenize(keyword)
    if not tokens:
        return "misc"
    if len(tokens) == 1:
        return tokens[0]
    return " ".join(tokens[:2])


def write_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def main() -> int:
    args = parse_args()
    sprint = args.sprint.resolve()
    dataset_path = sprint / "planning_dataset.json"
    if not dataset_path.exists():
        print(f"ERROR: missing planning_dataset.json in {sprint}. Run content_planning_ingest.py first.")
        return 1

    payload = load_json(dataset_path)
    keyword_rows = payload.get("keywords", []) if isinstance(payload.get("keywords"), list) else []
    serp_rows = payload.get("serp_results", []) if isinstance(payload.get("serp_results"), list) else []
    paa_rows = payload.get("paa_questions", []) if isinstance(payload.get("paa_questions"), list) else []
    trend_rows = payload.get("trend_points", []) if isinstance(payload.get("trend_points"), list) else []

    if not keyword_rows:
        print("ERROR: keyword dataset is empty. Cannot build topic clusters.")
        return 1

    company_services = load_company_services(
        sprint.parents[1] / "docs" / "company_context_profiles.md"
    )

    by_company_cluster: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in keyword_rows:
        company = normalize_company(str(row.get("company", "") or "unknown"))
        keyword = str(row.get("keyword", "")).strip()
        if not keyword:
            continue
        cluster_key = choose_cluster_key(keyword)
        by_company_cluster[(company, cluster_key)].append(row)

    candidates: list[dict[str, Any]] = []
    topic_counter = 1

    for (company, cluster_name), rows in sorted(by_company_cluster.items(), key=lambda item: (item[0][0], item[0][1])):
        rows_sorted = sorted(rows, key=lambda r: int(r.get("avg_monthly_searches", 0) or 0), reverse=True)
        primary = str(rows_sorted[0].get("keyword", "")).strip()
        secondaries = [str(r.get("keyword", "")).strip() for r in rows_sorted[1:16] if str(r.get("keyword", "")).strip()]
        total_searches = sum(int(r.get("avg_monthly_searches", 0) or 0) for r in rows_sorted[:15])

        intent = infer_intent(primary)
        rec_min, rec_max = recommended_lengths(intent)

        company_serp = [r for r in serp_rows if normalize_company(str(r.get("company", ""))) == company]
        cluster_serp = [r for r in company_serp if cluster_name in str(r.get("query", "")).lower() or cluster_name in str(r.get("title", "")).lower()]
        serp_level = infer_serp_competition(cluster_serp or company_serp)

        company_trends = [r for r in trend_rows if normalize_company(str(r.get("company", ""))) == company]
        trend = trend_direction(company_trends, primary)

        services = company_services.get(company, [])
        target_service_url = services[0] if services else ""
        business_fit = 4.0 if target_service_url else 2.0
        if services and any(any(token in primary.lower() for token in tokenize(url)) for url in services):
            business_fit = 5.0

        intent_fit = 4.0 if intent in {"informational", "commercial", "local"} else 3.0
        if intent == "local" and any(city in primary.lower() for city in ["niepołomice", "niepolomice", "kraków", "krakow"]):
            intent_fit = 5.0

        dem = demand_score(total_searches)
        trend_bonus = 0.6 if trend == "up" else (0.3 if trend == "flat" else -0.3)
        competition_penalty = 0.6 if serp_level == "high" else (0.3 if serp_level == "medium" else 0.0)
        priority = ((dem / 5.0) * 35.0) + ((intent_fit / 5.0) * 25.0) + ((business_fit / 5.0) * 25.0) + (15.0 + trend_bonus * 5.0) - (competition_penalty * 10.0)
        priority = max(0.0, min(100.0, round(priority, 2)))

        status = "approved" if (priority >= args.min_priority and len(secondaries) >= 8 and target_service_url) else "candidate"
        cta_type = "consultation" if intent in {"commercial", "local", "transactional"} else "learn_more"

        candidates.append(
            {
                "topic_id": f"tp-{topic_counter:04d}",
                "company": company,
                "topic_cluster_name": cluster_name,
                "article_title_working": f"{primary}: co warto wiedzieć",
                "primary_keyword": primary,
                "secondary_keywords": " | ".join(secondaries),
                "avg_monthly_searches_sum": total_searches,
                "intent": intent,
                "trend_direction": trend,
                "serp_competition_level": serp_level,
                "content_gap_note": "Dodaj lokalne FAQ, konkretne scenariusze i link do usługi.",
                "demand_score": round(dem, 2),
                "intent_fit_score": round(intent_fit, 2),
                "business_fit_score": round(business_fit, 2),
                "priority_score": priority,
                "recommended_length_min": rec_min,
                "recommended_length_max": rec_max,
                "target_service_url": target_service_url,
                "cta_type": cta_type,
                "status": status,
            }
        )
        topic_counter += 1

    headers = [
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
    ]

    write_csv(sprint / "content_plan_candidates.csv", candidates, headers)
    backlog = [row for row in candidates if row["status"] == "approved"]
    write_csv(sprint / "content_plan_backlog.csv", backlog, headers)

    print(
        json.dumps(
            {
                "ok": True,
                "candidates": len(candidates),
                "approved": len(backlog),
                "candidates_csv": str((sprint / 'content_plan_candidates.csv').resolve()),
                "backlog_csv": str((sprint / 'content_plan_backlog.csv').resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
