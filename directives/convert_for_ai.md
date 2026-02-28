# Directive: Convert Files for AI

## Cel
Konwertuj pliki PPTX na PDF gotowy dla AI agentów:
- **PDF** — screenshoty slajdów + AI opis wizualny + AI-ustrukturyzowana treść (jeden plik, NotebookLM-ready)

## Wymagania (jednorazowo)
```bash
pip3 install python-pptx reportlab spire.presentation Pillow
```

## Flow — JEDEN PROMPT, resztą zajmuje się Claude

Użytkownik wrzuca plik do `file_converter/Input/` i daje jeden prompt.
Claude wykonuje CAŁY pipeline automatycznie:

```
1. python3 execution/convert_for_ai.py
   → rendery PNG (Spire.Presentation, pełny layout)
   → extracted.json (surowy tekst per slajd)

2. Claude czyta każdy PNG + extracted.json
   → opisuje co widzi na każdym slajdzie (diagramy, układ, relacje)
   → strukturyzuje treść slajdu w oparciu o wizualny kontekst (nagłówki, bullet points, milestone'y)
   → zapisuje .tmp/{stem}/descriptions.json

3. python3 execution/build_document.py ".tmp/{stem}"
   → PDF w file_converter/output/
```

Użytkownik nie robi nic między krokami. Claude orchestruje cały flow w jednej odpowiedzi.

## Output

```
file_converter/output/
  {stem}.pdf       ← screenshot + AI opis + AI-ustrukturyzowana treść (NotebookLM, Claude, GPT-4V)
.tmp/{stem}/       ← pliki pośrednie (można usunąć po konwersji)
  slides/
    slide_01.png, slide_02.png ...
  extracted.json
  descriptions.json
```

## Format descriptions.json (Step 2 — Claude pisze)

```json
[
  {
    "slide": 1,
    "description": "Opis wizualny slajdu — co widać, układ, diagramy, kolory, relacje.",
    "structured_text": "Treść slajdu sformatowana na podstawie wizualnego kontekstu."
  }
]
```

### Zasady structured_text

Claude strukturyzuje treść **na podstawie PNG slajdu + extracted.json**:

```
## Nagłówek sekcji / fazy    ← linie zaczynające się od "## "
• Bullet point               ← linie zaczynające się od "• "
→ Milestone / key outcome    ← linie zaczynające się od "→ "
Zwykły tekst                 ← pozostałe linie
```

**Reguły:**
- Jeśli slajd to timeline/roadmap → struktura per faza: `## Phase N: Tytuł  |  daty`, bullets z deliverables, `→ Milestone`
- Jeśli slajd to lista → bullet points `• `
- Jeśli slajd tytułowy → czysty tekst (tytuł, podtytuł, data)
- Puste slajdy (tylko logo) → `structured_text: ""`
- Milestones (ostatnia pozycja w fazie, np. "Sign-off", "Completed", "Milestone") → `→ `

## Struktura PDF (per strona = jeden slajd)

```
Slide N: Tytuł
─────────────────────────
[Screenshot slajdu]

Opis wizualny
[Claude's opis wizualny]

Treść slajdu
## Phase 1: Tytuł  |  daty
• deliverable 1
• deliverable 2
→ Milestone
...
```

## Edge Cases

- Puste slajdy (brak tytułu, tekstu i opisu) są pomijane w output
- Slajd bez tekstu ale z opisem wizualnym → tylko sekcja "Opis wizualny"
- Jeśli `descriptions.json` nie istnieje → build_document.py działa dalej (bez opisów, raw text)
- Jeśli `structured_text` puste → fallback do raw texts z extracted.json
- XLSX: row 1 = nagłówki tabeli, max 500 wierszy per arkusz
- Watermark Spire.Presentation (drobny tekst w rogu) — nie wpływa na jakość AI analizy

## Używane narzędzia

- `execution/convert_for_ai.py` — Krok 1
- `execution/build_document.py` — Krok 3
- Claude Code (Krok 2) — analiza wizualna + strukturyzacja treści slajdów
