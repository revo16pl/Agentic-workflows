#!/usr/bin/env python3
"""Google Trends provider via pytrends with retry/backoff/cache."""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class TrendsProviderError(RuntimeError):
    """Raised when trend fetch fails."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _cache_key(locale: str, geo: str, timeframe: str, queries: list[str]) -> str:
    payload = json.dumps(
        {
            "locale": locale,
            "geo": geo,
            "timeframe": timeframe,
            "queries": sorted(set(queries)),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_cache(cache_path: Path) -> dict[str, Any]:
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _save_cache(cache_path: Path, payload: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _is_cache_fresh(entry: dict[str, Any], ttl_hours: int) -> bool:
    created_at = str(entry.get("created_at", ""))
    if not created_at:
        return False
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(timezone.utc) - created <= timedelta(hours=ttl_hours)


def fetch_trends(
    *,
    queries: list[str],
    locale: str = "pl-PL",
    geo: str = "PL",
    timeframe: str = "today 12-m",
    cache_path: Path | None = None,
) -> dict[str, Any]:
    if not queries:
        raise TrendsProviderError("queries list is empty.")

    unique_queries = list(dict.fromkeys([q.strip() for q in queries if q.strip()]))
    if not unique_queries:
        raise TrendsProviderError("queries list has no valid query strings.")

    ttl_hours = int(os.getenv("RESEARCH_CACHE_TTL_HOURS", "24"))
    retry_max = int(os.getenv("RESEARCH_RETRY_MAX", "3"))
    backoff = int(os.getenv("RESEARCH_BACKOFF_SECONDS", "2"))

    cache_path = cache_path or Path(".tmp/research/trends_cache.json")
    cache = _load_cache(cache_path)
    key = _cache_key(locale=locale, geo=geo, timeframe=timeframe, queries=unique_queries)
    cached_entry = cache.get(key)
    if isinstance(cached_entry, dict) and _is_cache_fresh(cached_entry, ttl_hours):
        return cached_entry.get("payload", {})

    try:
        from pytrends.request import TrendReq
    except Exception as exc:  # pragma: no cover
        raise TrendsProviderError("pytrends dependency missing. Install with `pip install pytrends`.") from exc

    last_error = ""
    for attempt in range(1, retry_max + 1):
        try:
            trends = TrendReq(hl=locale, tz=360)
            points: list[dict[str, Any]] = []
            rising: list[str] = []
            top: list[str] = []

            for query in unique_queries:
                trends.build_payload([query], timeframe=timeframe, geo=geo)

                iot = trends.interest_over_time()
                if iot is not None and not iot.empty:
                    for timestamp, row in iot.iterrows():
                        if query not in row:
                            continue
                        points.append(
                            {
                                "query": query,
                                "period": timeframe,
                                "date": timestamp.isoformat(),
                                "value": int(row[query]),
                                "source_tool": "pytrends",
                            }
                        )

                rq = trends.related_queries()
                bucket = rq.get(query, {}) if isinstance(rq, dict) else {}

                top_df = bucket.get("top") if isinstance(bucket, dict) else None
                if top_df is not None and hasattr(top_df, "iterrows"):
                    for _, row in top_df.head(10).iterrows():
                        value = str(row.get("query", "")).strip()
                        if value:
                            top.append(value)

                rising_df = bucket.get("rising") if isinstance(bucket, dict) else None
                if rising_df is not None and hasattr(rising_df, "iterrows"):
                    for _, row in rising_df.head(10).iterrows():
                        value = str(row.get("query", "")).strip()
                        if value:
                            rising.append(value)

            payload = {
                "queries": unique_queries,
                "locale": locale,
                "geo": geo,
                "timeframe": timeframe,
                "trend_points": points,
                "related_top_queries": list(dict.fromkeys(top)),
                "related_rising_queries": list(dict.fromkeys(rising)),
                "source_tool": "pytrends",
                "pulled_at": _now_iso(),
            }

            cache[key] = {"created_at": _now_iso(), "payload": payload}
            _save_cache(cache_path, cache)
            return payload
        except Exception as exc:  # pragma: no cover
            last_error = str(exc)
            if attempt < retry_max:
                time.sleep(backoff * attempt)

    raise TrendsProviderError(f"pytrends fetch failed after {retry_max} attempts: {last_error}")
