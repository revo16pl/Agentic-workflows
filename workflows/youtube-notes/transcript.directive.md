# Directive: Process YouTube Video (Transcript Only, v5)

**Goal**: Wyciągnąć z filmu YouTube dobry, czytelny transkrypt w Markdown. Ten workflow nie robi już notatek ani podsumowań. Ma kończyć się wyłącznie na gotowym transkrypcie, który później może być wejściem do osobnego workflow notatek.

## Inputs
- `video_url` (required)

## Outputs
- `Transcript - [Truncated Title].md`

## Tools
- `workflows/youtube-notes/scripts/extract_youtube_transcript.py`

## Workflow
1. **Extract transcript**
```bash
python3 workflows/youtube-notes/scripts/extract_youtube_transcript.py "{video_url}"
```

2. **Return only transcript artifact**
- Wynik końcowy to ścieżka do pliku transkryptu.
- Nie generuj `Notes - ...md`.
- Nie uruchamiaj `generate_youtube_notes.py`.
- Nie uruchamiaj `validate_youtube_notes.py`.

## Required Transcript Format
```markdown
# Transcript: [Video Title]

**Video ID:** ...
**URL:** ...
**Estimated duration minutes:** ...
**Transcript paragraphs:** ...

## Transcript
[00:00] Pierwszy czytelny akapit...

[01:32] Kolejny akapit...
```

## Quality Gates
- Transkrypt ma być czytelny, a nie zapisany linia po linii jak surowe captiony.
- Łącz krótkie fragmenty w sensowne akapity.
- Zachowuj timestamp na poziomie akapitu, nie na każdej linijce.
- Zachowuj metadane pliku: tytuł, URL, video ID i orientacyjny czas trwania.

## Edge Cases
- Jeśli film nie ma dostępnego transkryptu, zakończ workflow błędem i pokaż jasny komunikat.
- Jeśli nie da się pobrać tytułu filmu, użyj `video_id`.
- Jeśli tytuł jest zbyt długi dla nazwy pliku, skróć go jak dotychczas, ale zachowaj pełny tytuł w treści dokumentu.

## Separation Rule
Tworzenie notatek do wideo jest od teraz osobnym workflow i nie należy do tej dyrektywy.

## Pipeline Relationship
- Upstream: none
- Downstream:
  - `workflows/youtube-notes/notes.directive.md`
  - `workflows/youtube-notes/enrichment.directive.md` (through `workflows/youtube-notes/pipeline.directive.md`)

If this directive is called as part of a larger chain, it should return the transcript path for the next workflow instead of treating transcript creation as the final user-visible stop.
