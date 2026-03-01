"""Style heuristics for humanization QA."""
from __future__ import annotations

import math
import os
import re
from pathlib import Path

from article_workflow_validate import clean_markdown_for_language_checks, parse_brief_metadata

DEFAULT_FORBIDDEN = [
    "procesowo",
    "holistycznie",
    "w dzisiejszych czasach",
    "w niniejszym artykule",
    "nalezy podkreslic",
    "nalezy zaznaczyc",
    "warto podkreslic",
    "warto zaznaczyc",
    "nie da sie ukryc",
    "kluczowe jest to",
    "kluczowe jest",
    "nie ulega watpliwosci",
    "na poziomie",
    "w obszarze",
]
DEFAULT_FILLERS = ["ponadto", "dodatkowo", "co wiecej", "w konsekwencji", "tym samym", "podsumowujac"]
DEFAULT_JARGON = [
    "kompleksowo",
    "optymalizacja",
    "synergia",
    "transformacja",
    "skalowalny",
    "w obszarze",
    "na poziomie",
    "interdyscyplinarny",
]
GENERIC_LEAD_PHRASES = [
    "w dzisiejszych czasach",
    "nie da sie ukryc",
    "nalezy podkreslic",
    "w niniejszym artykule",
    "temat jest bardzo wazny",
    "na poczatku warto zaznaczyc",
]
SECOND_PERSON = ["ty ", "tobie", "ciebie", "ci ", "twoj", "twoja", "twoje", "twoim", "dla ciebie"]
SERVICE_MARKERS = ["usluga", "zabieg", "konsultacja", "plan", "rezerwacja", "trening", "masaz", "terapia"]


def norm(text: str) -> str:
    return text.lower().translate(
        str.maketrans({"ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ż": "z", "ź": "z"})
    )


def wc(text: str) -> int:
    return len(re.findall(r"\b[\w\-]+\b", text, flags=re.UNICODE))


def mean(xs: list[float]) -> float:
    return (sum(xs) / len(xs)) if xs else 0.0


