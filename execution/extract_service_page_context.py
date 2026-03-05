#!/usr/bin/env python3
"""Extract structured service-page context from URL.

Primary mode tries Playwright rendering. If unavailable, falls back to curl + HTML parsing.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_TAB_LABELS = [
    "Wskazania",
    "Przeciwwskazania i bezpieczeństwo",
    "Zalecenia przed i po",
    "FAQ",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract context from service page URL.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", type=Path, default=None, help="Optional output JSON path.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    return parser.parse_args()


def _strip_tags(value: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", value)
    clean = html.unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _extract_with_regex(document_html: str, url: str, extractor_mode: str) -> dict[str, Any]:
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", document_html, flags=re.S | re.I)
    h1_text = _strip_tags(h1_match.group(1)) if h1_match else ""

    lead_match = re.search(r"service-page-hero_lead[^>]*>(.*?)</p>", document_html, flags=re.S | re.I)
    if not lead_match:
        lead_match = re.search(r"<section[^>]*service-page-hero[^>]*>.*?<p[^>]*>(.*?)</p>", document_html, flags=re.S | re.I)
    lead_text = _strip_tags(lead_match.group(1)) if lead_match else ""

    desc_block = re.search(
        r'data-testid="service-page-description-text"[^>]*>(.*?)</div>\s*</div>\s*</div>',
        document_html,
        flags=re.S | re.I,
    )
    description_paragraphs: list[str] = []
    if desc_block:
        for paragraph in re.findall(r"<p[^>]*>(.*?)</p>", desc_block.group(1), flags=re.S | re.I):
            text = _strip_tags(paragraph)
            if text:
                description_paragraphs.append(text)

    tab_labels = []
    for raw in re.findall(
        r'data-testid="service-page-tab-\d+"[^>]*>(.*?)</button>',
        document_html,
        flags=re.S | re.I,
    ):
        label = _strip_tags(raw)
        if label:
            tab_labels.append(label)
    tab_labels = list(dict.fromkeys(tab_labels))
    if not tab_labels:
        tab_labels = list(DEFAULT_TAB_LABELS)

    desc_text = " ".join(description_paragraphs).strip()
    lead_words = re.findall(r"\S+", lead_text)
    desc_words = re.findall(r"\S+", desc_text)

    return {
        "source_url": url,
        "source_domain": urlparse(url).netloc,
        "extracted_at": now_iso(),
        "extractor_mode": extractor_mode,
        "h1": h1_text,
        "subheading": {
            "text": lead_text,
            "chars": len(lead_text),
            "words": len(lead_words),
        },
        "description": {
            "paragraphs": description_paragraphs,
            "paragraph_count": len(description_paragraphs),
            "total_chars": len(desc_text),
            "total_words": len(desc_words),
        },
        "tab_labels": tab_labels,
    }


def _extract_via_playwright(url: str) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(f"Playwright unavailable: {exc}") from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(1200)
        document_html = page.content()
        browser.close()
    return _extract_with_regex(document_html=document_html, url=url, extractor_mode="playwright")


def _extract_via_curl(url: str) -> dict[str, Any]:
    process = subprocess.run(
        ["curl", "-L", "-s", "-A", "Mozilla/5.0", url],
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0 or not process.stdout.strip():
        raise RuntimeError(process.stderr.strip() or "curl returned no data")
    return _extract_with_regex(document_html=process.stdout, url=url, extractor_mode="curl")


def extract_service_page_context(url: str) -> dict[str, Any]:
    try:
        return _extract_via_playwright(url)
    except Exception:
        return _extract_via_curl(url)


def main() -> int:
    args = parse_args()
    payload = extract_service_page_context(args.url.strip())

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json or not args.out:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Saved context: {args.out.resolve()}")
        print(f"- extractor_mode: {payload.get('extractor_mode', '')}")
        print(f"- h1: {payload.get('h1', '')}")
        print(f"- tab_labels: {', '.join(payload.get('tab_labels', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
