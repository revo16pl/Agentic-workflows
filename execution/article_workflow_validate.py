#!/usr/bin/env python3
"""
Validate Agentic Articles workflow artifacts.

Usage:
    python3 execution/article_workflow_validate.py \
      --workspace "Agentic Articles/workspace/2026-02-28_ems-niepolomice"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from article_workflow_state import QUALITY_GATE_FILENAME, RESEARCH_EVIDENCE_FILENAME, ensure_quality_gate

REQUIRED_ARTIFACTS = [
    "article_brief.md",
    "article_research_pack.md",
    RESEARCH_EVIDENCE_FILENAME,
    QUALITY_GATE_FILENAME,
    "article_draft_v1.md",
    "qa_report.md",
    "article_draft_v2.md",
    "publish_ready.md",
    "run_context.md",
]

LEGACY_RESEARCH_ARTIFACTS = [
    "intent_map.md",
    "serp_snapshot.md",
    "fact_bank.md",
    "keyword_cluster.md",
    "article_blueprint.md",
]

POLISH_DIACRITICS_REGEX = re.compile(r"[ąćęłńóśżźĄĆĘŁŃÓŚŻŹ]")
POLISH_LETTERS_REGEX = re.compile(r"[A-Za-ząćęłńóśżźĄĆĘŁŃÓŚŻŹ]")
DEFAULT_LANGUAGE_PROTECTED_TERMS = [
    "Kobido",
    "Studio Balans",
    "Niepołomice",
    "Niepolomice",
    "EMS",
]

REQUIRED_SKILLS = [
    "content-strategy",
    "copywriting",
    "copy-editing",
    "seo-audit",
    "schema-markup",
    "ai-seo",
]

REQUIRED_HARD_GATES = [
    "polish_title_naturalness_pass",
    "polish_collocation_pass",
    "polish_grammar_pass",
    "polish_diacritics_pass",
    "polish_punctuation_pass",
    "polish_fluency_ml_pass",
    "structure_variance_pass_v2",
    "semantic_rewrite_pass_v2",
    "forbidden_phrase_pass",
    "specificity_pass",
    "voice_authenticity_pass",
    "rewrite_loop_pass",
    "evidence_provenance_pass",
    "skills_policy_pass",
    "keyword_metrics_coverage_pass",
    "serp_dataset_quality_pass",
    "trends_dataset_quality_pass",
    "competitor_matrix_pass",
    "research_data_freshness_pass",
    "research_hard_block_pass",
    "hard_block_export_pass",
]


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: dict[str, str] = field(default_factory=dict)

    def add_error(self, name: str, message: str) -> None:
        self.checks[name] = "FAIL"
        self.errors.append(message)

    def add_pass(self, name: str) -> None:
        self.checks[name] = "PASS"

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_brief_metadata(text: str) -> dict[str, str]:
    yaml_block = re.search(r"```yaml\s*(.*?)```", text, flags=re.S)
    if not yaml_block:
        return {}

    metadata: dict[str, str] = {}
    for raw_line in yaml_block.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        clean_value = value.strip()
        if " #" in clean_value:
            clean_value = clean_value.split(" #", 1)[0].strip()
        metadata[key.strip()] = clean_value.strip('"').strip("'")
    return metadata


def parse_int(value: str | None, fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def parse_score(text: str) -> int | None:
    patterns = [
        r"total_score\s*:\s*(\d{1,3})",
        r"Total score\s*:?\s*(\d{1,3})",
        r"total\s*>=?\s*(\d{1,3})/100",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def count_words(text: str) -> int:
    body = re.sub(r"```.*?```", " ", text, flags=re.S)
    body = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", body)
    words = re.findall(r"\b[\w\-]+\b", body, flags=re.UNICODE)
    return len(words)


def clean_markdown_for_language_checks(text: str) -> str:
    cleaned = re.sub(r"```.*?```", " ", text, flags=re.S)
    cleaned = re.sub(r"(?is)\n##\s*zr[oó]d[łl]a.*$", " ", cleaned)
    cleaned = re.sub(r"(?is)\n#\s*zr[oó]d[łl]a.*$", " ", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.M)
    cleaned = re.sub(r"^\s*[-*]\s+", "", cleaned, flags=re.M)
    cleaned = re.sub(r"^\s*\d+\.\s+", "", cleaned, flags=re.M)
    cleaned = re.sub(r"^\s*>\s?", "", cleaned, flags=re.M)
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_prose_for_grammar_checks(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    prose_lines: list[str] = []
    in_code_block = False
    in_sources_section = False

    for raw_line in lines:
        if re.match(r"^\s*```", raw_line):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        line = raw_line.strip()
        if not line:
            continue

        if re.match(r"^#{1,6}\s*(Źródła|Zrodla|Sources)\s*$", line, flags=re.IGNORECASE):
            in_sources_section = True
            continue
        if in_sources_section:
            continue

        if line.startswith("|"):
            continue

        if re.match(r"^#{1,6}\s+", line):
            # Headings are often sentence fragments and create false positives in grammar tools.
            continue

        line = re.sub(r"^\s*>\s?", "", line)

        list_match = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", line)
        if list_match:
            candidate = list_match.group(1).strip()
            if len(re.findall(r"\b[\w\-]+\b", candidate, flags=re.UNICODE)) < 7:
                continue
            line = candidate

        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"\*([^*]+)\*", r"\1", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"https?://\S+", " ", line).strip()
        if not line:
            continue

        if not re.search(r"[.!?…:]$", line):
            line = re.sub(r"[,;:]+$", "", line).strip()
            line = f"{line}."

        prose_lines.append(line)

    prose_text = "\n".join(prose_lines).strip()
    prose_text = re.sub(r"\n{3,}", "\n\n", prose_text)
    prose_text = re.sub(r"\s+", " ", prose_text).strip()
    return prose_text


def polish_diacritics_stats(text: str) -> tuple[int, int, float]:
    letters = POLISH_LETTERS_REGEX.findall(text)
    diacritics = POLISH_DIACRITICS_REGEX.findall(text)
    total_letters = len(letters)
    diacritics_count = len(diacritics)
    ratio = (diacritics_count / total_letters) if total_letters else 0.0
    return diacritics_count, total_letters, ratio


def language_tool_matches(text: str, language: str) -> dict[str, object]:
    provider = os.getenv("LANGUAGETOOL_PROVIDER", "auto").strip().lower()
    timeout = float(os.getenv("LANGUAGETOOL_TIMEOUT_SECONDS", "20"))
    chunk_size = int(os.getenv("LANGUAGETOOL_CHUNK_SIZE", "12000"))
    disabled_rules = os.getenv("LANGUAGETOOL_DISABLED_RULES", "").strip()

    chunks: list[str] = []
    if len(text) <= chunk_size:
        chunks.append(text)
    else:
        cursor = 0
        while cursor < len(text):
            upper = min(cursor + chunk_size, len(text))
            chunks.append(text[cursor:upper])
            cursor = upper

    if provider in {"auto", "local"}:
        try:
            import language_tool_python

            tool = language_tool_python.LanguageTool(language)
            try:
                local_matches: list[dict[str, object]] = []
                for chunk in chunks:
                    checked = tool.check(chunk)
                    for match in checked:
                        replacements: list[dict[str, str]] = []
                        raw_replacements = getattr(match, "replacements", [])
                        if isinstance(raw_replacements, list):
                            for replacement in raw_replacements:
                                value = str(replacement).strip()
                                if value:
                                    replacements.append({"value": value})
                        local_matches.append(
                            {
                                "message": getattr(match, "message", ""),
                                "context": {"text": getattr(match, "context", "")},
                                "ruleIssueType": getattr(match, "ruleIssueType", ""),
                                "category": getattr(match, "category", ""),
                                "ruleId": getattr(match, "ruleId", ""),
                                "offset": int(getattr(match, "offset", 0)),
                                "length": int(getattr(match, "errorLength", 0)),
                                "replacements": replacements,
                            }
                        )
                return {"matches": local_matches}
            finally:
                tool.close()
        except Exception:
            if provider == "local":
                raise

    import requests

    api_url = os.getenv("LANGUAGETOOL_API_URL", "https://api.languagetool.org/v2/check")
    all_matches: list[dict[str, object]] = []
    for chunk in chunks:
        payload = {"language": language, "text": chunk}
        if disabled_rules:
            payload["disabledRules"] = disabled_rules
        response = requests.post(api_url, data=payload, timeout=timeout)
        response.raise_for_status()
        parsed = response.json()
        matches = parsed.get("matches", [])
        if isinstance(matches, list):
            all_matches.extend(matches)

    return {"matches": all_matches}


def resolve_language_protected_terms() -> list[str]:
    env_terms = os.getenv("LANGUAGE_PROTECTED_TERMS", "")
    merged = DEFAULT_LANGUAGE_PROTECTED_TERMS + [x.strip() for x in env_terms.split(",")]
    unique: list[str] = []
    seen: set[str] = set()
    for term in merged:
        if not term:
            continue
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(term)
    return unique


def count_polish_grammar_issues(
    matches: list[dict[str, object]],
    source_text: str = "",
) -> tuple[int, list[str]]:
    issue_types = {"misspelling", "grammar", "typographical"}
    categories = {"GRAMMAR", "TYPOS", "PUNCTUATION", "SPELLING"}
    protected_terms = resolve_language_protected_terms()
    issues = 0
    sample_messages: list[str] = []

    for match in matches:
        if not isinstance(match, dict):
            continue
        rule = match.get("rule", {}) if isinstance(match.get("rule"), dict) else {}
        issue_type = str(rule.get("issueType", "")).lower() or str(match.get("ruleIssueType", "")).lower()
        category_id = str((rule.get("category", {}) or {}).get("id", "")).upper()
        if not category_id:
            category_id = str(match.get("category", "")).upper()

        replacements = match.get("replacements", [])
        has_replacements = False
        if isinstance(replacements, list):
            for item in replacements:
                if isinstance(item, dict) and str(item.get("value", "")).strip():
                    has_replacements = True
                    break

        context = str((match.get("context", {}) or {}).get("text", "")).strip()
        if not context:
            context = str(match.get("context", "")).strip()

        matched_text = ""
        try:
            offset = int(match.get("offset", -1))
            length = int(match.get("length", 0))
            if source_text and offset >= 0 and length > 0 and offset + length <= len(source_text):
                matched_text = source_text[offset : offset + length]
        except (TypeError, ValueError):
            matched_text = ""

        if issue_type == "misspelling" or category_id in {"TYPOS", "SPELLING"}:
            if matched_text and any(matched_text.lower() == term.lower() for term in protected_terms):
                continue
            if context:
                ctx_lower = context.lower()
                if any(term.lower() in ctx_lower for term in protected_terms):
                    continue

        if issue_type in issue_types or category_id in categories:
            issues += 1
            if len(sample_messages) < 3:
                message = str(match.get("message", "")).strip()
                if context:
                    sample_messages.append(f"{message} | context: {context}")
                elif message:
                    sample_messages.append(message)

    return issues, sample_messages


def parse_final_decision(text: str) -> str | None:
    match = re.search(
        r"final_decision\s*:\s*`?(approved|revise)`?",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).lower()
    return None


def parse_critical_failures(text: str) -> list[str]:
    json_block = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if json_block:
        try:
            parsed = json.loads(json_block.group(1))
            failures = parsed.get("critical_failures")
            if isinstance(failures, list):
                return [str(item).strip() for item in failures if str(item).strip()]
        except json.JSONDecodeError:
            pass

    checked = re.findall(r"- \[(x|X)\] (.+)", text)
    fail_labels = []
    for _, label in checked:
        if (
            "niezweryfikowane" in label.lower()
            or "niezgodnosc" in label.lower()
            or "stuffing" in label.lower()
            or "ryzyko" in label.lower()
            or "blokada" in label.lower()
        ):
            fail_labels.append(label.strip())
    return fail_labels


def is_approved_publish_ready(text: str) -> bool:
    if re.search(r"status\s*:\s*approved", text, flags=re.IGNORECASE):
        return True
    if re.search(r"\bapproved\b", text, flags=re.IGNORECASE):
        return True
    if re.search(r"status\s*:\s*ready[_ ]for[_ ]manual[_ ]review", text, flags=re.IGNORECASE):
        return True
    if re.search(r"ready[_ ]for[_ ]manual[_ ]review", text, flags=re.IGNORECASE):
        return True
    return False


def parse_gate_value(text: str, key: str) -> str | None:
    pattern = rf"{re.escape(key)}\s*:\s*(PASS|FAIL)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def parse_run_context(path: Path) -> dict[str, str]:
    payload: dict[str, str] = {}
    if not path.exists():
        return payload
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        payload[key.strip()] = value.strip()
    return payload


def parse_comma_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_skills_policy(workspace: Path, result: ValidationResult) -> None:
    context = parse_run_context(workspace / "run_context.md")
    data_mode = context.get("data_mode", "").strip()
    if data_mode != "external_only":
        result.add_error(
            "data_mode_external_only",
            "run_context.md must contain '- data_mode: external_only'.",
        )
    else:
        result.add_pass("data_mode_external_only")

    providers_loaded = context.get("research_providers_loaded", "").strip()
    if not providers_loaded:
        result.add_error(
            "research_providers_loaded",
            "run_context.md must contain '- research_providers_loaded: ...' after research_fetch.",
        )
    else:
        required_providers = ["google_ads_keyword_planner_api", "serper", "pytrends"]
        missing_providers = [provider for provider in required_providers if provider not in providers_loaded]
        if missing_providers:
            result.add_error(
                "research_providers_loaded",
                "run_context.md research_providers_loaded missing: " + ", ".join(missing_providers),
            )
        else:
            result.add_pass("research_providers_loaded")

    research_status = context.get("research_fetch_status", "").strip().lower()
    if research_status != "ok":
        result.add_error(
            "research_fetch_status",
            "run_context.md research_fetch_status must be 'ok' before pre_export validation.",
        )
    else:
        result.add_pass("research_fetch_status")

    required = parse_comma_list(context.get("skills_required")) or REQUIRED_SKILLS
    loaded = set(parse_comma_list(context.get("skills_loaded")))
    applied = set(parse_comma_list(context.get("skills_applied")))

    missing_required = [skill for skill in REQUIRED_SKILLS if skill not in required]
    if missing_required:
        result.add_error(
            "skills_required_declared",
            "run_context.md skills_required missing mandatory skills: " + ", ".join(missing_required),
        )
    else:
        result.add_pass("skills_required_declared")

    missing_loaded = [skill for skill in REQUIRED_SKILLS if skill not in loaded]
    if missing_loaded:
        result.add_error(
            "skills_loaded",
            "run_context.md skills_loaded missing: " + ", ".join(missing_loaded),
        )
    else:
        result.add_pass("skills_loaded")

    missing_applied = [skill for skill in REQUIRED_SKILLS if skill not in applied]
    if missing_applied:
        result.add_error(
            "skills_applied",
            "run_context.md skills_applied missing: " + ", ".join(missing_applied),
        )
    else:
        result.add_pass("skills_applied")

    project_root = workspace.parents[2] if len(workspace.parents) >= 3 else workspace.parent
    missing_local: list[str] = []
    for skill in REQUIRED_SKILLS:
        if not (project_root / "skills" / skill / "SKILL.md").exists():
            missing_local.append(skill)
    if missing_local:
        result.add_error(
            "skills_local_install",
            "Missing local skill install(s) in ./skills: " + ", ".join(missing_local),
        )
    else:
        result.add_pass("skills_local_install")


def validate_evidence_manifest(workspace: Path, result: ValidationResult) -> None:
    manifest_path = workspace / RESEARCH_EVIDENCE_FILENAME
    if not manifest_path.exists():
        result.add_error("evidence_manifest_exists", f"Missing {RESEARCH_EVIDENCE_FILENAME}.")
        return

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.add_error("evidence_manifest_json", f"Invalid JSON in {manifest_path}: {exc}")
        return

    if not isinstance(payload, dict):
        result.add_error("evidence_manifest_json", f"{manifest_path} must contain a JSON object.")
        return
    result.add_pass("evidence_manifest_json")

    data_mode = str(payload.get("data_mode", "")).strip()
    if data_mode != "external_only":
        result.add_error("evidence_manifest_data_mode", "research_evidence_manifest.json data_mode must be external_only.")
    else:
        result.add_pass("evidence_manifest_data_mode")

    serp_urls = payload.get("serp_urls", [])
    keyword_phrases = payload.get("keyword_phrases", [])
    paa_questions = payload.get("paa_questions", [])
    trend_queries = payload.get("trend_queries", [])
    serp_results = payload.get("serp_results", [])
    keyword_metrics = payload.get("keyword_metrics", [])
    trend_points = payload.get("trend_points", [])
    competitor_matrix = payload.get("competitor_matrix", [])
    sources = payload.get("sources", [])

    def as_list(value: object) -> list[object]:
        return value if isinstance(value, list) else []

    serp_urls = as_list(serp_urls)
    keyword_phrases = as_list(keyword_phrases)
    paa_questions = as_list(paa_questions)
    trend_queries = as_list(trend_queries)
    serp_results = as_list(serp_results)
    keyword_metrics = as_list(keyword_metrics)
    trend_points = as_list(trend_points)
    competitor_matrix = as_list(competitor_matrix)
    sources = as_list(sources)

    minimum = payload.get("minimum_dataset", {})
    minimum = minimum if isinstance(minimum, dict) else {}

    min_serp = int(minimum.get("serp_results", minimum.get("serp_top10_urls", 10)))
    min_keywords = int(minimum.get("keyword_metrics", minimum.get("keyword_phrases", 30)))
    min_paa = int(minimum.get("paa_questions", 10))
    min_trends = int(minimum.get("trend_queries", 5))
    min_competitor = int(minimum.get("competitor_matrix", 10))

    trend_query_count = 0
    if trend_points:
        unique_queries = set()
        for point in trend_points:
            if isinstance(point, dict):
                query = str(point.get("query", "")).strip()
                if query:
                    unique_queries.add(query)
        trend_query_count = len(unique_queries)

    checks = [
        (
            "evidence_serp_count",
            len(serp_results) if serp_results else len(serp_urls),
            min_serp,
            "serp_results/serp_urls",
        ),
        (
            "evidence_keyword_count",
            len(keyword_metrics) if keyword_metrics else len(keyword_phrases),
            min_keywords,
            "keyword_metrics/keyword_phrases",
        ),
        ("evidence_paa_count", len(paa_questions), min_paa, "paa_questions"),
        (
            "evidence_trend_count",
            trend_query_count if trend_query_count else len(trend_queries),
            min_trends,
            "trend_points/trend_queries",
        ),
        ("evidence_competitor_count", len(competitor_matrix), min_competitor, "competitor_matrix"),
    ]
    for name, actual, minimum_count, field_name in checks:
        if actual < minimum_count:
            result.add_error(name, f"{field_name} has {actual}, expected at least {minimum_count}.")
        else:
            result.add_pass(name)

    required_source_fields = ["source_tool", "query_seed", "url", "date_range", "pulled_at"]
    malformed_sources: list[str] = []
    for idx, source in enumerate(sources):
        if not isinstance(source, dict):
            malformed_sources.append(f"sources[{idx}] is not an object")
            continue
        missing = [key for key in required_source_fields if not str(source.get(key, "")).strip()]
        if missing:
            malformed_sources.append(f"sources[{idx}] missing: {', '.join(missing)}")

    if malformed_sources:
        result.add_error("evidence_sources_schema", "; ".join(malformed_sources))
    else:
        result.add_pass("evidence_sources_schema")

    version = str(payload.get("version", "")).strip()
    if version == "3.0":
        providers = payload.get("providers", {})
        if not isinstance(providers, dict):
            result.add_error("evidence_providers_schema", "Manifest v3.0 requires providers object.")
        else:
            expected = ["keyword_metrics", "serp", "serp_fallback", "trends"]
            missing_provider_keys = [key for key in expected if not str(providers.get(key, "")).strip()]
            if missing_provider_keys:
                result.add_error(
                    "evidence_providers_schema",
                    "Manifest providers missing keys: " + ", ".join(missing_provider_keys),
                )
            else:
                result.add_pass("evidence_providers_schema")

        query_seeds = payload.get("query_seeds", [])
        if not isinstance(query_seeds, list) or len(query_seeds) < 3:
            result.add_error("evidence_query_seeds", "Manifest v3.0 requires at least 3 query_seeds.")
        else:
            result.add_pass("evidence_query_seeds")


def validate_quality_gate(workspace: Path, result: ValidationResult) -> None:
    payload = ensure_quality_gate(workspace)
    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        result.add_error("quality_gate_schema", "quality_gate.json gates must be an object.")
        return
    result.add_pass("quality_gate_schema")

    hard = payload.get("hard_gates", [])
    if not isinstance(hard, list):
        hard = []
    missing_hard = [name for name in REQUIRED_HARD_GATES if name not in hard]
    if missing_hard:
        result.add_error("quality_gate_hard_set", "quality_gate.json hard_gates missing: " + ", ".join(missing_hard))
    else:
        result.add_pass("quality_gate_hard_set")

    for gate_name in REQUIRED_HARD_GATES:
        gate_payload = gates.get(gate_name, {})
        status = str((gate_payload or {}).get("status", "")).upper()
        if status != "PASS":
            result.add_error(
                f"quality_gate_{gate_name}",
                f"quality_gate.json hard gate '{gate_name}' must be PASS.",
            )
        else:
            result.add_pass(f"quality_gate_{gate_name}")

    advisory = gates.get("detector_ensemble_pass", {})
    advisory_status = str((advisory or {}).get("status", "")).upper()
    if advisory_status and advisory_status != "PASS":
        result.add_warning("Advisory gate detector_ensemble_pass is FAIL (non-blocking).")


def validate_research_artifacts(workspace: Path, result: ValidationResult) -> None:
    research_pack = workspace / "article_research_pack.md"
    if research_pack.exists():
        if research_pack.stat().st_size == 0:
            result.add_error("research_pack_non_empty", f"Artifact is empty: {research_pack}")
        else:
            result.add_pass("research_pack_non_empty")
    else:
        missing_legacy = []
        for artifact in LEGACY_RESEARCH_ARTIFACTS:
            artifact_path = workspace / artifact
            if not artifact_path.exists():
                missing_legacy.append(artifact)
                continue
            if artifact_path.stat().st_size == 0:
                result.add_error(
                    f"non_empty_{artifact}",
                    f"Artifact is empty: {artifact_path}",
                )
            else:
                result.add_pass(f"non_empty_{artifact}")
        if missing_legacy:
            result.add_error(
                "research_artifacts_present",
                (
                    "Missing research artifact(s). Provide either article_research_pack.md "
                    f"or legacy set: {', '.join(missing_legacy)}"
                ),
            )
        else:
            result.add_pass("research_artifacts_present")

    validate_evidence_manifest(workspace, result)


def validate_workspace(workspace: Path, mode: str) -> ValidationResult:
    result = ValidationResult()

    if not workspace.exists() or not workspace.is_dir():
        result.add_error("workspace_exists", f"Workspace not found: {workspace}")
        return result
    result.add_pass("workspace_exists")

    missing = []
    for artifact in REQUIRED_ARTIFACTS:
        artifact_path = workspace / artifact
        if not artifact_path.exists():
            missing.append(artifact)
            continue
        if artifact_path.stat().st_size == 0:
            result.add_error(
                f"non_empty_{artifact}",
                f"Artifact is empty: {artifact_path}",
            )
        else:
            result.add_pass(f"non_empty_{artifact}")

    if missing:
        result.add_error(
            "artifacts_present",
            f"Missing artifacts: {', '.join(missing)}",
        )
    else:
        result.add_pass("artifacts_present")

    validate_research_artifacts(workspace, result)

    if mode == "artifacts":
        return result

    brief_path = workspace / "article_brief.md"
    brief_meta: dict[str, str] = {}
    locale = "pl-PL"
    if brief_path.exists():
        brief = read_text(brief_path)
        brief_meta = parse_brief_metadata(brief)
        locale = brief_meta.get("locale", "pl-PL")
        if brief_meta.get("topic") and brief_meta.get("company"):
            result.add_pass("brief_topic_company")
        else:
            result.add_error(
                "brief_topic_company",
                "article_brief.md missing topic/company in metadata.",
            )

        min_words = parse_int(brief_meta.get("word_count_min"), 1200)
        max_words = parse_int(brief_meta.get("word_count_max"), 2500)
        draft_v2_path = workspace / "article_draft_v2.md"
        if draft_v2_path.exists():
            wc = count_words(read_text(draft_v2_path))
            if wc < min_words or wc > max_words:
                result.add_error(
                    "draft_word_count",
                    f"article_draft_v2.md word count {wc} outside configured range {min_words}-{max_words}.",
                )
            else:
                result.add_pass("draft_word_count")
        else:
            result.add_error("draft_word_count", "article_draft_v2.md not found for length check.")

    draft_v2_path = workspace / "article_draft_v2.md"
    if draft_v2_path.exists() and locale.lower().startswith("pl"):
        draft_v2_text = read_text(draft_v2_path)
        cleaned_text = clean_markdown_for_language_checks(draft_v2_text)
        grammar_text = extract_prose_for_grammar_checks(draft_v2_text)
        if count_words(grammar_text) < 300:
            grammar_text = cleaned_text

        min_diacritics = int(os.getenv("POLISH_DIACRITICS_MIN_COUNT", "25"))
        min_ratio = float(os.getenv("POLISH_DIACRITICS_MIN_RATIO", "0.003"))
        diacritics_count, letters_count, ratio = polish_diacritics_stats(cleaned_text)
        if diacritics_count < min_diacritics or ratio < min_ratio:
            result.add_error(
                "polish_diacritics",
                (
                    "Missing Polish diacritics in article_draft_v2.md. "
                    f"Found {diacritics_count} diacritics over {letters_count} letters "
                    f"(ratio={ratio:.4f}), expected at least {min_diacritics} and ratio >= {min_ratio:.4f}."
                ),
            )
        else:
            result.add_pass("polish_diacritics")

        try:
            grammar_payload = language_tool_matches(grammar_text, language="pl-PL")
            matches = grammar_payload.get("matches", [])
            if not isinstance(matches, list):
                matches = []
            issues, samples = count_polish_grammar_issues(matches, source_text=grammar_text)
            words = count_words(grammar_text)
            max_per_1000 = float(os.getenv("POLISH_GRAMMAR_MAX_ERRORS_PER_1000", "5.0"))
            allowed_issues = max(5, round((words / 1000) * max_per_1000))
            if issues > allowed_issues:
                sample_text = " | ".join(samples) if samples else "No sample messages."
                result.add_error(
                    "polish_grammar_quality",
                    (
                        "Polish grammar quality below gate. "
                        f"Detected issues={issues}, allowed={allowed_issues} for {words} words. "
                        f"Samples: {sample_text}"
                    ),
                )
            else:
                result.add_pass("polish_grammar_quality")
        except Exception as exc:
            result.add_error(
                "polish_grammar_quality",
                f"Grammar validation unavailable (LanguageTool API): {exc}",
            )

    qa_path = workspace / "qa_report.md"
    if qa_path.exists():
        qa_text = read_text(qa_path)
        score = parse_score(qa_text)
        if score is None:
            result.add_warning("Cannot parse total score from qa_report.md (non-blocking).")
        elif score < 85:
            result.add_warning(f"QA score below 85/100 in qa_report.md ({score}).")

        decision = parse_final_decision(qa_text)
        if decision != "approved":
            result.add_warning("qa_report.md final_decision is not approved (non-blocking).")
        else:
            result.add_pass("qa_decision_advisory")

        critical_failures = parse_critical_failures(qa_text)
        if critical_failures:
            result.add_warning("qa_report.md has marked critical failures (non-blocking): " + "; ".join(critical_failures))

    validate_skills_policy(workspace, result)
    validate_quality_gate(workspace, result)

    publish_path = workspace / "publish_ready.md"
    if publish_path.exists():
        publish_text = read_text(publish_path)
        if is_approved_publish_ready(publish_text):
            result.add_pass("publish_ready_status")
        else:
            result.add_error(
                "publish_ready_status",
                "publish_ready.md must be Ready_for_manual_review or Approved.",
            )

    if mode == "post_export":
        result.add_pass("post_export_mode")

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate article workflow workspace.")
    parser.add_argument(
        "--workspace",
        required=True,
        type=Path,
        help="Workspace directory path.",
    )
    parser.add_argument(
        "--mode",
        choices=["artifacts", "pre_export", "post_export", "final"],
        default="pre_export",
        help=(
            "artifacts=only file completeness, "
            "pre_export=QA gate before Docs export, "
            "post_export=alias mode for compatibility, "
            "final=alias for pre_export."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "pre_export" if args.mode == "final" else args.mode
    result = validate_workspace(args.workspace.resolve(), mode)

    if args.json:
        payload = {
            "ok": result.ok,
            "checks": result.checks,
            "errors": result.errors,
            "warnings": result.warnings,
            "workspace": str(args.workspace.resolve()),
            "mode": mode,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Workspace: {args.workspace.resolve()}")
        print(f"Mode: {mode}")
        for check, status in sorted(result.checks.items()):
            print(f"[{status}] {check}")
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"- {warning}")
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"- {error}")
        print("\nValidation result:", "PASS" if result.ok else "FAIL")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