def std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def hits(text_norm: str, phrases: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for phrase in phrases:
        if not phrase:
            continue
        count = len(re.findall(rf"(?<!\w){re.escape(phrase)}(?!\w)", text_norm))
        if count:
            out[phrase] = count
    return out


def split_sentences(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]


def sentence_openings(text: str, tokens_count: int = 1) -> list[str]:
    out: list[str] = []
    for sentence in split_sentences(text):
        tokens = re.findall(r"\b[\w\-]+\b", norm(sentence))
        if tokens:
            out.append(" ".join(tokens[:tokens_count]))
    return out


def most_common_share(items: list[str]) -> float:
    if not items:
        return 0.0
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return max(counts.values()) / len(items)


def max_run(items: list[str]) -> int:
    if not items:
        return 0
    best = 1
    curr = 1
    prev = items[0]
    for item in items[1:]:
        if item == prev:
            curr += 1
        else:
            best = max(best, curr)
            curr = 1
            prev = item
    return max(best, curr)


def paragraphs(md: str) -> list[str]:
    out: list[str] = []
    for paragraph in [x.strip() for x in re.split(r"\n\s*\n", md) if x.strip()]:
        if paragraph.startswith("#"):
            continue
        out.append(paragraph)
    return out


def paragraph_openings(md: str) -> list[str]:
    out: list[str] = []
    for paragraph in paragraphs(md):
        line = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", paragraph.splitlines()[0].strip())
        tokens = re.findall(r"\b[\w\-]+\b", norm(line))
        if tokens:
            out.append(" ".join(tokens[:2]))
    return out


def links(md: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\((https?://[^)\s]+)\)", md)


def parse_brief(path: Path) -> dict[str, str]:
    return parse_brief_metadata(path.read_text(encoding="utf-8")) if path.exists() else {}


def service_marker_hits(text_norm: str) -> int:
    return sum(len(re.findall(rf"(?<!\w){re.escape(x)}(?!\w)", text_norm)) for x in SERVICE_MARKERS)


def style_checks(md: str, brief: dict[str, str]) -> dict[str, object]:
    cleaned = clean_markdown_for_language_checks(md)
    text_norm = norm(cleaned)
    words = wc(cleaned)

    sentence_lengths = [wc(s) for s in split_sentences(cleaned) if wc(s) > 0]
    sent_mean = mean([float(x) for x in sentence_lengths]) if sentence_lengths else 0.0
    sent_cv = (std([float(x) for x in sentence_lengths]) / sent_mean) if sent_mean else 0.0
    sentence_uniform_share = 0.0
    if sentence_lengths and sent_mean:
        low, high = sent_mean * 0.85, sent_mean * 1.15
        sentence_uniform_share = sum(1 for x in sentence_lengths if low <= x <= high) / len(sentence_lengths)

    sentence_opening_items = sentence_openings(cleaned, tokens_count=1)
    sentence_opening_repeat_share = most_common_share(sentence_opening_items)
    sentence_opening_max_run = max_run(sentence_opening_items)

    paragraph_items = paragraphs(md)
    paragraph_lengths = [wc(clean_markdown_for_language_checks(p)) for p in paragraph_items if wc(clean_markdown_for_language_checks(p)) > 0]
    para_mean = mean([float(x) for x in paragraph_lengths]) if paragraph_lengths else 0.0
    para_cv = (std([float(x) for x in paragraph_lengths]) / para_mean) if para_mean else 0.0
    short_para_share = 0.0
    if paragraph_lengths:
        limit = int(os.getenv("HUMAN_SHORT_PARAGRAPH_WORDS", "35"))
        short_para_share = sum(1 for x in paragraph_lengths if x < limit) / len(paragraph_lengths)

    opening_list = paragraph_openings(md)
    opening_repeat_share = 1.0 - (len(set(opening_list)) / len(opening_list)) if opening_list else 0.0

    forbidden = [norm(x) for x in DEFAULT_FORBIDDEN]
    forbidden += [norm(x.strip()) for x in os.getenv("HUMAN_FORBIDDEN_PHRASES", "").split(",") if x.strip()]
    forbidden_hits = hits(text_norm, forbidden)
    forbidden_total = sum(forbidden_hits.values())

    filler_hits = hits(text_norm, [norm(x) for x in DEFAULT_FILLERS])
    filler_density = (sum(filler_hits.values()) / max(1, words)) * 1000

    jargon_hits = hits(text_norm, [norm(x) for x in DEFAULT_JARGON])
    jargon_density = (sum(jargon_hits.values()) / max(1, words)) * 1000

    triad_count = len(re.findall(r"\b[\w\-]+,\s+[\w\-]+\s+i\s+[\w\-]+\b", text_norm))
    triad_density = (triad_count / max(1, words)) * 1000

    lead_words = " ".join(cleaned.split()[: int(os.getenv("HUMAN_LEAD_WORD_WINDOW", "180"))])
    lead_hits = hits(norm(lead_words), [norm(x) for x in GENERIC_LEAD_PHRASES])
    generic_lead_hits = sum(lead_hits.values())

    digits_count = len(re.findall(r"\d+", cleaned))
    numeric_context_count = len(re.findall(r"\b\d+\s*(%|min|minut|dni|tygodni|miesiecy|sesji|zabiegow|zabiegi)\b", text_norm))
    examples_count = len(re.findall(r"\b(np\.|na przyklad|w praktyce|krok|przyklad)\b", text_norm))
    links_count = len(links(md))
    question_marks = cleaned.count("?")

    company = norm(brief.get("company", ""))
    city = norm((brief.get("primary_city_or_region", "") or ""))
    intent = norm(brief.get("target_intent", ""))
    local_hits = (text_norm.count(company) if company else 0) + (text_norm.count(city) if city and city != "null" else 0)
    second_person_hits = sum(len(re.findall(re.escape(norm(marker)), text_norm)) for marker in SECOND_PERSON)
    service_hits = service_marker_hits(text_norm)
    nominalization_count = len(re.findall(r"\b\w+(izacja|owanie|ywanie)\b", text_norm))
    nominalization_density = (nominalization_count / max(1, words)) * 1000

    need_local = intent == "local" or bool(city and city != "null")
    need_second = ("studio balans" in company) or ("balans" in company)

    specificity_points = 0
    if digits_count >= int(os.getenv("HUMAN_MIN_DIGITS", "4")):
        specificity_points += 1
    if numeric_context_count >= int(os.getenv("HUMAN_MIN_NUMERIC_CONTEXTS", "2")):
        specificity_points += 1
    if examples_count >= int(os.getenv("HUMAN_MIN_EXAMPLE_MARKERS", "2")):
        specificity_points += 1
    if links_count >= int(os.getenv("HUMAN_MIN_LINKS", "2")):
        specificity_points += 1
    if service_hits >= int(os.getenv("HUMAN_MIN_SERVICE_MARKER_HITS", "3")):
        specificity_points += 1
    if (not need_local) or local_hits >= int(os.getenv("HUMAN_MIN_LOCAL_HITS", "2")):
        specificity_points += 1

    gates = {
        "forbidden_phrase_pass": forbidden_total <= int(os.getenv("HUMAN_MAX_FORBIDDEN_HITS", "0")),
        "structure_variance_pass": (
            sent_cv >= float(os.getenv("HUMAN_MIN_SENTENCE_CV", "0.48"))
            and sentence_uniform_share <= float(os.getenv("HUMAN_MAX_SENTENCE_UNIFORM_SHARE", "0.62"))
            and para_cv >= float(os.getenv("HUMAN_MIN_PARAGRAPH_CV", "0.34"))
            and opening_repeat_share <= float(os.getenv("HUMAN_MAX_PARAGRAPH_OPENING_REPEAT_SHARE", "0.28"))
            and sentence_opening_repeat_share <= float(os.getenv("HUMAN_MAX_SENTENCE_OPENING_REPEAT_SHARE", "0.18"))
            and sentence_opening_max_run <= int(os.getenv("HUMAN_MAX_SENTENCE_OPENING_RUN", "2"))
            and filler_density <= float(os.getenv("HUMAN_MAX_FILLER_PER_1000", "6.0"))
            and triad_density <= float(os.getenv("HUMAN_MAX_TRIADS_PER_1000", "3.0"))
        ),
        "specificity_pass": specificity_points >= int(os.getenv("HUMAN_MIN_SPECIFICITY_POINTS", "5")),
        "voice_authenticity_pass": (
            jargon_density <= float(os.getenv("HUMAN_MAX_JARGON_PER_1000", "5.0"))
            and nominalization_density <= float(os.getenv("HUMAN_MAX_NOMINALIZATIONS_PER_1000", "14.0"))
            and generic_lead_hits <= int(os.getenv("HUMAN_MAX_GENERIC_LEAD_HITS", "0"))
            and short_para_share <= float(os.getenv("HUMAN_MAX_SHORT_PARAGRAPH_SHARE", "0.55"))
            and ((not need_second) or second_person_hits >= int(os.getenv("HUMAN_MIN_SECOND_PERSON_HITS", "6")))
            and ((not need_second) or question_marks >= int(os.getenv("HUMAN_MIN_QUESTIONS_FOR_CONVERSATIONAL_VOICE", "2")))
        ),
    }

    metrics = {
        "words": words,
        "sentence_cv": sent_cv,
        "sentence_uniform_share": sentence_uniform_share,
        "sentence_opening_repeat_share": sentence_opening_repeat_share,
        "sentence_opening_max_run": sentence_opening_max_run,
        "paragraph_cv": para_cv,
        "short_paragraph_share": short_para_share,
        "paragraph_opening_repeat_share": opening_repeat_share,
        "forbidden_hits": forbidden_hits,
        "filler_density_per_1000": filler_density,
        "jargon_density_per_1000": jargon_density,
        "nominalization_density_per_1000": nominalization_density,
        "triad_density_per_1000": triad_density,
        "generic_lead_hits": generic_lead_hits,
        "digits_count": digits_count,
        "numeric_context_count": numeric_context_count,
        "example_markers": examples_count,
        "links_count": links_count,
        "question_marks": question_marks,
        "local_hits": local_hits,
        "service_hits": service_hits,
        "second_person_hits": second_person_hits,
        "specificity_points": specificity_points,
    }
    return {"gates": gates, "metrics": metrics}


def update_qa(qa_path: Path, gates: dict[str, bool]) -> None:
    if not qa_path.exists():
        return
    text = qa_path.read_text(encoding="utf-8")
    for gate, status in gates.items():
        value = "PASS" if status else "FAIL"
        pattern = rf"(^-\s*{re.escape(gate)}\s*:\s*)(PASS|FAIL)"
        text = re.sub(pattern, rf"\1{value}", text, flags=re.M) if re.search(pattern, text, flags=re.M) else text + f"\n- {gate}: {value}"
    qa_path.write_text(text, encoding="utf-8")


def write_report(path: Path, payload: dict[str, object]) -> None:
    lines = ["# humanization_report.md", "", f"- overall: {'PASS' if payload['ok'] else 'FAIL'}", "", "## Gates"]
    lines.extend([f"- {k}: {'PASS' if v else 'FAIL'}" for k, v in payload["gates"].items()])
    lines.extend(
        [
            "",
            "## Style metrics",
            *[f"- {k}: {v}" for k, v in payload["style_metrics"].items()],
            "",
            "## Detector ensemble",
            f"- detectors_run: {payload['detector']['detectors_run']}",
            f"- mean_ai_risk: {payload['detector']['mean_ai_risk']:.3f}",
            f"- max_single_ai_risk: {payload['detector']['max_single_ai_risk']:.3f}",
            f"- max_ai_prob: {payload['detector']['max_ai_prob']:.3f}",
            f"- max_single_ai_prob: {payload['detector']['max_single_ai_prob']:.3f}",
        ]
    )
    for item in payload["detector"]["results"]:
        lines.append(f"- model {item['model']}: avg_ai_risk={float(item['avg_ai_risk']):.3f}, pass={'PASS' if item['pass'] else 'FAIL'}")
    for err in payload["detector"]["errors"]:
        lines.append(f"- detector_error: {err}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
