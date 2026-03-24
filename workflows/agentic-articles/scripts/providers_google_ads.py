#!/usr/bin/env python3
"""Google Ads Keyword Planner provider for Agentic Articles research."""

from __future__ import annotations

import os
from typing import Any


class GoogleAdsProviderError(RuntimeError):
    """Raised for Google Ads provider failures."""


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise GoogleAdsProviderError(f"Missing required env: {name}")
    return value


def _build_client():
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except Exception as exc:  # pragma: no cover - import/runtime dependency
        raise GoogleAdsProviderError(
            "google-ads dependency is missing. Install with `pip install google-ads`."
        ) from exc

    config = {
        "developer_token": _required_env("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": _required_env("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": _required_env("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": _required_env("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }
    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip().replace("-", "")
    if login_customer_id:
        config["login_customer_id"] = login_customer_id

    try:
        return GoogleAdsClient.load_from_dict(config)
    except Exception as exc:  # pragma: no cover
        raise GoogleAdsProviderError(f"Failed to initialize Google Ads client: {exc}") from exc


def _normalize_customer_id(raw: str) -> str:
    return raw.replace("-", "").strip()


def _chunked(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_keyword_metrics(
    *,
    seed_keywords: list[str],
    locale: str = "pl-PL",
    country_code: str = "PL",
    target_count: int = 120,
) -> list[dict[str, Any]]:
    if not seed_keywords:
        raise GoogleAdsProviderError("seed_keywords list is empty.")

    customer_id = _normalize_customer_id(_required_env("GOOGLE_ADS_CUSTOMER_ID"))
    client = _build_client()

    # Google Ads constant ids used in API docs examples.
    # Polish language = 1000, Poland geo target = 2616.
    language_id = int(os.getenv("GOOGLE_ADS_LANGUAGE_ID", "1000"))
    location_id = int(os.getenv("GOOGLE_ADS_LOCATION_ID", "2616"))

    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    geo_target_service = client.get_service("GeoTargetConstantService")
    language_service = client.get_service("LanguageConstantService")

    language_rn = language_service.language_constant_path(str(language_id))
    location_rn = geo_target_service.geo_target_constant_path(str(location_id))

    # 1) Expand ideas from seed keywords.
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = language_rn
    request.geo_target_constants.append(location_rn)
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH

    keyword_seed = client.get_type("KeywordSeed")
    for seed in list(dict.fromkeys([x.strip() for x in seed_keywords if x.strip()]))[:20]:
        keyword_seed.keywords.append(seed)
    request.keyword_seed = keyword_seed

    try:
        ideas = keyword_plan_idea_service.generate_keyword_ideas(request=request)
    except Exception as exc:  # pragma: no cover - runtime/API
        raise GoogleAdsProviderError(f"GenerateKeywordIdeas failed: {exc}") from exc

    expanded: list[str] = []
    for row in ideas:
        text = str(getattr(row, "text", "") or "").strip()
        if text:
            expanded.append(text)
        if len(expanded) >= target_count:
            break

    candidates = list(dict.fromkeys([*seed_keywords, *expanded]))[: max(target_count, 40)]
    if not candidates:
        raise GoogleAdsProviderError("Google Ads returned no keyword ideas.")

    # 2) Pull historical metrics for expanded set.
    out: list[dict[str, Any]] = []
    for chunk in _chunked(candidates, 200):
        metrics_request = client.get_type("GenerateKeywordHistoricalMetricsRequest")
        metrics_request.customer_id = customer_id
        metrics_request.language = language_rn
        metrics_request.geo_target_constants.append(location_rn)
        metrics_request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        for kw in chunk:
            metrics_request.keywords.append(kw)

        try:
            response = keyword_plan_idea_service.generate_keyword_historical_metrics(request=metrics_request)
        except Exception as exc:  # pragma: no cover
            raise GoogleAdsProviderError(f"GenerateKeywordHistoricalMetrics failed: {exc}") from exc

        for result in response.results:
            metrics = result.keyword_metrics
            competition = str(metrics.competition.name) if metrics and metrics.competition else "UNSPECIFIED"
            out.append(
                {
                    "keyword": str(result.text),
                    "avg_monthly_searches": int(getattr(metrics, "avg_monthly_searches", 0) or 0),
                    "competition": competition,
                    "top_of_page_bid_low_micros": int(getattr(metrics, "low_top_of_page_bid_micros", 0) or 0),
                    "top_of_page_bid_high_micros": int(getattr(metrics, "high_top_of_page_bid_micros", 0) or 0),
                    "source_tool": "google_ads_api",
                    "locale": locale,
                    "country": country_code,
                }
            )

    if not out:
        raise GoogleAdsProviderError("No keyword metrics returned by Google Ads API.")

    # Keep strongest first, then deterministic tie-break by keyword.
    out.sort(key=lambda x: (-int(x.get("avg_monthly_searches", 0)), str(x.get("keyword", ""))))
    return out[: max(target_count, 40)]
