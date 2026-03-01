#!/usr/bin/env python3
"""Rule-based Polish naturalness checker for article workflow."""

from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from article_workflow_state import set_many_gates
from article_workflow_validate import clean_markdown_for_language_checks


BANNED_TITLE_PATTERNS = [
    r"\bkomu\b.{0,60}\bsi[eę]\s+sprawdza\b",
    r"\bco\s+naprawd[eę]\s+daje\s+i\s+komu\b",
]

BANNED_COLLOCATIONS = [
    "dowodzić w kalendarzu",
    "procesowo",
    "w dzisiejszych czasach",
    "warto zaznaczyć",
    "należy zaznaczyć",
    "kluczowe jest to",
    "na poziomie",
    "w obszarze",
]

KNOWN_UPPER_TOKENS = {
    "AI",
    "SEO",
    "GEO",
    "LLM",
    "CMS",
    "CTA",
    "SERP",
    "PAA",
    "FAQ",
    "JSON",
    "API",
    "PL",
    "WHO",
    "FDA",
    "EMS",
    "WB",
    "EEAT",
}


@dataclass
class Metrics:
    title_issues: list[str]
    collocation_hits: dict[str, int]
    unknown_uppercase_tokens: list[str]
    punctuation_issues: list[str]
    sentence_cv: float
    paragraph_cv: float
    max_sentence_bucket_share: float
    changed_ratio: float
    changed_paragraphs: int


def normalize(text: str) -> str:
    lowered = text.lower()
    return "".join(ch for ch in unicodedata.normalize("NFKD", lowered) if not unicodedata.combining(ch))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polish naturalness gate (rule-based).")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--input", default="article_draft_v2.md")
    parser.add_argument("--baseline", default="article_draft_v1.md")
    parser.add_argument("--report", default="polish_naturalness_report.md")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def split_sentences(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w\-ąćęłńóśżźĄĆĘŁŃÓŚŻŹ]+\b", text, flags=re.UNICODE))


def cv(values: list[int]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance) / mean


def paragraph_lengths(markdown: str) -> list[int]:
    lengths: list[int] = []
    for paragraph in re.split(r"\n\s*\n", markdown):
        stripped = paragraph.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cleaned = clean_markdown_for_language_checks(stripped)
        wc = word_count(cleaned)
        if wc > 0:
            lengths.append(wc)
    return lengths


