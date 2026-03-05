#!/usr/bin/env python3
"""Resolve company profile snapshot from machine-readable company_context_profiles.yaml."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROFILES_PATH = PROJECT_ROOT / "Agentic Articles" / "docs" / "company_context_profiles.yaml"


class CompanyProfileResolutionError(RuntimeError):
    """Raised when company profile cannot be resolved unambiguously."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve company profile by natural-language company name.")
    parser.add_argument("--company", required=True, help="Company name provided in natural language.")
    parser.add_argument("--profiles-file", type=Path, default=DEFAULT_PROFILES_PATH)
    parser.add_argument("--workspace", type=Path, default=None, help="Optional workspace path to save company_profile_snapshot.json")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def normalize(value: str) -> str:
    lowered = value.strip().lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_text = re.sub(r"\s+", " ", ascii_text)
    return ascii_text


def load_profiles(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise CompanyProfileResolutionError(f"Profiles file not found: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CompanyProfileResolutionError(
            "company_context_profiles.yaml must be machine-readable JSON-compatible YAML."
        ) from exc

    if not isinstance(payload, dict):
        raise CompanyProfileResolutionError("Profiles root must be an object.")

    profiles = payload.get("profiles", [])
    if not isinstance(profiles, list) or not profiles:
        raise CompanyProfileResolutionError("Profiles file must contain non-empty 'profiles' list.")

    normalized_profiles: list[dict[str, Any]] = []
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        profile_id = str(profile.get("profile_id", "")).strip()
        company = str(profile.get("company", "")).strip()
        aliases = profile.get("aliases", [])
        if not profile_id or not company:
            continue
        alias_values = []
        if isinstance(aliases, list):
            alias_values = [str(item).strip() for item in aliases if str(item).strip()]

        normalized_profiles.append(
            {
                **profile,
                "profile_id": profile_id,
                "company": company,
                "aliases": alias_values,
                "_company_norm": normalize(company),
                "_aliases_norm": [normalize(alias) for alias in alias_values],
            }
        )

    if not normalized_profiles:
        raise CompanyProfileResolutionError("No valid profiles found in profiles file.")

    return normalized_profiles


def _dedupe_profiles(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        profile_id = str(item.get("profile_id", "")).strip()
        if not profile_id or profile_id in seen:
            continue
        seen.add(profile_id)
        out.append(item)
    return out


def resolve_profile(company_input: str, profiles: list[dict[str, Any]]) -> dict[str, Any]:
    user_norm = normalize(company_input)
    if not user_norm:
        raise CompanyProfileResolutionError("Company input is empty after normalization.")

    exact_matches: list[dict[str, Any]] = []
    for profile in profiles:
        if user_norm == profile.get("_company_norm"):
            exact_matches.append(profile)
            continue
        aliases_norm = profile.get("_aliases_norm", [])
        if isinstance(aliases_norm, list) and user_norm in aliases_norm:
            exact_matches.append(profile)

    exact_matches = _dedupe_profiles(exact_matches)
    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(exact_matches) > 1:
        raise CompanyProfileResolutionError(
            "Ambiguous company alias (exact). Matches: "
            + ", ".join(str(item.get("profile_id", "")) for item in exact_matches)
        )

    contains_matches: list[dict[str, Any]] = []
    for profile in profiles:
        company_norm = str(profile.get("_company_norm", ""))
        aliases_norm = profile.get("_aliases_norm", [])
        if company_norm and (company_norm in user_norm or user_norm in company_norm):
            contains_matches.append(profile)
            continue
        if isinstance(aliases_norm, list):
            for alias_norm in aliases_norm:
                if alias_norm and (alias_norm in user_norm or user_norm in alias_norm):
                    contains_matches.append(profile)
                    break

    contains_matches = _dedupe_profiles(contains_matches)
    if len(contains_matches) == 1:
        return contains_matches[0]
    if len(contains_matches) > 1:
        raise CompanyProfileResolutionError(
            "Ambiguous company alias (contains). Matches: "
            + ", ".join(str(item.get("profile_id", "")) for item in contains_matches)
        )

    raise CompanyProfileResolutionError(f"No company profile match found for input: {company_input}")


def build_snapshot(profile: dict[str, Any], company_input: str) -> dict[str, Any]:
    services = profile.get("services", []) if isinstance(profile.get("services"), list) else []
    service_links = [
        str(item.get("service_url", "")).strip()
        for item in services
        if isinstance(item, dict) and str(item.get("service_url", "")).strip()
    ]
    explicit_links = profile.get("allowed_service_links", [])
    if isinstance(explicit_links, list):
        service_links.extend([str(item).strip() for item in explicit_links if str(item).strip()])
    allowed_links = list(dict.fromkeys(service_links))

    brand_voice = profile.get("brand_voice", {}) if isinstance(profile.get("brand_voice"), dict) else {}
    tone_rules = brand_voice.get("tone_rules", []) if isinstance(brand_voice.get("tone_rules"), list) else []
    avoid_rules = brand_voice.get("avoid_rules", []) if isinstance(brand_voice.get("avoid_rules"), list) else []

    cta = profile.get("default_cta", {}) if isinstance(profile.get("default_cta"), dict) else {}

    legal_notes = profile.get("legal_compliance_notes", [])
    if not isinstance(legal_notes, list):
        legal_notes = []

    excluded_claims = profile.get("excluded_topics_or_claims", [])
    if not isinstance(excluded_claims, list):
        excluded_claims = []

    return {
        "resolved_from_input": company_input,
        "company_profile_id": str(profile.get("profile_id", "")).strip(),
        "company": str(profile.get("company", "")).strip(),
        "website_domain": str(profile.get("website_domain", "")).strip(),
        "primary_locations": [str(item).strip() for item in profile.get("primary_locations", []) if str(item).strip()]
        if isinstance(profile.get("primary_locations"), list)
        else [],
        "brand_voice": {
            "name": str(brand_voice.get("name", "")).strip(),
            "narrator": str(brand_voice.get("narrator", "")).strip(),
            "tone_rules": [str(item).strip() for item in tone_rules if str(item).strip()],
            "avoid_rules": [str(item).strip() for item in avoid_rules if str(item).strip()],
            "requires_second_person": bool(brand_voice.get("requires_second_person", False)),
            "second_person_min_hits": int(brand_voice.get("second_person_min_hits", 0) or 0),
        },
        "default_cta": {
            "tofu": str(cta.get("tofu", "")).strip(),
            "mofu": str(cta.get("mofu", "")).strip(),
            "bofu": str(cta.get("bofu", "")).strip(),
        },
        "legal_notes": [str(item).strip() for item in legal_notes if str(item).strip()],
        "excluded_claims": [str(item).strip() for item in excluded_claims if str(item).strip()],
        "allowed_service_links": allowed_links,
    }


def resolve_company_profile(company_input: str, profiles_file: Path = DEFAULT_PROFILES_PATH) -> dict[str, Any]:
    profiles = load_profiles(profiles_file)
    profile = resolve_profile(company_input, profiles)
    return build_snapshot(profile, company_input=company_input)


def main() -> int:
    args = parse_args()
    try:
        snapshot = resolve_company_profile(args.company.strip(), profiles_file=args.profiles_file.resolve())
    except CompanyProfileResolutionError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.workspace:
        workspace = args.workspace.resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        out_path = workspace / "company_profile_snapshot.json"
        out_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    else:
        print(f"company_profile_id: {snapshot['company_profile_id']}")
        print(f"company: {snapshot['company']}")
        print(f"allowed_service_links: {len(snapshot['allowed_service_links'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
