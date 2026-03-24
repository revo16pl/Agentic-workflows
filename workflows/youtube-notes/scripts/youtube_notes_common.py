from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from youtube_notes_config import DECISION_PATTERNS, PROCEDURAL_PATTERNS, PROFILE_CONFIGS, TOOL_HINTS


TIMESTAMP_RE = re.compile(r"^\[(\d{1,3}):(\d{2})(?::(\d{2}))?\]\s*(.+?)\s*$")
WORD_RE = re.compile(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż0-9']+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class TranscriptEntry:
    timestamp: str
    start_seconds: int
    text: str


@dataclass(frozen=True)
class Segment:
    id: str
    start_seconds: int
    end_seconds: int
    summary: str
    procedural_points: list[str]
    decision_points: list[str]
    tools: list[str]



def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))



def normalize_sentence(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip())
    return normalized.rstrip(".,;: ")



def format_mmss(seconds: int) -> str:
    total = max(0, int(seconds))
    return f"{total // 60:02d}:{total % 60:02d}"



def parse_timestamp(part1: str, part2: str, part3: str | None) -> int:
    if part3 is None:
        return int(part1) * 60 + int(part2)
    return int(part1) * 3600 + int(part2) * 60 + int(part3)



def parse_transcript_markdown(path: str) -> dict[str, Any]:
    content = Path(path).read_text(encoding="utf-8")
    title_match = re.search(r"^# Transcript:\s*(.+)$", content, flags=re.M)
    url_match = re.search(r"^\*\*URL:\*\*\s*(.+)$", content, flags=re.M)
    video_title = title_match.group(1).strip() if title_match else "Untitled Video"
    video_url = url_match.group(1).strip() if url_match else ""

    entries: list[TranscriptEntry] = []
    max_seconds = 0
    for line in content.splitlines():
        match = TIMESTAMP_RE.match(line)
        if not match:
            continue
        start_seconds = parse_timestamp(match.group(1), match.group(2), match.group(3))
        text = re.sub(r"\s+", " ", match.group(4)).strip()
        if not text:
            continue
        entries.append(TranscriptEntry(timestamp=f"[{format_mmss(start_seconds)}]", start_seconds=start_seconds, text=text))
        max_seconds = max(max_seconds, start_seconds)

    duration_minutes = (max_seconds // 60) + (1 if max_seconds % 60 else 0)
    return {
        "video_title": video_title,
        "video_url": video_url,
        "entries": entries,
        "duration_minutes": duration_minutes,
    }



def resolve_profile(notes_profile: str, duration_minutes: int):
    if notes_profile in ("short", "standard", "deep"):
        return PROFILE_CONFIGS[notes_profile]
    if duration_minutes <= 20:
        return PROFILE_CONFIGS["short"]
    if duration_minutes <= 90:
        return PROFILE_CONFIGS["standard"]
    if duration_minutes <= 240:
        return PROFILE_CONFIGS["deep"]
    return PROFILE_CONFIGS["deep_plus"]



def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [normalize_sentence(s) for s in SENTENCE_SPLIT_RE.split(text) if normalize_sentence(s)]



def _pick_signal_sentences(sentences: list[str], patterns: tuple[str, ...], limit: int) -> list[str]:
    compiled = [re.compile(pattern, flags=re.I) for pattern in patterns]
    selected: list[str] = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) < 5 or len(words) > 40:
            continue
        if any(pattern.search(sentence) for pattern in compiled) and sentence not in selected:
            selected.append(sentence)
            if len(selected) >= limit:
                break
    return selected



def _detect_tools(segment_text: str, limit: int = 8) -> list[str]:
    found: list[str] = []
    for hint in TOOL_HINTS:
        if re.search(re.escape(hint), segment_text, flags=re.I):
            found.append(hint)
            if len(found) >= limit:
                break
    return found



def build_segments(entries: list[TranscriptEntry], window_minutes: int = 6) -> list[Segment]:
    if not entries:
        return []

    window_seconds = window_minutes * 60
    buckets: dict[int, list[TranscriptEntry]] = {}
    for entry in entries:
        buckets.setdefault(entry.start_seconds // window_seconds, []).append(entry)

    segments: list[Segment] = []
    for idx, bucket in enumerate(sorted(buckets.keys()), start=1):
        segment_entries = buckets[bucket]
        start_seconds = bucket * window_seconds
        end_seconds = start_seconds + window_seconds - 1
        merged_text = " ".join(entry.text for entry in segment_entries)
        sentences = split_sentences(merged_text)
        procedural_points = _pick_signal_sentences(sentences, PROCEDURAL_PATTERNS, limit=4)
        decision_points = _pick_signal_sentences(sentences, DECISION_PATTERNS, limit=4)

        fallback = [s for s in sentences if s not in procedural_points and s not in decision_points][:2]
        summary_source = procedural_points[:2] + decision_points[:1] + fallback[:1]
        summary = " ".join(summary_source)[:420].rstrip(" ,.;:") or " ".join(sentences[:2])[:420].rstrip(" ,.;:")
        segments.append(
            Segment(
                id=f"S{idx:02d}",
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                summary=summary,
                procedural_points=procedural_points,
                decision_points=decision_points,
                tools=_detect_tools(merged_text),
            )
        )
    return segments



def build_notes_context(
    *,
    transcript_path: str,
    transcript_data: dict[str, Any],
    profile,
    notes_profile_input: str,
    language_policy: str,
    evidence_mode: str,
) -> dict[str, Any]:
    segments = build_segments(transcript_data["entries"])
    context_segments = [
        {
            "id": segment.id,
            "range": f"{format_mmss(segment.start_seconds)}-{format_mmss(segment.end_seconds)}",
            "summary": segment.summary,
            "procedural_points": segment.procedural_points,
            "decision_points": segment.decision_points,
            "tools": segment.tools,
        }
        for segment in segments
    ]
    return {
        "workflow_version": "youtube_notes_v3",
        "transcript_path": str(transcript_path),
        "video_title": transcript_data["video_title"],
        "video_url": transcript_data["video_url"],
        "duration_minutes": transcript_data["duration_minutes"],
        "notes_profile_input": notes_profile_input,
        "effective_profile": profile.internal_name,
        "language_policy": language_policy,
        "evidence_mode": evidence_mode,
        "quality_targets": {
            "word_min": profile.word_min,
            "word_max": profile.word_max,
            "methods_min": profile.methods_min,
            "takeaways_min": profile.takeaways_min,
            "claims_min": profile.claims_min,
            "tldr_sentences": profile.tldr_sentences,
        },
        "segments": context_segments,
    }
