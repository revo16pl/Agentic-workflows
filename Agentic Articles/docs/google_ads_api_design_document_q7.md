# Google Ads API Tool Design Documentation (Q7)

## 1. Tool Purpose

This internal tool supports SEO content planning for two local Polish businesses.  
Its goal is to improve article topic selection using real keyword demand data instead of guesses.

Main use case:
- gather keyword ideas and historical keyword metrics for Polish market (`pl-PL`, `PL`)
- map search intent for article briefs
- support editorial planning for SEO articles

This tool is not a campaign management platform. It is a research support layer for content strategy.

## 2. Who Uses the Tool

Access model:
- internal users only (owner + authorized team collaborators)
- no public user access
- no external client self-service dashboard

Users operate the tool through local scripts in a controlled project environment.

## 3. Google Ads API Scope and Endpoints Used

The tool uses Google Ads API only for keyword research.

Primary services:
- `KeywordPlanIdeaService.GenerateKeywordIdeas`
- `KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics`

Data points consumed:
- keyword text
- average monthly searches
- competition level
- top of page bid ranges (low/high)
- language/location filtered outputs (Poland)

Purpose of these calls:
- build keyword clusters
- improve intent matching
- prioritize article topics

## 4. Explicitly Not Used

The tool does not use Google Ads API for:
- campaign creation or editing
- ad group creation or editing
- ad creation or editing
- budget or bidding automation
- account billing operations
- user/permission management in Google Ads
- conversion tracking configuration
- remarketing setup

No automation is performed on paid campaign delivery.

## 5. System Architecture and Data Flow

High-level flow:
1. Internal user provides topic seed (for example: local service topic in Polish).
2. Tool calls Google Ads API keyword planning endpoints.
3. Tool normalizes returned metrics into local research artifacts.
4. Results are merged with SERP and trends data from other providers.
5. Research outputs are used to prepare article brief and content outline.
6. Final article draft is reviewed and exported to Google Docs.

Data handling:
- keyword metrics are stored in local workspace artifacts (JSON/Markdown)
- data is used for planning and QA only
- no resale or republishing of raw API output

## 6. Security and Access Controls

Authentication and authorization:
- OAuth 2.0 credentials are used for API access
- developer token is stored in environment variables
- refresh tokens are used only in trusted local runtime

Secret handling:
- secrets are kept in local `.env` and credential files excluded from git
- tokens are never hardcoded in source code
- tokens are never shared publicly

Operational controls:
- only authorized internal users can run scripts
- no multi-tenant public exposure
- no end-user direct access to credentials

## 7. Compliance and Data Minimization

Data minimization principles:
- only required fields are fetched
- only keyword research metrics needed for editorial planning are retained
- no unnecessary personal data processing

Usage constraints:
- API output supports internal SEO planning decisions
- tool behavior remains read-focused for keyword research

## 8. Reliability and Error Handling

The tool includes:
- input validation (topic, locale, geo parameters)
- retry and backoff for temporary provider failures
- hard fail behavior when critical research data is unavailable
- explicit logs for troubleshooting and auditability

If the keyword data fetch fails, article generation is blocked until research quality gates pass.

## 9. Summary

This is an internal SEO research tool that uses Google Ads API in a limited and controlled way for keyword planning only.  
It does not manage ads or billing, does not expose public access, and applies OAuth-based security with strict secret handling.