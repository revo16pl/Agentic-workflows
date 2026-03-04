#!/usr/bin/env python3
"""One-command content planning run for non-SEO users.

User provides keyword CSV exports (+ optional extra CSV files), and the script:
1) initializes a planning sprint,
2) ingests CSV data,
3) auto-fills missing SERP/PAA via Serper/SerpApi,
4) auto-fills missing Trends via pytrends,
5) builds clusters, runs strict gates, and publishes queue.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from providers_serp import SerpProviderError, fetch_serp_bundle
from providers_trends import TrendsProviderError, fetch_trends

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLANNING_ROOT = PROJECT_ROOT / "Agentic Articles" / "planning"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autopilot content planning from CSV exports.")
    parser.add_argument("--company", required=True, help='Natural company name, e.g. "studio balans"')
    parser.add_argument(
        "--keyword-files",
        nargs="+",
        required=True,
        help="Path(s) to keyword export CSV files.",
    )
    parser.add_argument(
        "--extra-files",
        nargs="*",
        default=[],
        help="Optional additional CSV files (SERP/PAA/Trends).",
    )
    parser.add_argument("--sprint-date", default="", help="Sprint date YYYY-MM-DD (default: today).")
    parser.add_argument("--locale", default="pl-PL")
    parser.add_argument("--country", default="PL")
    parser.add_argument("--max-serp-seeds", type=int, default=5)
    parser.add_argument("--max-trends-seeds", type=int, default=8)
    parser.add_argument("--skip-auto-serp", action="store_true")
    parser.add_argument("--skip-auto-trends", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def normalize_company(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def slugify(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-") or "company"


def run(cmd: list[str], cwd: Path = PROJECT_ROOT) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def detect_csv_type(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = [h.strip().lower() for h in (reader.fieldnames or [])]

    def has_any(candidates: list[str]) -> bool:
        normalized = set(headers)
        return any(candidate.lower() in normalized for candidate in candidates)

    if has_any(["keyword", "phrase", "fraza", "słowo kluczowe", "slowo kluczowe"]) and has_any(
        ["avg_monthly_searches", "avg monthly searches", "monthly searches", "search volume", "volume", "wyszukiwania"]
    ):
        return "keyword"
    if has_any(["url", "link"]) and has_any(["rank", "position", "pozycja"]):
        return "serp"
    if has_any(["question", "pytanie"]):
        return "paa"
    if has_any(["period", "date", "okres"]) and has_any(["value", "interest", "score", "wartosc"]):
        return "trends"
    return "unknown"


def copy_inputs(sprint_inputs: Path, company: str, keyword_files: list[str], extra_files: list[str]) -> dict[str, int]:
    company_slug = slugify(company)
    counts = {"keyword": 0, "serp": 0, "paa": 0, "trends": 0, "unknown": 0}

    all_paths = [(Path(p).expanduser().resolve(), "keyword") for p in keyword_files]
    all_paths.extend((Path(p).expanduser().resolve(), "auto") for p in extra_files)

    for idx, (src, forced_type) in enumerate(all_paths, start=1):
        if not src.exists() or src.suffix.lower() != ".csv":
            counts["unknown"] += 1
            continue

        csv_type = forced_type if forced_type != "auto" else detect_csv_type(src)
        if csv_type == "unknown":
            counts["unknown"] += 1
            continue

        dst = sprint_inputs / f"{csv_type}_{company_slug}_{idx}.csv"
        shutil.copyfile(src, dst)
        counts[csv_type] += 1

    return counts


def load_dataset(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_dataset(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_default_company(payload: dict[str, Any], company: str) -> None:
    for key in ["keywords", "serp_results", "paa_questions", "trend_points"]:
        rows = payload.get(key, [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict):
                current = normalize_company(str(row.get("company", "")))
                if not current or current == "unknown":
                    row["company"] = company


def top_seed_keywords(payload: dict[str, Any], company: str, max_count: int) -> list[str]:
    rows = payload.get("keywords", []) if isinstance(payload.get("keywords"), list) else []
    normalized_company = normalize_company(company)
    filtered = [
        row
        for row in rows
        if isinstance(row, dict) and normalize_company(str(row.get("company", ""))) == normalized_company
    ]
    filtered.sort(key=lambda r: int(r.get("avg_monthly_searches", 0) or 0), reverse=True)

    seeds: list[str] = []
    for row in filtered:
        keyword = str(row.get("keyword", "")).strip()
        if keyword and keyword not in seeds:
            seeds.append(keyword)
        if len(seeds) >= max_count:
            break
    return seeds


def enrich_serp_and_paa(payload: dict[str, Any], company: str, locale: str, country: str, max_seeds: int) -> dict[str, Any]:
    seeds = top_seed_keywords(payload, company=company, max_count=max_seeds)
    if not seeds:
        return {"ok": False, "reason": "No keyword seeds available for SERP enrichment.", "added_serp": 0, "added_paa": 0}

    existing_serp = payload.get("serp_results", []) if isinstance(payload.get("serp_results"), list) else []
    existing_paa = payload.get("paa_questions", []) if isinstance(payload.get("paa_questions"), list) else []

    seen_serp = {(str(row.get("query", "")).strip(), str(row.get("url", "")).strip()) for row in existing_serp if isinstance(row, dict)}
    seen_paa = {(str(row.get("query", "")).strip(), str(row.get("question", "")).strip()) for row in existing_paa if isinstance(row, dict)}

    added_serp = 0
    added_paa = 0

    for seed in seeds:
        bundle = fetch_serp_bundle(query=seed, locale=locale, country_code=country, num=10)
        for row in bundle.organic:
            key = (str(row.get("query", "")).strip(), str(row.get("url", "")).strip())
            if key in seen_serp:
                continue
            seen_serp.add(key)
            row["company"] = company
            existing_serp.append(row)
            added_serp += 1

        for row in bundle.paa:
            key = (str(row.get("query", "")).strip(), str(row.get("question", "")).strip())
            if key in seen_paa:
                continue
            seen_paa.add(key)
            row["company"] = company
            existing_paa.append(row)
            added_paa += 1

    payload["serp_results"] = existing_serp
    payload["paa_questions"] = existing_paa
    return {"ok": True, "added_serp": added_serp, "added_paa": added_paa, "seeds": seeds}


def enrich_trends(payload: dict[str, Any], company: str, locale: str, country: str, max_seeds: int, sprint_dir: Path) -> dict[str, Any]:
    seeds = top_seed_keywords(payload, company=company, max_count=max_seeds)
    if not seeds:
        return {"ok": False, "reason": "No keyword seeds available for Trends enrichment.", "added_trend_points": 0}

    result = fetch_trends(
        queries=seeds,
        locale=locale,
        geo=country,
        timeframe="today 12-m",
        cache_path=sprint_dir / ".cache" / "trends_cache.json",
    )
    trend_points = payload.get("trend_points", []) if isinstance(payload.get("trend_points"), list) else []
    existing = {
        (str(row.get("query", "")).strip().lower(), str(row.get("date", "")).strip())
        for row in trend_points
        if isinstance(row, dict)
    }

    added = 0
    for row in result.get("trend_points", []):
        if not isinstance(row, dict):
            continue
        key = (str(row.get("query", "")).strip().lower(), str(row.get("date", "")).strip())
        if key in existing:
            continue
        existing.add(key)
        trend_points.append(
            {
                "company": company,
                "query": str(row.get("query", "")).strip(),
                "period": str(row.get("period", "today 12-m")),
                "value": int(row.get("value", 0) or 0),
                "source_file": "autofetch_pytrends",
            }
        )
        added += 1

    payload["trend_points"] = trend_points
    return {"ok": True, "added_trend_points": added, "seeds": seeds}


def run_pipeline_steps(sprint_dir: Path) -> tuple[bool, list[str]]:
    commands = [
        ["python3", str(PROJECT_ROOT / "execution" / "content_planning_cluster.py"), "--sprint", str(sprint_dir)],
        ["python3", str(PROJECT_ROOT / "execution" / "content_planning_gate.py"), "--sprint", str(sprint_dir)],
        ["python3", str(PROJECT_ROOT / "execution" / "content_planning_to_queue.py"), "--sprint", str(sprint_dir)],
    ]
    outputs: list[str] = []
    for cmd in commands:
        code, out, err = run(cmd)
        outputs.append(out.strip())
        if code != 0:
            if err.strip():
                outputs.append(err.strip())
            return False, outputs
    return True, outputs


def first_ready_queue_row(queue_path: Path) -> str:
    if not queue_path.exists():
        return ""
    with queue_path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if str(row.get("workflow_b_ready", "")).strip().lower() == "yes":
                return str(row.get("queue_row_id", "")).strip()
    return ""


def main() -> int:
    args = parse_args()

    init_cmd = [
        "python3",
        str(PROJECT_ROOT / "execution" / "content_planning_init.py"),
        "--companies",
        args.company,
    ]
    if args.sprint_date:
        init_cmd.extend(["--sprint-date", args.sprint_date])
    if args.force:
        init_cmd.append("--force")

    code, out, err = run(init_cmd)
    if code != 0:
        print(out)
        print(err)
        return code

    init_payload = json.loads(out)
    sprint_dir = Path(init_payload["sprint_dir"]).resolve()
    sprint_inputs = sprint_dir / "research_inputs"

    copied = copy_inputs(
        sprint_inputs=sprint_inputs,
        company=args.company,
        keyword_files=args.keyword_files,
        extra_files=args.extra_files,
    )
    if copied["keyword"] == 0:
        print("ERROR: no valid keyword CSVs detected. Provide keyword exports in --keyword-files.")
        return 1

    ingest_cmd = [
        "python3",
        str(PROJECT_ROOT / "execution" / "content_planning_ingest.py"),
        "--sprint",
        str(sprint_dir),
    ]
    code, out, err = run(ingest_cmd)
    if code != 0:
        print(out)
        print(err)
        return code

    ingest_payload = json.loads(out)
    dataset_path = Path(ingest_payload["dataset_path"]).resolve()
    dataset = load_dataset(dataset_path)
    set_default_company(dataset, args.company)

    enrichment_log: dict[str, Any] = {"copied": copied}

    if not args.skip_auto_serp:
        try:
            serp_info = enrich_serp_and_paa(
                dataset,
                company=args.company,
                locale=args.locale,
                country=args.country,
                max_seeds=args.max_serp_seeds,
            )
            enrichment_log["serp_paa"] = serp_info
        except SerpProviderError as exc:
            enrichment_log["serp_paa"] = {"ok": False, "reason": str(exc)}

    if not args.skip_auto_trends:
        try:
            trends_info = enrich_trends(
                dataset,
                company=args.company,
                locale=args.locale,
                country=args.country,
                max_seeds=args.max_trends_seeds,
                sprint_dir=sprint_dir,
            )
            enrichment_log["trends"] = trends_info
        except TrendsProviderError as exc:
            enrichment_log["trends"] = {"ok": False, "reason": str(exc)}

    save_dataset(dataset_path, dataset)

    ok, outputs = run_pipeline_steps(sprint_dir)

    queue_path = sprint_dir / "run_queue.csv"
    queue_row = first_ready_queue_row(queue_path)

    summary = {
        "ok": ok,
        "sprint_dir": str(sprint_dir),
        "dataset_path": str(dataset_path),
        "enrichment": enrichment_log,
        "queue_path": str(queue_path),
        "first_ready_queue_row_id": queue_row,
        "next_step": (
            f"python3 execution/prepare_article_from_queue.py --queue-row-id '{queue_row}'"
            if queue_row
            else "Fix planning gate errors and rerun autopilot."
        ),
        "pipeline_logs": outputs,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
