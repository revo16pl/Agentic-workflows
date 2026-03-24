import sys
import os
import requests
import re
import math
import html
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


PARAGRAPH_BREAK_GAP_SECONDS = 7.0
TARGET_PARAGRAPH_WORDS = 90
MIN_PARAGRAPH_WORDS = 35
HARD_MAX_PARAGRAPH_WORDS = 150
SENTENCE_END_RE = re.compile(r'[.!?]["\']?$')
PROJECT_ROOT = Path(__file__).resolve().parents[3]

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
        if query.path[:8] == '/shorts/':
            return query.path.split('/')[2]
    # fail?
    return None

def get_video_title(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        # We need a user agent, otherwise YouTube might block or give a consent page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        matches = re.findall(r'<title>(.*?)</title>', response.text)
        if matches:
            title = html.unescape(matches[0]).replace(" - YouTube", "")
            return title
        return video_id
    except Exception as e:
        print(f"Warning: Could not fetch video title: {e}")
        return video_id

def sanitize_filename(name):
    # Remove invalid characters
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def clean_transcript_text(text):
    text = html.unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text


def format_timestamp(seconds):
    total_seconds = max(0, int(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"


def paragraph_word_count(parts):
    return sum(len(part.split()) for part in parts)


def should_break_paragraph(current_parts, current_text, gap_seconds):
    if not current_parts:
        return False
    words = paragraph_word_count(current_parts)
    if gap_seconds >= PARAGRAPH_BREAK_GAP_SECONDS and words >= MIN_PARAGRAPH_WORDS:
        return True
    if words >= TARGET_PARAGRAPH_WORDS and SENTENCE_END_RE.search(current_text):
        return True
    if words >= HARD_MAX_PARAGRAPH_WORDS:
        return True
    return False


def build_paragraphs(transcript):
    paragraphs = []
    current_parts = []
    current_start = None
    previous_end = None

    for entry in transcript:
        text = clean_transcript_text(entry.text)
        if not text:
            continue

        start_seconds = float(entry.start)
        duration = float(getattr(entry, "duration", 0.0))
        gap_seconds = 0.0 if previous_end is None else max(0.0, start_seconds - previous_end)
        current_text = " ".join(current_parts).strip()

        if should_break_paragraph(current_parts, current_text, gap_seconds):
            paragraphs.append((current_start, current_text))
            current_parts = []
            current_start = None

        if current_start is None:
            current_start = start_seconds

        current_parts.append(text)
        previous_end = start_seconds + duration

    final_text = " ".join(current_parts).strip()
    if current_start is not None and final_text:
        paragraphs.append((current_start, final_text))

    return paragraphs

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_youtube_transcript.py <youtube_url>")
        sys.exit(1)

    video_url = sys.argv[1]
    video_id = get_video_id(video_url)

    if not video_id:
        print("Error: Could not extract video ID from URL.")
        sys.exit(1)

    # Fetch title
    raw_title = get_video_title(video_id)
    safe_title = sanitize_filename(raw_title)
    if not safe_title:
        safe_title = video_id
        
    print(f"Processing video: {raw_title} ({video_id})")

    try:
        # Initializing the API instance
        yt = YouTubeTranscriptApi()
        
        # specific language behavior can be adjusted here if needed, defaults to 'en'
        # fetch() is a shortcut for list().find_transcript().fetch()
        transcript = yt.fetch(video_id)
        
        # Create base output directory if it doesn't exist
        base_dir = PROJECT_ROOT / "runtime" / "youtube-notes"
        base_dir.mkdir(parents=True, exist_ok=True)
            
        # Create video-specific directory
        video_dir = base_dir / safe_title
        video_dir.mkdir(parents=True, exist_ok=True)

        max_end_seconds = 0.0
        for entry in transcript:
            duration = float(getattr(entry, "duration", 0.0))
            max_end_seconds = max(max_end_seconds, float(entry.start) + duration)

        paragraphs = build_paragraphs(transcript)
        markdown_content = f"# Transcript: {raw_title}\n\n"
        markdown_content += f"**Video ID:** {video_id}\n"
        markdown_content += f"**URL:** {video_url}\n"
        markdown_content += (
            f"**Estimated duration minutes:** "
            f"{int(math.ceil(max_end_seconds / 60)) if max_end_seconds > 0 else 0}\n"
        )
        markdown_content += f"**Transcript paragraphs:** {len(paragraphs)}\n\n"
        markdown_content += "## Transcript\n\n"
        for start_seconds, paragraph in paragraphs:
            markdown_content += f"{format_timestamp(start_seconds)} {paragraph}\n\n"

        # Truncate title for filename (max 30 characters)
        if len(safe_title) > 30:
            truncated_title = safe_title[:30] + "..."
        else:
            truncated_title = safe_title

        # Save transcript as "Transcript - [Truncated Title].md"
        transcript_filename = f"Transcript - {truncated_title}.md"
        output_file = video_dir / transcript_filename
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Transcript saved to: {output_file}")
        
        # Print the directory and truncated title so the directive knows where to save notes and how to name them
        print(f"Output directory: {video_dir}")
        print(f"Truncated title used: {truncated_title}")
        estimated_duration_minutes = int(math.ceil(max_end_seconds / 60)) if max_end_seconds > 0 else 0
        print(f"Estimated duration minutes: {estimated_duration_minutes}")

    except Exception as e:
        print(f"Error extracting transcript: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
