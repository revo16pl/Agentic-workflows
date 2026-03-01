# Content Patterns for Documentation-Grade Workflow Tiles

Use these patterns when the diagram is meant to document process logic, onboarding flow, and operational details.

## 1. Step Section Pattern (Action + Artifacts + Control)
Each major process step should include three internal cards.

1. Action card
- `Co to jest`
- `Co dzieje sie w tym momencie`
- `Po co`
- `Narzedzia/API/frameworky`
- `Output z narzedzi/API`

2. Artifact card
- `Tworzone lub aktualizowane pliki`
- for each file: one sentence `co zawiera` + one sentence `po co istnieje`

3. Control card
- `Warunek przejscia dalej`
- `Co blokuje przejscie`
- optional: `Powiazane gate'y` or `Decyzja PASS/FAIL`

## 2. Narrative Depth Rules
Avoid keyword-only cards.

1. Use complete sentences for explanations.
2. Keep each sentence concrete and specific to the step.
3. Do not copy user wording literally if it is placeholder-level.
4. Rewrite to documentation quality while preserving intent.
5. Preserve Polish diacritics in final wording when language is Polish.

## 2b. Readable Emphasis Pattern (for FigJam Mermaid)
Since rich text styling is limited, use structural emphasis.

1. Start each internal card with uppercase header (`ACTION`, `ARTEFAKTY`, `CONTROL`).
2. Use bullets `•` for lists.
3. Use blank-line effect with `\\n` between conceptual blocks.
4. Keep each bullet to one idea and one sentence.
5. Keep lines short enough for normal zoom readability.

## 3. Tool/API/Framework Pattern
List real execution components, not generic buzzwords.

1. `Narzedzia lokalne:` script names or validators.
2. `API zewnetrzne:` exact API name when used.
3. `Framework/library:` only if it materially changes behavior.
4. If no external API is used, write explicitly: `API: brak (operacja lokalna)`.

## 4. Output Pattern
Every execution line must map to a concrete output.

1. File output (for example `qa_report.md`).
2. State output (for example gate status PASS/FAIL).
3. URL output (for example Google Docs link).
4. If output is intermediate, say who consumes it next.

## 5. File Description Pattern (One-Sentence Purpose)
When listing files in a step, use this format:

1. `<file_name>`: what the file contains.
2. `<file_name>`: why this file exists at this point in the flow.

Example:
- `quality_gate.json`: stores current gate statuses and hard gate list.
- `quality_gate.json`: acts as source of truth for export eligibility.

## 6. Gate Card Pattern
For quality/validation steps include:

1. Gate scope.
2. Checker script/tool.
3. Report output.
4. Required statuses.
5. Blocking condition.
6. Advisory condition (if any).

## 7. Decision Card Pattern
For branching logic include:

1. Binary decision question.
2. PASS path with destination.
3. FAIL path with recovery action.
4. Iteration limit (if applicable).

## 8. Compression Rules (When Dense)
If a section is too dense:

1. Split into additional substeps, not shorter meaning.
2. Preserve action/artifact/control structure.
3. Keep one-sentence file purposes.
4. Remove decorative language first.
5. Keep all decision and transition logic.

## 9. Example Step Section

```text
KROK 1: Setup Workspace

1.1 Action
Co to jest:
- Inicjalizacja nowego runu artykulu.
Co dzieje sie w tym momencie:
- Uruchamiany jest article_workflow_init.py, ktory tworzy dedykowany workspace i pliki bazowe.
Po co:
- Zabezpiecza jednolity punkt startu dla kolejnych etapow workflow.
Narzedzia/API/frameworky:
- Narzedzie: article_workflow_init.py
- API: brak (operacja lokalna)
- Framework/library: Python pathlib
Output z narzedzi/API:
- Folder workspace i komplet plikow startowych.

1.2 Artifacts
Tworzone pliki:
- article_brief.md: zawiera brief i wymagania tresciowe.
- article_brief.md: definiuje kierunek merytoryczny dalszego pisania.
- quality_gate.json: przechowuje statusy gate'ow.
- quality_gate.json: jest punktem decyzyjnym dla przejscia do exportu.

1.3 Control
Warunek przejscia dalej:
- komplet artefaktow istnieje i jest zapisany w workspace.
Co blokuje przejscie:
- brak wymaganego pliku lub niespojny kontekst run_context.md.
```
