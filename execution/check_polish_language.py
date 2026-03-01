#!/usr/bin/env python3
"""
Check and optionally auto-correct Polish language quality in article markdown.

Usage:
    python3 execution/check_polish_language.py \
      --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic" \
      --input article_draft_v2.md \
      --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from article_workflow_state import set_many_gates
from article_workflow_validate import (
    POLISH_DIACRITICS_REGEX,
    POLISH_LETTERS_REGEX,
    clean_markdown_for_language_checks,
    count_polish_grammar_issues,
    extract_prose_for_grammar_checks,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polish language QA + auto-correction.")
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace directory path.")
    parser.add_argument("--input", default="article_draft_v2.md", help="Input markdown filename.")
    parser.add_argument("--output", default=None, help="Output markdown filename (default: overwrite input).")
    parser.add_argument("--report", default="language_quality_report.md", help="Report filename in workspace.")
    parser.add_argument("--locale", default="pl-PL", help="LanguageTool locale, default: pl-PL.")
    parser.add_argument("--apply", action="store_true", help="Apply auto-corrections to markdown.")
    parser.add_argument(
        "--max-errors-per-1000",
        type=float,
        default=5.0,
        help="Max allowed grammar/spelling issues per 1000 words after correction.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Max correction iterations when --apply is enabled.",
    )
    parser.add_argument(
        "--min-diacritics",
        type=int,
        default=25,
        help="Minimum Polish diacritics count required.",
    )
    parser.add_argument(
        "--min-diacritics-ratio",
        type=float,
        default=0.003,
        help="Minimum Polish diacritics ratio (diacritics/letters).",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    parser.add_argument(
        "--protect-terms",
        default="",
        help="Comma-separated list of protected terms (never auto-corrected).",
    )
    return parser.parse_args()


@dataclass
class Segment:
    text: str
    correctable: bool


def load_language_tool(locale: str):
    provider = os.getenv("LANGUAGETOOL_PROVIDER", "auto").strip().lower()
    if provider in {"auto", "local"}:
        try:
            import language_tool_python

            return LocalToolAdapter(language_tool_python.LanguageTool(locale))
        except Exception as exc:  # pragma: no cover
            if provider == "local":
                raise RuntimeError(
                    "Cannot start local LanguageTool. Ensure Java is installed and LANGUAGETOOL_PROVIDER=local is valid."
                ) from exc

    if provider in {"auto", "http"}:
        return HttpToolAdapter(locale=locale)

    raise RuntimeError(f"Unsupported LANGUAGETOOL_PROVIDER value: {provider}")


class LocalToolAdapter:
    def __init__(self, tool) -> None:
        self.tool = tool

    def check(self, text: str) -> list[dict[str, object]]:
        raw = self.tool.check(text)
        results: list[dict[str, object]] = []
        for match in raw:
            results.append(
                {
                    "offset": int(getattr(match, "offset", 0)),
                    "length": int(getattr(match, "errorLength", 0)),
                    "message": getattr(match, "message", ""),
                    "context": {"text": getattr(match, "context", "")},
                    "ruleIssueType": getattr(match, "ruleIssueType", ""),
                    "category": getattr(match, "category", ""),
                    "replacements": [{"value": v} for v in getattr(match, "replacements", [])],
                }
            )
        return results

    def correct(self, text: str) -> str:
        return self.tool.correct(text)

    def close(self) -> None:
        self.tool.close()


class HttpToolAdapter:
    def __init__(self, locale: str) -> None:
        self.locale = locale
        self.api_url = os.getenv("LANGUAGETOOL_API_URL", "https://api.languagetool.org/v2/check")
        self.timeout = float(os.getenv("LANGUAGETOOL_TIMEOUT_SECONDS", "20"))
        self.disabled_rules = os.getenv("LANGUAGETOOL_DISABLED_RULES", "").strip()

    def check(self, text: str) -> list[dict[str, object]]:
        import requests

        payload = {"language": self.locale, "text": text}
        if self.disabled_rules:
            payload["disabledRules"] = self.disabled_rules
        response = requests.post(self.api_url, data=payload, timeout=self.timeout)
        response.raise_for_status()
        parsed = response.json()
        matches = parsed.get("matches", [])
        return matches if isinstance(matches, list) else []

    def correct(self, text: str) -> str:
        matches = self.check(text)
        if not matches:
            return text

        corrected = text
        # Apply from end to start to keep offsets valid.
        sortable: list[tuple[int, int, str]] = []
        for match in matches:
            if not isinstance(match, dict):
                continue
            offset = int(match.get("offset", 0))
            length = int(match.get("length", 0))
            replacements = match.get("replacements", [])
            replacement = ""
            if isinstance(replacements, list) and replacements:
                first = replacements[0]
                if isinstance(first, dict):
                    replacement = str(first.get("value", ""))
            if replacement and length >= 0:
                sortable.append((offset, length, replacement))

        for offset, length, replacement in sorted(sortable, key=lambda item: item[0], reverse=True):
            if offset < 0 or offset > len(corrected):
                continue
            end = min(offset + length, len(corrected))
            corrected = corrected[:offset] + replacement + corrected[end:]
        return corrected

    def close(self) -> None:
        return None


INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def resolve_protected_terms(raw_terms: str) -> list[str]:
    defaults = [
        "Kobido",
        "Studio Balans",
        "Niepołomice",
        "Niepolomice",
        "EMS",
    ]
    env_terms = os.getenv("LANGUAGE_PROTECTED_TERMS", "")
    merged = defaults + [x.strip() for x in env_terms.split(",")] + [x.strip() for x in raw_terms.split(",")]
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


def correct_inline_text(text: str, tool, protected_terms: list[str]) -> str:
    protected_code: list[str] = []
    protected_terms_map: dict[str, str] = {}

    def save_inline_code(match: re.Match[str]) -> str:
        protected_code.append(match.group(0))
        return f"__CODETOKEN_{len(protected_code)-1}__"

    masked = INLINE_CODE_PATTERN.sub(save_inline_code, text)

    for term in protected_terms:
        pattern = re.compile(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)
        if not pattern.search(masked):
            continue

        def save_term(match: re.Match[str]) -> str:
            token = f"__TERMTOKEN_{len(protected_terms_map)}__"
            protected_terms_map[token] = match.group(0)
            return token

        masked = pattern.sub(save_term, masked)

    rebuilt_parts: list[str] = []
    cursor = 0
    for link_match in LINK_PATTERN.finditer(masked):
        prefix = masked[cursor : link_match.start()]
        rebuilt_parts.append(tool.correct(prefix))

        link_text = link_match.group(1)
        link_url = link_match.group(2)
        corrected_link_text = tool.correct(link_text)
        rebuilt_parts.append(f"[{corrected_link_text}]({link_url})")
        cursor = link_match.end()

    rebuilt_parts.append(tool.correct(masked[cursor:]))
    corrected = "".join(rebuilt_parts)

    for idx, token in enumerate(protected_code):
        corrected = corrected.replace(f"__CODETOKEN_{idx}__", token)
    for token, value in protected_terms_map.items():
        corrected = corrected.replace(token, value)
    return corrected


def split_markdown_segments(markdown: str) -> list[Segment]:
    lines = markdown.splitlines(keepends=True)
    segments: list[Segment] = []
    in_code_block = False
    code_fence_pattern = re.compile(r"^\s*```")
    list_prefix_pattern = re.compile(r"^(\s*(?:[-*]|\d+\.)\s+)(.*)$")
    heading_prefix_pattern = re.compile(r"^(#{1,6}\s+)(.*)$")
    quote_prefix_pattern = re.compile(r"^(\s*>\s?)(.*)$")

    in_sources_section = False

    for line in lines:
        if code_fence_pattern.match(line):
            in_code_block = not in_code_block
            segments.append(Segment(text=line, correctable=False))
            continue

        if in_code_block:
            segments.append(Segment(text=line, correctable=False))
            continue

        if not line.strip():
            segments.append(Segment(text=line, correctable=False))
            continue

        if re.match(r"^#{1,6}\s*(Źródła|Zrodla|Sources)\s*$", line.strip(), flags=re.IGNORECASE):
            in_sources_section = True
            segments.append(Segment(text=line, correctable=False))
            continue

        if in_sources_section:
            segments.append(Segment(text=line, correctable=False))
            continue

        if line.strip().startswith("|"):
            # Tables often contain URLs and structured data; keep untouched.
            segments.append(Segment(text=line, correctable=False))
            continue

        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line

        for pattern in (heading_prefix_pattern, list_prefix_pattern, quote_prefix_pattern):
            match = pattern.match(body)
            if match:
                prefix = match.group(1)
                content = match.group(2)
                segments.append(Segment(text=prefix, correctable=False))
                segments.append(Segment(text=content, correctable=True))
                segments.append(Segment(text=newline, correctable=False))
                break
        else:
            segments.append(Segment(text=body, correctable=True))
            segments.append(Segment(text=newline, correctable=False))

    return segments


def correct_markdown(markdown: str, tool, protected_terms: list[str]) -> str:
    segments = split_markdown_segments(markdown)
    output: list[str] = []
    for segment in segments:
        if segment.correctable:
            output.append(correct_inline_text(segment.text, tool, protected_terms=protected_terms))
        else:
            output.append(segment.text)
    return "".join(output)


def polish_diacritics_stats(text: str) -> tuple[int, int, float]:
    letters = POLISH_LETTERS_REGEX.findall(text)
    diacritics = POLISH_DIACRITICS_REGEX.findall(text)
    total_letters = len(letters)
    diacritics_count = len(diacritics)
    ratio = (diacritics_count / total_letters) if total_letters else 0.0
    return diacritics_count, total_letters, ratio


def count_words(text: str) -> int:
    words = re.findall(r"\b[\w\-]+\b", text, flags=re.UNICODE)
    return len(words)


def write_report(
    report_path: Path,
    *,
    locale: str,
    input_path: Path,
    output_path: Path,
    issues_before: int,
    issues_after: int,
    allowed_issues: int,
    words: int,
    diacritics_count: int,
    letters_count: int,
    diacritics_ratio: float,
    diacritics_pass: bool,
    grammar_pass: bool,
    overall_pass: bool,
    samples: list[str],
) -> None:
    lines = [
        "# language_quality_report.md",
        "",
        f"- locale: {locale}",
        f"- input: {input_path.name}",
        f"- output: {output_path.name}",
        f"- words: {words}",
        f"- issues_before: {issues_before}",
        f"- issues_after: {issues_after}",
        f"- allowed_issues: {allowed_issues}",
        f"- diacritics_count: {diacritics_count}",
        f"- letters_count: {letters_count}",
        f"- diacritics_ratio: {diacritics_ratio:.4f}",
        f"- diacritics_pass: {'PASS' if diacritics_pass else 'FAIL'}",
        f"- grammar_pass: {'PASS' if grammar_pass else 'FAIL'}",
        f"- overall: {'PASS' if overall_pass else 'FAIL'}",
        "",
        "## Sample grammar issues",
    ]
    if samples:
        lines.extend([f"- {item}" for item in samples])
    else:
        lines.append("- none")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_qa_gates(workspace: Path, diacritics_pass: bool, grammar_pass: bool) -> None:
    qa_path = workspace / "qa_report.md"
    if not qa_path.exists():
        return

    text = qa_path.read_text(encoding="utf-8")
    gates = {
        "polish_diacritics_pass": "PASS" if diacritics_pass else "FAIL",
        "polish_grammar_pass": "PASS" if grammar_pass else "FAIL",
    }

    for gate, status in gates.items():
        pattern = rf"(^-\s*{re.escape(gate)}\s*:\s*)(PASS|FAIL)"
        if re.search(pattern, text, flags=re.M):
            text = re.sub(pattern, rf"\1{status}", text, flags=re.M)
        else:
            text += f"\n- {gate}: {status}"

    qa_path.write_text(text, encoding="utf-8")


def update_quality_gate(
    workspace: Path,
    *,
    diacritics_pass: bool,
    grammar_pass: bool,
    diacritics_count: int,
    letters_count: int,
    diacritics_ratio: float,
    issues_after: int,
    allowed_issues: int,
) -> None:
    details = {
        "polish_diacritics_pass": (
            f"diacritics={diacritics_count}, letters={letters_count}, ratio={diacritics_ratio:.4f}"
        ),
        "polish_grammar_pass": f"issues_after={issues_after}, allowed_issues={allowed_issues}",
    }
    set_many_gates(
        workspace=workspace,
        gates={
            "polish_diacritics_pass": diacritics_pass,
            "polish_grammar_pass": grammar_pass,
        },
        source="check_polish_language.py",
        severity="hard",
        details=details,
    )


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    if not workspace.exists():
        print(f"ERROR: Workspace not found: {workspace}", file=sys.stderr)
        return 1

    input_path = workspace / args.input
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        return 1

    output_name = args.output or args.input
    output_path = workspace / output_name
    report_path = workspace / args.report

    original_markdown = input_path.read_text(encoding="utf-8")
    cleaned_before = clean_markdown_for_language_checks(original_markdown)
    grammar_before = extract_prose_for_grammar_checks(original_markdown)
    if count_words(grammar_before) < 300:
        grammar_before = cleaned_before
    protected_terms = resolve_protected_terms(args.protect_terms)

    try:
        tool = load_language_tool(args.locale)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        matches_before = tool.check(grammar_before)
        issues_before, samples_before = count_polish_grammar_issues(
            matches_before,
            source_text=grammar_before,
        )

        processed_markdown = original_markdown
        if args.apply:
            previous_issue_count = issues_before
            for _ in range(max(1, args.max_iterations)):
                candidate = correct_markdown(processed_markdown, tool, protected_terms=protected_terms)
                if candidate == processed_markdown:
                    break
                candidate_grammar = extract_prose_for_grammar_checks(candidate)
                if count_words(candidate_grammar) < 300:
                    candidate_grammar = clean_markdown_for_language_checks(candidate)
                candidate_matches = tool.check(candidate_grammar)
                candidate_issues, _ = count_polish_grammar_issues(
                    candidate_matches,
                    source_text=candidate_grammar,
                )
                processed_markdown = candidate
                if candidate_issues >= previous_issue_count:
                    break
                previous_issue_count = candidate_issues
            output_path.write_text(processed_markdown, encoding="utf-8")

        cleaned_after = clean_markdown_for_language_checks(processed_markdown)
        grammar_after = extract_prose_for_grammar_checks(processed_markdown)
        if count_words(grammar_after) < 300:
            grammar_after = cleaned_after
        matches_after = tool.check(grammar_after)
        issues_after, samples_after = count_polish_grammar_issues(
            matches_after,
            source_text=grammar_after,
        )

        words = count_words(grammar_after)
        allowed_issues = max(5, round((words / 1000) * args.max_errors_per_1000))

        diacritics_count, letters_count, diacritics_ratio = polish_diacritics_stats(cleaned_after)
        diacritics_pass = (
            diacritics_count >= args.min_diacritics and diacritics_ratio >= args.min_diacritics_ratio
        )
        grammar_pass = issues_after <= allowed_issues
        overall_pass = diacritics_pass and grammar_pass

        write_report(
            report_path,
            locale=args.locale,
            input_path=input_path,
            output_path=output_path,
            issues_before=issues_before,
            issues_after=issues_after,
            allowed_issues=allowed_issues,
            words=words,
            diacritics_count=diacritics_count,
            letters_count=letters_count,
            diacritics_ratio=diacritics_ratio,
            diacritics_pass=diacritics_pass,
            grammar_pass=grammar_pass,
            overall_pass=overall_pass,
            samples=samples_after or samples_before,
        )
        update_qa_gates(
            workspace=workspace,
            diacritics_pass=diacritics_pass,
            grammar_pass=grammar_pass,
        )
        update_quality_gate(
            workspace=workspace,
            diacritics_pass=diacritics_pass,
            grammar_pass=grammar_pass,
            diacritics_count=diacritics_count,
            letters_count=letters_count,
            diacritics_ratio=diacritics_ratio,
            issues_after=issues_after,
            allowed_issues=allowed_issues,
        )

        payload = {
            "ok": overall_pass,
            "issues_before": issues_before,
            "issues_after": issues_after,
            "allowed_issues": allowed_issues,
            "words": words,
            "diacritics_count": diacritics_count,
            "letters_count": letters_count,
            "diacritics_ratio": diacritics_ratio,
            "diacritics_pass": diacritics_pass,
            "grammar_pass": grammar_pass,
            "report_path": str(report_path),
            "output_path": str(output_path),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Language check report: {report_path}")
            print(f"issues_before={issues_before}, issues_after={issues_after}, allowed={allowed_issues}")
            print(
                f"diacritics={diacritics_count}, ratio={diacritics_ratio:.4f}, "
                f"diacritics_pass={diacritics_pass}, grammar_pass={grammar_pass}"
            )
            print("Language gate:", "PASS" if overall_pass else "FAIL")

        return 0 if overall_pass else 1
    finally:
        tool.close()


if __name__ == "__main__":
    raise SystemExit(main())