def sentence_bucket_share(lengths: list[int], bucket_size: int = 4) -> float:
    if not lengths:
        return 0.0
    buckets = Counter((x // bucket_size) * bucket_size for x in lengths)
    return max(buckets.values()) / len(lengths)


def title_issues(title: str) -> list[str]:
    issues: list[str] = []
    title_norm = normalize(title)
    for pattern in BANNED_TITLE_PATTERNS:
        if re.search(pattern, title_norm, flags=re.IGNORECASE):
            issues.append(f"Pattern not allowed in title: {pattern}")
    if "  " in title:
        issues.append("Double space in title.")
    if title.endswith(":"):
        issues.append("Title ends with colon.")
    return issues


def collocation_hits(text: str) -> dict[str, int]:
    text_norm = normalize(text)
    hits: dict[str, int] = {}
    for phrase in BANNED_COLLOCATIONS:
        count = len(re.findall(rf"(?<!\w){re.escape(normalize(phrase))}(?!\w)", text_norm))
        if count:
            hits[phrase] = count
    return hits


def punctuation_issues(markdown: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    unknown_tokens: list[str] = []
    text = clean_markdown_for_language_checks(markdown)

    if re.search(r"\s+[,.!?;:]", text):
        issues.append("Found spaces before punctuation.")

    if text.count("„") != text.count("”"):
        issues.append("Unbalanced Polish quotation marks.")

    for token in re.findall(r"\b[A-Z]{2,4}\b", markdown):
        if token not in KNOWN_UPPER_TOKENS:
            unknown_tokens.append(token)
    if unknown_tokens:
        uniq = sorted(set(unknown_tokens))
        issues.append("Unknown uppercase abbreviations: " + ", ".join(uniq))
    return issues, sorted(set(unknown_tokens))


def semantic_rewrite_metrics(draft_v1: str, draft_v2: str) -> tuple[float, int]:
    if not draft_v1.strip() or not draft_v2.strip():
        return (0.0, 0)
    ratio = SequenceMatcher(a=draft_v1, b=draft_v2).ratio()
    changed_ratio = 1.0 - ratio

    p1 = [x.strip() for x in re.split(r"\n\s*\n", draft_v1) if x.strip()]
    p2 = [x.strip() for x in re.split(r"\n\s*\n", draft_v2) if x.strip()]
    changed = 0
    for idx in range(min(len(p1), len(p2))):
        pr = SequenceMatcher(a=p1[idx], b=p2[idx]).ratio()
        if pr < 0.85:
            changed += 1
    changed += max(0, len(p2) - len(p1))
    return (changed_ratio, changed)


def evaluate(markdown_v2: str, markdown_v1: str) -> tuple[dict[str, bool], Metrics]:
    title = extract_title(markdown_v2)
    cleaned = clean_markdown_for_language_checks(markdown_v2)
    title_problem_list = title_issues(title)
    collocations = collocation_hits(markdown_v2)
    punct_issues, unknown_upper = punctuation_issues(markdown_v2)

    sent = split_sentences(cleaned)
    sent_lengths = [word_count(x) for x in sent if word_count(x) > 0]
    para_lengths = paragraph_lengths(markdown_v2)
    sent_cv = cv(sent_lengths)
    para_cv = cv(para_lengths)
    bucket_share = sentence_bucket_share(sent_lengths)
    changed_ratio, changed_paragraphs = semantic_rewrite_metrics(markdown_v1, markdown_v2)

    min_sent_cv = float_env("PL_NATURALNESS_MIN_SENTENCE_CV", 0.62)
    min_para_cv = float_env("PL_NATURALNESS_MIN_PARAGRAPH_CV", 0.45)
    max_bucket = float_env("PL_NATURALNESS_MAX_SENTENCE_BUCKET_SHARE", 0.42)
    min_changed_ratio = float_env("PL_NATURALNESS_MIN_CHANGED_RATIO", 0.12)
    min_changed_paragraphs = int_env("PL_NATURALNESS_MIN_CHANGED_PARAGRAPHS", 3)

    gates = {
        "polish_title_naturalness_pass": len(title_problem_list) == 0,
        "polish_collocation_pass": not collocations,
        "polish_punctuation_pass": len(punct_issues) == 0,
        "structure_variance_pass_v2": (
            sent_cv >= min_sent_cv and para_cv >= min_para_cv and bucket_share <= max_bucket
        ),
        "semantic_rewrite_pass_v2": (
            changed_ratio >= min_changed_ratio and changed_paragraphs >= min_changed_paragraphs
        ),
    }

    metrics = Metrics(
        title_issues=title_problem_list,
        collocation_hits=collocations,
        unknown_uppercase_tokens=unknown_upper,
        punctuation_issues=punct_issues,
        sentence_cv=sent_cv,
        paragraph_cv=para_cv,
        max_sentence_bucket_share=bucket_share,
        changed_ratio=changed_ratio,
        changed_paragraphs=changed_paragraphs,
    )
    return gates, metrics


def float_env(name: str, default: float) -> float:
    import os

    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def int_env(name: str, default: int) -> int:
    import os

    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def write_report(path: Path, gates: dict[str, bool], metrics: Metrics) -> None:
    lines = [
        "# polish_naturalness_report.md",
        "",
        "## Gates",
    ]
    for key, value in gates.items():
        lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Metrics",
            f"- sentence_cv: {metrics.sentence_cv:.4f}",
            f"- paragraph_cv: {metrics.paragraph_cv:.4f}",
            f"- max_sentence_bucket_share: {metrics.max_sentence_bucket_share:.4f}",
            f"- changed_ratio_v1_v2: {metrics.changed_ratio:.4f}",
            f"- changed_paragraphs_v1_v2: {metrics.changed_paragraphs}",
        ]
    )
    lines.extend(["", "## Title issues"])
    lines.extend([f"- {x}" for x in metrics.title_issues] or ["- none"])
    lines.extend(["", "## Collocation hits"])
    if metrics.collocation_hits:
        for phrase, count in metrics.collocation_hits.items():
            lines.append(f"- {phrase}: {count}")
    else:
        lines.append("- none")
    lines.extend(["", "## Punctuation issues"])
    lines.extend([f"- {x}" for x in metrics.punctuation_issues] or ["- none"])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    source = workspace / args.input
    baseline = workspace / args.baseline
    if not workspace.exists() or not source.exists():
        print(f"ERROR: Missing workspace or source file: {workspace} / {source}")
        return 1

    draft_v2 = source.read_text(encoding="utf-8")
    draft_v1 = baseline.read_text(encoding="utf-8") if baseline.exists() else ""
    gates, metrics = evaluate(draft_v2, draft_v1)

    details = {
        "polish_title_naturalness_pass": "; ".join(metrics.title_issues) or "No blocked title patterns.",
        "polish_collocation_pass": "No blocked collocations." if not metrics.collocation_hits else str(metrics.collocation_hits),
        "polish_punctuation_pass": "; ".join(metrics.punctuation_issues) or "No punctuation issues.",
        "structure_variance_pass_v2": (
            f"sentence_cv={metrics.sentence_cv:.4f}, paragraph_cv={metrics.paragraph_cv:.4f}, "
            f"bucket_share={metrics.max_sentence_bucket_share:.4f}"
        ),
        "semantic_rewrite_pass_v2": (
            f"changed_ratio={metrics.changed_ratio:.4f}, changed_paragraphs={metrics.changed_paragraphs}"
        ),
    }
    set_many_gates(
        workspace,
        gates=gates,
        source="check_polish_naturalness.py",
        severity="hard",
        details=details,
    )

    report_path = workspace / args.report
    write_report(report_path, gates, metrics)
    payload = {
        "ok": all(gates.values()),
        "gates": gates,
        "metrics": {
            "title_issues": metrics.title_issues,
            "collocation_hits": metrics.collocation_hits,
            "unknown_uppercase_tokens": metrics.unknown_uppercase_tokens,
            "punctuation_issues": metrics.punctuation_issues,
            "sentence_cv": metrics.sentence_cv,
            "paragraph_cv": metrics.paragraph_cv,
            "max_sentence_bucket_share": metrics.max_sentence_bucket_share,
            "changed_ratio": metrics.changed_ratio,
            "changed_paragraphs": metrics.changed_paragraphs,
        },
        "report_path": str(report_path.resolve()),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Naturalness report: {report_path}")
        for name, passed in gates.items():
            print(f"- {name}: {'PASS' if passed else 'FAIL'}")
        print("Naturalness gate:", "PASS" if payload["ok"] else "FAIL")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

