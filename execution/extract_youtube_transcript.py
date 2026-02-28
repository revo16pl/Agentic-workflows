import sys
import os
import requests
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
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
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        matches = re.findall(r'<title>(.*?)</title>', response.text)
        if matches:
            title = matches[0].replace(" - YouTube", "")
            return title
        return video_id
    except Exception as e:
        print(f"Warning: Could not fetch video title: {e}")
        return video_id

def sanitize_filename(name):
    # Remove invalid characters
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

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
        base_dir = "YouTube_transcripts"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        # Create video-specific directory
        video_dir = os.path.join(base_dir, safe_title)
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)

        # Format the transcript
        # We'll create a simple markdown format with timestamps
        markdown_content = f"# Transcript: {raw_title}\n\n"
        markdown_content += f"**Video ID:** {video_id}\n"
        markdown_content += f"**URL:** {video_url}\n\n"
        
        for entry in transcript:
            start_time = int(entry.start)
            minutes = start_time // 60
            seconds = start_time % 60
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            text = entry.text
            markdown_content += f"{timestamp} {text}\n\n"

        # Truncate title for filename (max 30 characters)
        if len(safe_title) > 30:
            truncated_title = safe_title[:30] + "..."
        else:
            truncated_title = safe_title

        # Save transcript as "Transcript - [Truncated Title].md"
        transcript_filename = f"Transcript - {truncated_title}.md"
        output_file = os.path.join(video_dir, transcript_filename)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Transcript saved to: {output_file}")
        
        # Print the directory and truncated title so the directive knows where to save notes and how to name them
        print(f"Output directory: {video_dir}")
        print(f"Truncated title used: {truncated_title}")

    except Exception as e:
        print(f"Error extracting transcript: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
