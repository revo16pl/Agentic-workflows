#!/usr/bin/env python3
"""Competitor matrix builder for SERP top results."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class CompetitorRow:
    url: str
    word_count: int
    h2_count: int
    faq_count: int
    local_signals_count: int
    cta_type: str
    content_gaps: list[str]


DEFAULT_TIMEOUT_SECONDS = 20


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w\-ąćęłńóśżźĄĆĘŁŃÓŚŻŹ]+\b", text, flags=re.UNICODE))


def _extract_text_metrics(html: str, city_or_region: str, company_name: str) -> tuple[int, int, int, int, str]:
    try:
        from bs4 import BeautifulSoup
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Missing dependency: beautifulsoup4. Install with `pip install beautifulsoup4`.") from exc

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text_low = text.lower()

    h2_count = len(soup.find_all("h2"))
    faq_count = len(re.findall(r"\?", text)) + len(re.findall(r"\bfaq\b", text_low))

    local_terms = [city_or_region.strip().lower(), company_name.strip().lower()]
    local_signals_count = 0
    for term in local_terms:
        if term:
            local_signals_count += text_low.count(term)

    cta_patterns = {
        "hard": ["kup", "zamów", "zamow", "zarezerwuj", "book now"],
        "medium": ["umów", "umow", "rezerw", "skontaktuj", "kontakt"],
        "soft": ["dowiedz", "sprawdź", "sprawdz", "czytaj", "poznaj"],
    }
    cta_type = "none"
    for candidate, patterns in cta_patterns.items():
        if any(pattern in text_low for pattern in patterns):
            cta_type = candidate
            break

    return _word_count(text), h2_count, faq_count, local_signals_count, cta_type


def _derive_row_gaps(*, word_count: int, faq_count: int, local_signals_count: int, h2_count: int) -> list[str]:
    gaps: list[str] = []
    if word_count < 900:
        gaps.append("niska_glebokosc_tresci")
    if faq_count < 4:
        gaps.append("slabe_pokrycie_pytan_uzytkownikow")
    if local_signals_count < 2:
        gaps.append("niski_kontekst_lokalny")
    if h2_count < 4:
        gaps.append("slaba_struktura_naglowkow")
    return gaps


def build_competitor_matrix(
    *,
    urls: list[str],
    city_or_region: str,
    company_name: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[list[dict[str, Any]], list[str]]:
    matrix: list[dict[str, Any]] = []
    gap_counter: dict[str, int] = {}

    unique_urls = list(dict.fromkeys([u.strip() for u in urls if u.strip()]))[:20]

    for url in unique_urls:
        try:
            response = requests.get(
                url,
                timeout=timeout_seconds,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
                    )
                },
            )
            if response.status_code >= 400:
                continue
            html = response.text

            word_count, h2_count, faq_count, local_signals_count, cta_type = _extract_text_metrics(
                html=html,
                city_or_region=city_or_region,
                company_name=company_name,
            )
            row_gaps = _derive_row_gaps(
                word_count=word_count,
                faq_count=faq_count,
                local_signals_count=local_signals_count,
                h2_count=h2_count,
            )
            for gap in row_gaps:
                gap_counter[gap] = gap_counter.get(gap, 0) + 1

            matrix.append(
                CompetitorRow(
                    url=url,
                    word_count=word_count,
                    h2_count=h2_count,
                    faq_count=faq_count,
                    local_signals_count=local_signals_count,
                    cta_type=cta_type,
                    content_gaps=row_gaps,
                ).__dict__
            )
        except Exception:
            continue

    sorted_gaps = sorted(gap_counter.items(), key=lambda x: (-x[1], x[0]))
    top_gaps = [name for name, _ in sorted_gaps[:10]]
    return matrix, top_gaps
