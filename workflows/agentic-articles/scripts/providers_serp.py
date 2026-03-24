#!/usr/bin/env python3
"""SERP providers (Serper primary, SerpApi fallback) for Agentic Articles research."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_TIMEOUT_SECONDS = 30


class SerpProviderError(RuntimeError):
    """Raised when SERP providers cannot return valid data."""


@dataclass
class SerpBundle:
    provider: str
    query: str
    organic: list[dict[str, Any]]
    paa: list[dict[str, Any]]
    related: list[str]


def _domain_from_url(url: str) -> str:
    try:
        from urllib.parse import urlparse

        return (urlparse(url).netloc or "").lower()
    except Exception:
        return ""


def fetch_serper(
    *,
    query: str,
    locale: str,
    country_code: str,
    num: int = 10,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> SerpBundle:
    api_key = os.getenv("SERPER_API_KEY", "").strip()
    if not api_key:
        raise SerpProviderError("SERPER_API_KEY is not set.")

    lang = (locale.split("-")[0] if "-" in locale else locale).lower() or "pl"
    gl = country_code.lower() or "pl"

    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "hl": lang, "gl": gl, "num": num},
        timeout=timeout_seconds,
    )
    if response.status_code >= 400:
        raise SerpProviderError(f"Serper HTTP {response.status_code}: {response.text[:300]}")

    payload = response.json()
    organic: list[dict[str, Any]] = []
    for idx, item in enumerate(payload.get("organic", [])[:num], start=1):
        url = str(item.get("link", "")).strip()
        if not url:
            continue
        organic.append(
            {
                "query": query,
                "rank": idx,
                "title": str(item.get("title", "")).strip(),
                "url": url,
                "domain": _domain_from_url(url),
                "snippet": str(item.get("snippet", "")).strip(),
                "source_tool": "serper",
            }
        )

    paa: list[dict[str, Any]] = []
    for item in payload.get("peopleAlsoAsk", []):
        question = str(item.get("question", "")).strip()
        if not question:
            continue
        paa.append(
            {
                "query": query,
                "question": question,
                "source_tool": "serper",
            }
        )

    related = []
    for item in payload.get("relatedSearches", []):
        if isinstance(item, dict):
            q = str(item.get("query", "")).strip()
        else:
            q = str(item).strip()
        if q:
            related.append(q)

    return SerpBundle(provider="serper", query=query, organic=organic, paa=paa, related=related)


def fetch_serpapi(
    *,
    query: str,
    locale: str,
    country_code: str,
    num: int = 10,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> SerpBundle:
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        raise SerpProviderError("SERPAPI_API_KEY is not set.")

    lang = (locale.split("-")[0] if "-" in locale else locale).lower() or "pl"
    gl = country_code.lower() or "pl"

    response = requests.get(
        "https://serpapi.com/search.json",
        params={
            "engine": "google",
            "q": query,
            "hl": lang,
            "gl": gl,
            "num": num,
            "api_key": api_key,
        },
        timeout=timeout_seconds,
    )
    if response.status_code >= 400:
        raise SerpProviderError(f"SerpApi HTTP {response.status_code}: {response.text[:300]}")

    payload = response.json()
    organic: list[dict[str, Any]] = []
    for idx, item in enumerate(payload.get("organic_results", [])[:num], start=1):
        url = str(item.get("link", "")).strip()
        if not url:
            continue
        organic.append(
            {
                "query": query,
                "rank": idx,
                "title": str(item.get("title", "")).strip(),
                "url": url,
                "domain": _domain_from_url(url),
                "snippet": str(item.get("snippet", "")).strip(),
                "source_tool": "serpapi",
            }
        )

    paa: list[dict[str, Any]] = []
    for item in payload.get("related_questions", []):
        question = str(item.get("question", "")).strip()
        if not question:
            continue
        paa.append(
            {
                "query": query,
                "question": question,
                "source_tool": "serpapi",
            }
        )

    related: list[str] = []
    for item in payload.get("related_searches", []):
        q = str(item.get("query", "")).strip() if isinstance(item, dict) else str(item).strip()
        if q:
            related.append(q)

    return SerpBundle(provider="serpapi", query=query, organic=organic, paa=paa, related=related)


def fetch_serp_bundle(
    *,
    query: str,
    locale: str,
    country_code: str,
    num: int = 10,
) -> SerpBundle:
    errors: list[str] = []

    try:
        return fetch_serper(query=query, locale=locale, country_code=country_code, num=num)
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        errors.append(f"serper: {exc}")

    try:
        return fetch_serpapi(query=query, locale=locale, country_code=country_code, num=num)
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        errors.append(f"serpapi: {exc}")

    raise SerpProviderError("All SERP providers failed. " + " | ".join(errors))
