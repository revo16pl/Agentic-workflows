#!/usr/bin/env python3
"""
Validate Agentic Articles workflow artifacts.

Usage:
    python3 execution/article_workflow_validate.py \
      --workspace "Agentic Articles/workspace/2026-02-28_ems-niepolomice"
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from article_workflow_state import QUALITY_GATE_FILENAME, RESEARCH_EVIDENCE_FILENAME, ensure_quality_gate

REQUIRED_ARTIFACTS = [
    "article_brief.md",
    "article_research_pack.md",
    RESEARCH_EVIDENCE_FILENAME,
    QUALITY_GATE_FILENAME,
    "article_draft_v2.md",
    "editorial_review.md",
    "run_context.md",
]

SERVICE_REQUIRED_ARTIFACTS = [
    "service_page_context.json",
    "company_profile_snapshot.json",
    "service_page_writer_packet.md",
    "editorial_review.md",
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
    "topic_from_approved_plan_pass",
    "hard_block_export_pass",
]

SERVICE_REQUIRED_HARD_GATES = [
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

SERVICE_FALLBACK_TABS = [
    "Wskazania",
    "Przeciwwskazania i bezpieczeństwo",
    "Zalecenia przed i po",
    "FAQ",
]

SECOND_PERSON_MARKERS = [
    "ty",
    "tobie",
    "ciebie",
    "cię",
    "ci",
    "twój",
    "twoj",
    "twoja",
    "twoje",
    "twoim",
    "twoją",
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


def parse_logic_pass(text: str) -> str | None:
    match = re.search(
        r"logic_pass\s*:\s*`?(PASS|FAIL)`?",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).upper()
    return None


def parse_iterations_completed(text: str) -> int | None:
    match = re.search(r"iterations_completed\s*:\s*(\d+)", text, flags=re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def parse_post_machine_qa_revision(text: str) -> str | None:
    match = re.search(
        r"post_machine_qa_revision_completed\s*:\s*`?(yes|no)`?",
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


def resolve_content_profile(workspace: Path, content_profile: str) -> str:
    profile = (content_profile or "").strip().lower()
    if profile in {"article", "service_page"}:
        return profile
    context = parse_run_context(workspace / "run_context.md")
    context_profile = context.get("content_profile", "").strip().lower()
    if context_profile in {"article", "service_page"}:
        return context_profile
    return "article"


def expected_service_tabs(workspace: Path) -> list[str]:
    context = parse_run_context(workspace / "run_context.md")
    labels = parse_comma_list(context.get("section_labels"))
    if labels:
        return labels

    context_json = workspace / "service_page_context.json"
    if context_json.exists():
        try:
            payload = json.loads(context_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            tabs = payload.get("tab_labels", [])
            if isinstance(tabs, list):
                labels = [str(item).strip() for item in tabs if str(item).strip()]
                if labels:
                    return labels
    return list(SERVICE_FALLBACK_TABS)


def _extract_section_block(text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.M)
    if not match:
        return ""
    start = match.end()
    tail = text[start:]
    next_heading = re.search(r"^\s*##\s+.+$", tail, flags=re.M)
    if next_heading:
        return tail[: next_heading.start()].strip()
    return tail.strip()


def _extract_h3_subsection(parent_block: str, heading: str) -> str:
    pattern = rf"^###\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, parent_block, flags=re.IGNORECASE | re.M)
    if not match:
        return ""
    start = match.end()
    tail = parent_block[start:]
    next_heading = re.search(r"^\s*###\s+.+$", tail, flags=re.M)
    if next_heading:
        return tail[: next_heading.start()].strip()
    return tail.strip()


def _normalize_text(value: str) -> str:
    lowered = value.strip().lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", normalized)


def _count_second_person_hits(text: str) -> int:
    normalized = _normalize_text(text)
    hits = 0
    for marker in SECOND_PERSON_MARKERS:
        hits += len(re.findall(rf"(?<!\w){re.escape(_normalize_text(marker))}(?!\w)", normalized))
    return hits


def validate_service_page_sections(workspace: Path, result: ValidationResult) -> None:
    draft_path = workspace / "article_draft_v2.md"
    if not draft_path.exists():
        result.add_error("service_sections_presence", "article_draft_v2.md missing for service_page validation.")
        return
    text = read_text(draft_path)

    subheading_block = _extract_section_block(text, "Subheading")
    description_block = _extract_section_block(text, "Opis")
    info_block = _extract_section_block(text, "Najważniejsze informacje")

    if not subheading_block:
        result.add_error("service_subheading_presence", "Missing section '## Subheading' with content.")
    else:
        result.add_pass("service_subheading_presence")

    if not description_block:
        result.add_error("service_description_presence", "Missing section '## Opis' with content.")
    else:
        result.add_pass("service_description_presence")

    if not info_block:
        result.add_error("service_info_presence", "Missing section '## Najważniejsze informacje' with content.")
    else:
        result.add_pass("service_info_presence")

    if subheading_block:
        raw_lines = [line.strip() for line in subheading_block.splitlines() if line.strip() and not line.strip().startswith("### ")]
        subheading_text = " ".join(raw_lines).strip()
        subheading_chars = len(subheading_text)
        if subheading_chars < 40:
            result.add_error("service_subheading_length", f"Subheading too short ({subheading_chars} chars).")
        else:
            context_path = workspace / "service_page_context.json"
            target_chars = 0
            if context_path.exists():
                try:
                    payload = json.loads(context_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    payload = {}
                if isinstance(payload, dict):
                    subheading = payload.get("subheading", {})
                    if isinstance(subheading, dict):
                        raw_target = subheading.get("chars", 0)
                        try:
                            target_chars = int(raw_target)
                        except (TypeError, ValueError):
                            target_chars = 0

            if target_chars > 0:
                min_chars = max(40, int(target_chars * 0.50))
                max_chars = max(min_chars + 20, int(target_chars * 1.60))
                if subheading_chars < min_chars or subheading_chars > max_chars:
                    result.add_error(
                        "service_subheading_length",
                        (
                            f"Subheading length not similar to source. "
                            f"Got {subheading_chars}, expected approx {min_chars}-{max_chars} "
                            f"(source={target_chars})."
                        ),
                    )
                else:
                    result.add_pass("service_subheading_length")
            else:
                result.add_pass("service_subheading_length")

    if description_block:
        description_plain = re.sub(r"^###\s+.*$", "", description_block, flags=re.M).strip()
        description_words = count_words(description_plain)
        if description_words < 35 or description_words > 280:
            result.add_error(
                "service_description_length",
                f"Opis should be concise but informative (35-280 words). Got {description_words}.",
            )
        else:
            result.add_pass("service_description_length")

    if info_block:
        tabs = expected_service_tabs(workspace)
        missing_tabs: list[str] = []
        for tab in tabs:
            if not re.search(rf"^###\s+{re.escape(tab)}\s*$", info_block, flags=re.IGNORECASE | re.M):
                missing_tabs.append(tab)
        if missing_tabs:
            result.add_error(
                "service_tab_coverage",
                "Missing tab section(s) under 'Najważniejsze informacje': " + ", ".join(missing_tabs),
            )
        else:
            result.add_pass("service_tab_coverage")

        empty_tabs: list[str] = []
        faq_items_count = 0
        for tab in tabs:
            block = _extract_h3_subsection(info_block, tab)
            cleaned_lines = []
            for raw_line in block.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                if re.fullmatch(r"[-*]\s*", line):
                    continue
                if re.fullmatch(r"_?Wpisz.*_?", line, flags=re.IGNORECASE):
                    continue
                cleaned_lines.append(line)

            cleaned_text = " ".join(cleaned_lines).strip()
            if count_words(cleaned_text) < 4:
                empty_tabs.append(tab)

            if _normalize_text(tab) == _normalize_text("FAQ"):
                for line in cleaned_lines:
                    if "?" in line:
                        faq_items_count += 1

        if empty_tabs:
            result.add_error(
                "service_tab_content_nonempty_pass",
                "Tab(s) under 'Najważniejsze informacje' have empty/placeholder content: " + ", ".join(empty_tabs),
            )
        else:
            result.add_pass("service_tab_content_nonempty_pass")

        if faq_items_count < 2:
            result.add_error(
                "service_faq_min_items_pass",
                f"FAQ must contain at least 2 question/answer items. Found {faq_items_count}.",
            )
        else:
            result.add_pass("service_faq_min_items_pass")

    placeholder_patterns = [
        r"^\s*[-*]\s*$",
        r"_Wpisz[^_]*_",
    ]
    placeholder_hits = 0
    for pattern in placeholder_patterns:
        placeholder_hits += len(re.findall(pattern, text, flags=re.IGNORECASE | re.M))
    if placeholder_hits > 0:
        result.add_error(
            "service_no_placeholder_pass",
            f"Detected placeholder content markers in draft: {placeholder_hits}.",
        )
    else:
        result.add_pass("service_no_placeholder_pass")

    snapshot_path = workspace / "company_profile_snapshot.json"
    run_context = parse_run_context(workspace / "run_context.md")
    if not snapshot_path.exists():
        result.add_error(
            "service_brand_voice_alignment_pass",
            "Missing company_profile_snapshot.json for brand voice validation.",
        )
        return

    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        result.add_error(
            "service_brand_voice_alignment_pass",
            "Invalid company_profile_snapshot.json (JSON parse error).",
        )
        return

    if not isinstance(snapshot, dict):
        result.add_error(
            "service_brand_voice_alignment_pass",
            "Invalid company_profile_snapshot.json schema.",
        )
        return

    if run_context.get("brand_voice_loaded", "").strip().lower() != "yes":
        result.add_error(
            "service_brand_voice_alignment_pass",
            "run_context.md must contain brand_voice_loaded: yes for service_page.",
        )
        return

    brand_voice = snapshot.get("brand_voice", {}) if isinstance(snapshot.get("brand_voice"), dict) else {}
    avoid_rules = brand_voice.get("avoid_rules", []) if isinstance(brand_voice.get("avoid_rules"), list) else []
    normalized_text = _normalize_text(text)
    avoid_hits: list[str] = []
    for rule in avoid_rules:
        rule_norm = _normalize_text(str(rule))
        if rule_norm and rule_norm in normalized_text:
            avoid_hits.append(str(rule))

    if avoid_hits:
        result.add_error(
            "service_brand_voice_alignment_pass",
            "Brand voice avoid rules found in draft: " + ", ".join(avoid_hits),
        )
        return

    requires_second_person = bool(brand_voice.get("requires_second_person", False))
    second_person_min_hits_raw = brand_voice.get("second_person_min_hits", 0)
    try:
        second_person_min_hits = int(second_person_min_hits_raw or 0)
    except (TypeError, ValueError):
        second_person_min_hits = 0

    if requires_second_person and second_person_min_hits > 0:
        hits = _count_second_person_hits(text)
        if hits < second_person_min_hits:
            result.add_error(
                "service_brand_voice_alignment_pass",
                f"Brand voice requires second-person narration. Found {hits}, required >= {second_person_min_hits}.",
            )
            return

    result.add_pass("service_brand_voice_alignment_pass")


def validate_editorial_review(workspace: Path, result: ValidationResult, content_profile: str) -> None:
    review_path = workspace / "editorial_review.md"
    if not review_path.exists():
        result.add_error(
            "editorial_review_exists",
            f"Missing editorial_review.md for {content_profile} editorial QA.",
        )
        return

    text = read_text(review_path)
    if not text:
        result.add_error(
            "editorial_review_exists",
            "editorial_review.md is empty.",
        )
        return
    result.add_pass("editorial_review_exists")

    required_sections = [
        "## Pass 1: Logic and Sense",
        "## Pass 2: Content-Strategy Sweep",
        "## Pass 3: Copywriting Sweep",
        "## Pass 4: Copy-Editing Sweep",
        "## Final Decision",
    ]
    missing_sections = [section for section in required_sections if section not in text]
    if missing_sections:
        result.add_error(
            "editorial_review_structure",
            "editorial_review.md missing sections: " + ", ".join(missing_sections),
        )
        return
    result.add_pass("editorial_review_structure")

    placeholder_patterns = [
        r"^\s*-\s*$",
        r":\s*$",
        r"_Wpisz[^_]*_",
        r"\(uzupełnij\)",
    ]
    placeholder_hits = 0
    for pattern in placeholder_patterns:
        placeholder_hits += len(re.findall(pattern, text, flags=re.IGNORECASE | re.M))
    if placeholder_hits > 0:
        result.add_error(
            "editorial_review_complete",
            f"editorial_review.md still contains placeholder lines: {placeholder_hits}.",
        )
        return
    result.add_pass("editorial_review_complete")

    iterations = parse_iterations_completed(text)
    if iterations is None or iterations < 2:
        result.add_error(
            "editorial_iterations_pass",
            "editorial_review.md must record at least 2 editorial iterations before approval.",
        )
    else:
        result.add_pass("editorial_iterations_pass")

    logic_pass = parse_logic_pass(text)
    if logic_pass != "PASS":
        result.add_error(
            "editorial_logic_pass",
            "editorial_review.md must end with logic_pass: PASS.",
        )
    else:
        result.add_pass("editorial_logic_pass")

    post_machine_qa_revision = parse_post_machine_qa_revision(text)
    if post_machine_qa_revision != "yes":
        result.add_error(
            "post_machine_qa_revision_pass",
            "editorial_review.md must confirm post_machine_qa_revision_completed: yes.",
        )
    else:
        result.add_pass("post_machine_qa_revision_pass")

    final_decision = parse_final_decision(text)
    if final_decision != "approved":
        result.add_error(
            "editorial_final_decision",
            "editorial_review.md must end with final_decision: approved.",
        )
    else:
        result.add_pass("editorial_final_decision")


def validate_topic_from_approved_plan(workspace: Path, result: ValidationResult) -> None:
    context = parse_run_context(workspace / "run_context.md")
    planning_sprint_id = context.get("planning_sprint_id", "").strip()
    planning_topic_id = context.get("planning_topic_id", "").strip()
    planning_row_status = context.get("planning_row_status", "").strip().lower()
    planning_queue_path_raw = context.get("planning_queue_path", "").strip()

    if not planning_sprint_id:
        result.add_error(
            "topic_from_approved_plan",
            "Missing planning_sprint_id in run_context.md. Article must be sourced from Workflow A queue.",
        )
        return
    if not planning_topic_id:
        result.add_error(
            "topic_from_approved_plan",
            "Missing planning_topic_id in run_context.md. Article must map to approved topic row.",
        )
        return
    if planning_row_status != "approved":
        result.add_error(
            "topic_from_approved_plan",
            "planning_row_status must be 'approved' in run_context.md.",
        )
        return
    if not planning_queue_path_raw:
        result.add_error(
            "topic_from_approved_plan",
            "Missing planning_queue_path in run_context.md.",
        )
        return

    queue_path = Path(planning_queue_path_raw).expanduser()
    if not queue_path.is_absolute():
        queue_path = (workspace.parent.parent / queue_path).resolve()
    if not queue_path.exists():
        result.add_error(
            "topic_from_approved_plan",
            f"planning_queue_path does not exist: {queue_path}",
        )
        return

    matched_row: dict[str, str] | None = None
    try:
        with queue_path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if str(row.get("topic_id", "")).strip() == planning_topic_id:
                    matched_row = {key: str(value).strip() for key, value in row.items()}
                    break
    except Exception as exc:
        result.add_error("topic_from_approved_plan", f"Cannot read planning queue file: {exc}")
        return

    if not matched_row:
        result.add_error(
            "topic_from_approved_plan",
            f"planning_topic_id '{planning_topic_id}' not found in queue file: {queue_path}",
        )
        return

    if matched_row.get("workflow_b_ready", "").lower() != "yes":
        result.add_error(
            "topic_from_approved_plan",
            f"Queue row {planning_topic_id} is not workflow-ready ({matched_row.get('reason_if_no', 'unknown reason')}).",
        )
        return

    brief_path = workspace / "article_brief.md"
    if brief_path.exists():
        brief = read_text(brief_path)
        meta = parse_brief_metadata(brief)
        brief_company = str(meta.get("company", "")).strip().lower()
        queue_company = matched_row.get("company", "").strip().lower()
        if brief_company and queue_company and brief_company != queue_company:
            result.add_error(
                "topic_from_approved_plan",
                f"Company mismatch between brief ('{brief_company}') and queue ('{queue_company}').",
            )
            return

    result.add_pass("topic_from_approved_plan")


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
    if research_status not in {"ok", "ok_with_fallback"}:
        result.add_error(
            "research_fetch_status",
            "run_context.md research_fetch_status must be 'ok' or 'ok_with_fallback' before pre_export validation.",
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
    trend_query_count = max(trend_query_count, len(trend_queries))

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
            trend_query_count,
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


def validate_quality_gate(workspace: Path, result: ValidationResult, content_profile: str) -> None:
    payload = ensure_quality_gate(workspace)
    gates = payload.get("gates", {})
    if not isinstance(gates, dict):
        result.add_error("quality_gate_schema", "quality_gate.json gates must be an object.")
        return
    result.add_pass("quality_gate_schema")

    required_hard_gates = REQUIRED_HARD_GATES if content_profile == "article" else SERVICE_REQUIRED_HARD_GATES
    hard = payload.get("hard_gates", [])
    if not isinstance(hard, list):
        hard = []
    missing_hard = [name for name in required_hard_gates if name not in hard]
    if missing_hard:
        result.add_error("quality_gate_hard_set", "quality_gate.json hard_gates missing: " + ", ".join(missing_hard))
    else:
        result.add_pass("quality_gate_hard_set")

    for gate_name in required_hard_gates:
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


def validate_workspace(workspace: Path, mode: str, content_profile: str = "article") -> ValidationResult:
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

    effective_content_profile = resolve_content_profile(workspace, content_profile)
    result.add_pass(f"content_profile_{effective_content_profile}")

    if effective_content_profile == "service_page":
        missing_service = []
        for artifact in SERVICE_REQUIRED_ARTIFACTS:
            artifact_path = workspace / artifact
            if not artifact_path.exists():
                missing_service.append(artifact)
                continue
            if artifact_path.stat().st_size == 0:
                result.add_error(
                    f"non_empty_{artifact}",
                    f"Artifact is empty: {artifact_path}",
                )
            else:
                result.add_pass(f"non_empty_{artifact}")
        if missing_service:
            result.add_error(
                "service_artifacts_present",
                "Missing service_page artifacts: " + ", ".join(missing_service),
            )
        else:
            result.add_pass("service_artifacts_present")

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

        if effective_content_profile == "article":
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

    if effective_content_profile == "service_page":
        validate_service_page_sections(workspace, result)
    validate_editorial_review(workspace, result, effective_content_profile)

    validate_skills_policy(workspace, result)
    if effective_content_profile == "article":
        validate_topic_from_approved_plan(workspace, result)
    else:
        result.add_pass("topic_from_approved_plan_bypass_service_page")
    validate_quality_gate(workspace, result, effective_content_profile)

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
    parser.add_argument(
        "--content-profile",
        choices=["article", "service_page"],
        default="article",
        help="Validation profile. Use service_page for URL-first service content packages.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "pre_export" if args.mode == "final" else args.mode
    result = validate_workspace(args.workspace.resolve(), mode, content_profile=args.content_profile)

    if args.json:
        payload = {
            "ok": result.ok,
            "checks": result.checks,
            "errors": result.errors,
            "warnings": result.warnings,
            "workspace": str(args.workspace.resolve()),
            "mode": mode,
            "content_profile": args.content_profile,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Workspace: {args.workspace.resolve()}")
        print(f"Mode: {mode}")
        print(f"Content profile: {args.content_profile}")
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
