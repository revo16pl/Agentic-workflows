#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from youtube_notes_config import PROFILE_CONFIGS


WORD_RE = re.compile(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9']+")
REQUIRED_SECTIONS = (
    "## Core Concept",
    "## Actionable Methods & Workflows",
    "## Key Insights",
    "## Tools & Resources",
)


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    errors: list[str]
    warnings: list[str]
    metrics: dict[str, Any]



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate YouTube notes (v4 sanity checks).")
    parser.add_argument("notes_path", help="Path to notes markdown file.")
    parser.add_argument("--profile", choices=["short", "standard", "deep", "deep+"], default=None)
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    return parser.parse_args()



def _extract_metadata(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines()[:25]:
        match = re.match(r"^\*\*([^:]+):\*\*\s*(.+)$", line.strip())
        if match:
            data[match.group(1).strip().lower()] = match.group(2).strip()
    return data



def _extract_section_body(text: str, heading: str) -> str:
    marker = re.compile(rf"^{re.escape(heading)}\s*$", flags=re.M)
    match = marker.search(text)
    if not match:
        return ""
    next_heading = re.compile(r"^##\s+.+$", flags=re.M).search(text, pos=match.end())
    end = next_heading.start() if next_heading else len(text)
    return text[match.end() : end].strip()



def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))



def validate_notes(text: str, profile_name: str | None = None) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}

    if not text.strip():
        return ValidationResult(
            passed=False,
            errors=["Notes file is empty."],
            warnings=[],
            metrics={"word_count": 0},
        )

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"Missing section: {section}")

    for section in REQUIRED_SECTIONS:
        body = _extract_section_body(text, section)
        body_words = _word_count(body)
        metrics[f"{section.replace('## ', '').lower().replace(' & ', '_').replace(' ', '_')}_words"] = body_words
        if section in text and body_words < 40:
            errors.append(f"Section too short: {section} ({body_words} words)")

    word_count = _word_count(text)
    metrics["word_count"] = word_count

    if profile_name:
        profile = PROFILE_CONFIGS["deep_plus"] if profile_name == "deep+" else PROFILE_CONFIGS[profile_name]
        metrics["target_word_min"] = profile.word_min
        metrics["target_word_max"] = profile.word_max
        if word_count < profile.word_min:
            warnings.append(
                f"Word count is below target range for profile '{profile_name}': {word_count} < {profile.word_min}."
            )
        if word_count > profile.word_max:
            warnings.append(
                f"Word count is above target range for profile '{profile_name}': {word_count} > {profile.word_max}."
            )

    return ValidationResult(
        passed=not errors,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
    )



def main() -> int:
    args = parse_args()
    notes_path = Path(args.notes_path)
    if not notes_path.exists():
        raise SystemExit(f"Validation error: file not found: {notes_path}")

    text = notes_path.read_text(encoding="utf-8")
    metadata = _extract_metadata(text)
    profile_name = args.profile or metadata.get("profile", "")
    if profile_name and profile_name not in {"short", "standard", "deep", "deep+"}:
        profile_name = None

    result = validate_notes(text=text, profile_name=profile_name)
    payload = {
        "passed": result.passed,
        "errors": result.errors,
        "warnings": result.warnings,
        "metrics": result.metrics,
        "profile": profile_name or "unknown",
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Validation {'PASS' if result.passed else 'FAIL'}: {notes_path}")
        for key, value in result.metrics.items():
            print(f"- {key}: {value}")
        if result.warnings:
            print("Warnings:")
            for item in result.warnings:
                print(f"- {item}")
        if result.errors:
            print("Errors:")
            for item in result.errors:
                print(f"- {item}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
