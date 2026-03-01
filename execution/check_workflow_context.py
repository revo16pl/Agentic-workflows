#!/usr/bin/env python3
"""Validate workflow context (skills + research evidence) and update quality gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from article_workflow_state import set_many_gates

REQUIRED_SKILLS = [
    "content-strategy",
    "copywriting",
    "copy-editing",
    "seo-audit",
    "schema-markup",
    "ai-seo",
]

DEFAULT_MINIMUM_DATASET = {
    "serp_top10_urls": 10,
    "keyword_phrases": 30,
    "paa_questions": 10,
    "trend_queries": 5,
    "keyword_metrics": 40,
    "serp_results": 30,
    "competitor_matrix": 10,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Context/evidence gate checker.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", default="workflow_context_report.md")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def parse_run_context(path: Path) -> dict[str, str]:
    output: dict[str, str] = {}
    if not path.exists():
        return output
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        output[key.strip()] = value.strip()
    return output


def comma_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def evaluate_skills(workspace: Path) -> tuple[bool, list[str]]:
    context = parse_run_context(workspace / "run_context.md")
    messages: list[str] = []
    loaded = set(comma_list(context.get("skills_loaded")))
    applied = set(comma_list(context.get("skills_applied")))
    data_mode = context.get("data_mode", "")
    ok = True

    if data_mode != "external_only":
        ok = False
        messages.append("run_context.md must contain data_mode: external_only.")

    providers_loaded = context.get("research_providers_loaded", "").strip().lower()
    if not providers_loaded:
        ok = False
        messages.append("run_context.md must contain research_providers_loaded after research_fetch.")
    else:
        required_providers = ["google_ads_keyword_planner_api", "serper", "pytrends"]
        missing_providers = [provider for provider in required_providers if provider not in providers_loaded]
        if missing_providers:
            ok = False
            messages.append("run_context.md research_providers_loaded missing: " + ", ".join(missing_providers))

    fetch_status = context.get("research_fetch_status", "").strip().lower()
    if fetch_status != "ok":
        ok = False
        messages.append("run_context.md research_fetch_status must be 'ok'.")

    missing_loaded = [skill for skill in REQUIRED_SKILLS if skill not in loaded]
    if missing_loaded:
        ok = False
        messages.append("Missing loaded skills: " + ", ".join(missing_loaded))

    missing_applied = [skill for skill in REQUIRED_SKILLS if skill not in applied]
    if missing_applied:
        ok = False
        messages.append("Missing applied skills: " + ", ".join(missing_applied))

    project_root = workspace.parents[2] if len(workspace.parents) >= 3 else workspace.parent
    local_missing: list[str] = []
    for skill in REQUIRED_SKILLS:
        skill_file = project_root / "skills" / skill / "SKILL.md"
        if not skill_file.exists():
            local_missing.append(skill)
    if local_missing:
        ok = False
        messages.append("Missing local skill installs in ./skills: " + ", ".join(local_missing))

    if ok:
        messages.append("All required skills are loaded and applied.")
    return ok, messages


def evaluate_evidence(workspace: Path) -> tuple[bool, list[str]]:
    manifest_path = workspace / "research_evidence_manifest.json"
    if not manifest_path.exists():
        return False, ["Missing research_evidence_manifest.json."]
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [f"Invalid JSON in research_evidence_manifest.json: {exc}"]

    messages: list[str] = []
    ok = True
    if not isinstance(payload, dict):
        return False, ["research_evidence_manifest.json must contain a JSON object."]
    if str(payload.get("data_mode", "")).strip() != "external_only":
        ok = False
        messages.append("data_mode in research_evidence_manifest.json must be external_only.")

    version = str(payload.get("version", "")).strip()
    if version == "3.0":
        providers = payload.get("providers", {})
        if not isinstance(providers, dict):
            ok = False
            messages.append("providers section is required for manifest v3.0.")
        else:
            required_provider_keys = ["keyword_metrics", "serp", "serp_fallback", "trends"]
            missing_provider_keys = [k for k in required_provider_keys if not str(providers.get(k, "")).strip()]
            if missing_provider_keys:
                ok = False
                messages.append("providers missing keys: " + ", ".join(missing_provider_keys))

        query_seeds = payload.get("query_seeds", [])
        if not isinstance(query_seeds, list) or len(query_seeds) < 3:
            ok = False
            messages.append("query_seeds must contain at least 3 entries for manifest v3.0.")

    minimum = payload.get("minimum_dataset", {})
    minimum = minimum if isinstance(minimum, dict) else {}

    keyword_metrics = payload.get("keyword_metrics", [])
    serp_results = payload.get("serp_results", [])
    competitor_matrix = payload.get("competitor_matrix", [])
    serp_urls = payload.get("serp_urls", [])
    keyword_phrases = payload.get("keyword_phrases", [])
    paa_questions = payload.get("paa_questions", [])
    trend_points = payload.get("trend_points", [])
    trend_queries = payload.get("trend_queries", [])

    def safe_len(value: object) -> int:
        return len(value) if isinstance(value, list) else 0

    trend_query_count = 0
    if isinstance(trend_points, list):
        unique_queries = set()
        for point in trend_points:
            if isinstance(point, dict):
                query = str(point.get("query", "")).strip()
                if query:
                    unique_queries.add(query)
        trend_query_count = len(unique_queries)

    required_counts = {
        "serp_urls": (
            safe_len(serp_results) if safe_len(serp_results) > 0 else safe_len(serp_urls),
            int(minimum.get("serp_results", minimum.get("serp_top10_urls", DEFAULT_MINIMUM_DATASET["serp_results"]))),
        ),
        "keyword_phrases": (
            safe_len(keyword_metrics) if safe_len(keyword_metrics) > 0 else safe_len(keyword_phrases),
            int(minimum.get("keyword_metrics", minimum.get("keyword_phrases", DEFAULT_MINIMUM_DATASET["keyword_metrics"]))),
        ),
        "paa_questions": (
            safe_len(paa_questions),
            int(minimum.get("paa_questions", DEFAULT_MINIMUM_DATASET["paa_questions"])),
        ),
        "trend_queries": (
            trend_query_count if trend_query_count > 0 else safe_len(trend_queries),
            int(minimum.get("trend_queries", DEFAULT_MINIMUM_DATASET["trend_queries"])),
        ),
        "competitor_matrix": (
            safe_len(competitor_matrix),
            int(minimum.get("competitor_matrix", DEFAULT_MINIMUM_DATASET["competitor_matrix"])),
        ),
    }

    for field, pair in required_counts.items():
        count, minimum_count = pair
        if count < minimum_count:
            ok = False
            messages.append(f"{field}: {count}/{minimum_count} (insufficient)")
        else:
            messages.append(f"{field}: {count}/{minimum_count} (ok)")

    required_source_fields = ["source_tool", "query_seed", "url", "date_range", "pulled_at"]
    sources = payload.get("sources", [])
    if not isinstance(sources, list) or not sources:
        ok = False
        messages.append("sources: missing entries")
    else:
        for idx, source in enumerate(sources):
            if not isinstance(source, dict):
                ok = False
                messages.append(f"sources[{idx}] is not an object.")
                continue
            missing = [name for name in required_source_fields if not str(source.get(name, "")).strip()]
            if missing:
                ok = False
                messages.append(f"sources[{idx}] missing fields: {', '.join(missing)}")

    return ok, messages


def write_report(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# workflow_context_report.md",
        "",
        "## Gates",
        f"- skills_policy_pass: {'PASS' if payload['skills_policy_pass'] else 'FAIL'}",
        f"- evidence_provenance_pass: {'PASS' if payload['evidence_provenance_pass'] else 'FAIL'}",
        "",
        "## Skill checks",
    ]
    lines.extend([f"- {x}" for x in payload["skills_messages"]])  # type: ignore[index]
    lines.extend(["", "## Evidence checks"])
    lines.extend([f"- {x}" for x in payload["evidence_messages"]])  # type: ignore[index]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    if not workspace.exists():
        print(f"ERROR: Workspace not found: {workspace}")
        return 1

    skills_ok, skills_messages = evaluate_skills(workspace)
    evidence_ok, evidence_messages = evaluate_evidence(workspace)

    set_many_gates(
        workspace=workspace,
        gates={
            "skills_policy_pass": skills_ok,
            "evidence_provenance_pass": evidence_ok,
        },
        source="check_workflow_context.py",
        severity="hard",
        details={
            "skills_policy_pass": " | ".join(skills_messages),
            "evidence_provenance_pass": " | ".join(evidence_messages),
        },
    )

    payload = {
        "ok": skills_ok and evidence_ok,
        "skills_policy_pass": skills_ok,
        "evidence_provenance_pass": evidence_ok,
        "skills_messages": skills_messages,
        "evidence_messages": evidence_messages,
    }
    report_path = workspace / args.report
    write_report(report_path, payload)
    payload["report_path"] = str(report_path.resolve())

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Context report: {report_path}")
        print(f"- skills_policy_pass: {'PASS' if skills_ok else 'FAIL'}")
        print(f"- evidence_provenance_pass: {'PASS' if evidence_ok else 'FAIL'}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
