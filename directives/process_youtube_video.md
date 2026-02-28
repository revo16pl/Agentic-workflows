# Directive: Process YouTube Video

**Goal**: Extract a transcript from a YouTube video and generate a structured summary of actionable knowledge, methods, and insights.

## Inputs
- `video_url`: The URL of the YouTube video to process.

## Tools
- `execution/extract_youtube_transcript.py`: Extracts the transcript.
- `view_file`: Reads the generated transcript.
- `write_to_file`: Saves the summary.

## Workflow

1.  **Extract Transcript**
    - Run the extraction script:
      ```bash
      .venv/bin/python execution/extract_youtube_transcript.py "{video_url}"
      ```
    - The script will create a folder `YouTube_transcripts/[Video Title]/`.
    - Inside, it creates a file named `Transcript - [Truncated Title]....md`.
    - **Note**: The script prints the "Truncated title used" in the output. Use this exactly.

2.  **Read Transcript**
    - Use `view_file` to read the content of the generated transcript file.

3.  **Analyze and Summarize**
    - Analyze the transcript to identify:
        - **Core Concepts**: What is the video mainly about?
        - **Actionable Methods/Techniques**: specific steps, workflows, or techniques described.
        - **Tools/Resources**: Any tools or resources mentioned.
        - **Key Insights**: "Aha!" moments or counter-intuitive points.
    - **Crucial**: Focus on *concrete* information. Avoid generic summaries like "The speaker talks about X." Instead, write "To do X, follow these steps: 1, 2, 3."

4.  **Create Notes Artifact**
    - Create a new Markdown file in the *same folder* as the transcript.
    - Name it: `Notes - [Truncated Title]...md`.
    - **Important**: Use the *same* truncated title as the transcript file (max 30 chars + "...").
    - Content structure:
      ```markdown
      # Notes: [Video Title]

      ## 🚀 Core Concept
      ...

      ## 🛠️ Actionable Methods & Workflows
      ...

      ## 💡 Key Insights
      ...

      ## 🔗 Tools & Resources
      ...
      ```

5.  **Notify User**
    - Inform the user that the transcript and summary have been generated.
