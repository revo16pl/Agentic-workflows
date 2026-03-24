# Directive: YouTube Notes Pipeline (v1)

**Goal**: Skleić trzy osobne workflowy w jeden logiczny pipeline, tak aby agent wiedział, w jakiej kolejności uruchamiać etapy `transcript`, `notes` i `enrichment` na podstawie intencji użytkownika.

## Supported Stages
1. `workflows/youtube-notes/transcript.directive.md`
2. `workflows/youtube-notes/notes.directive.md`
3. `workflows/youtube-notes/enrichment.directive.md`

## Inputs
- `video_url` (optional)
- `transcript_path` (optional)
- `notes_path` (optional)
- `requested_depth` (derived from user intent): `transcript | notes | enrichment | full`

## Outputs
- zależnie od zakresu:
  - `Transcript - ...md`
  - `Notes - ...md`
  - `Enriched Notes - ...md`

## Pipeline Rules

### Rule 1: If the user provides a video URL and asks only for a transcript
Run:
1. `workflows/youtube-notes/transcript.directive.md`

Return:
- ścieżka do pliku transkryptu

### Rule 2: If the user provides a video URL and asks for notes
Run:
1. `workflows/youtube-notes/transcript.directive.md`
2. `workflows/youtube-notes/notes.directive.md`

Return:
- ścieżka do transkryptu
- ścieżka do bazowych notatek

### Rule 3: If the user provides a video URL and asks for notes plus enrichment
Run:
1. `workflows/youtube-notes/transcript.directive.md`
2. `workflows/youtube-notes/notes.directive.md`
3. `workflows/youtube-notes/enrichment.directive.md`

Return:
- ścieżka do transkryptu
- ścieżka do bazowych notatek
- ścieżka do enriched notes

### Rule 4: If the user provides a transcript path and asks for notes
Skip transcript generation.
Run:
1. `workflows/youtube-notes/notes.directive.md`

### Rule 5: If the user provides a transcript path and asks for notes plus enrichment
Skip transcript generation.
Run:
1. `workflows/youtube-notes/notes.directive.md`
2. `workflows/youtube-notes/enrichment.directive.md`

### Rule 6: If the user provides a notes path and asks for enrichment
Skip transcript and base notes generation.
Run:
1. `workflows/youtube-notes/enrichment.directive.md`

## Enrichment Mode
The enrichment stage should be treated as an agent-run editorial pass, not as a deterministic script step.

When enrichment is requested:
- the main agent acts as orchestrator,
- the enrichment stage should use a lightweight multi-agent setup,
- the final merge and final file write stay with the main agent.

## Intent Mapping
Interpret requests like this:

- `zrób transkrypt` -> `requested_depth=transcript`
- `zrób notatki` -> `requested_depth=notes`
- `zrób notatki i enrichment` -> `requested_depth=full`
- `ulepsz notatki`, `dopieszczone notatki`, `enrichment notatek` -> `requested_depth=enrichment`

If user says:
- `wysyłam link do filmiku`
- `zrób mi notatki`
- `zrób enrichment notatek`

agent should assume the full chain:
1. transcript
2. base notes
3. enriched notes

## Skip Logic
- Never regenerate an upstream artifact if the downstream input already exists and the user provided it explicitly.
- If a parent pipeline request requires downstream stages, do not stop after creating an upstream artifact.
- Always pass resulting paths forward to the next stage.

## Naming Convention
- Transcript: `Transcript - [Truncated Title].md`
- Base notes: `Notes - [Truncated Title].md`
- Enriched notes: `Enriched Notes - [Truncated Title].md`

All files should live together in the same video directory unless the user explicitly asks otherwise.

## Agent Behavior
When the user request is compound, the agent should think in pipeline order, not tool order.

This means:
- first create missing upstream artifacts,
- then create requested downstream artifacts,
- if enrichment is requested, run it as a lightweight multi-agent editorial pass,
- then report all produced paths together.

## Relationship To Other Workflows
This directive is the parent orchestration layer for:
- `workflows/youtube-notes/transcript.directive.md`
- `workflows/youtube-notes/notes.directive.md`
- `workflows/youtube-notes/enrichment.directive.md`
