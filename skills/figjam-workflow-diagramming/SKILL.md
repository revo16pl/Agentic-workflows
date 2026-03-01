---
name: figjam-workflow-diagramming
description: Create documentation-grade FigJam workflow diagrams using Figma MCP. Use for workflow diagrams, process maps, SOP diagrams, pipeline maps, and onboarding process documentation in Polish or English. Trigger for requests like "zrob diagram workflow", "opisz proces na FigJam", "workflow diagram", "process map", and "SOP flow".
---

# FigJam Workflow Diagramming

## Overview
Use this skill to produce workflow diagrams that work as real process documentation, not just visual summaries.
Default style: left-to-right flow, section-per-step, substeps inside sections, file explanations in the same step context, explicit decision logic, and operationally grounded descriptions.

This skill prioritizes:
1. process understanding before drawing,
2. documentation quality over brevity,
3. source-grounded wording over guessed or generic wording.

## Non-Negotiable Preparation (Before Diagram)
Do this before generating any final diagram.

1. Read source materials for the target workflow (directive, execution scripts, sample artifacts).
2. Build a mapping of: step -> action -> tools/APIs/frameworks -> outputs -> transition condition -> blockers.
3. For each mentioned file, identify what it contains and why it exists in that step.
4. If a detail is unknown, mark it as unknown and avoid inventing facts.

Do not jump directly to Mermaid from user phrasing only.

## Core Default Rules
Apply these unless the user explicitly overrides.

1. Keep global process direction left-to-right.
2. Represent each major step as a separate section.
3. Use substeps inside each section (for example 1.1, 1.2, 1.3).
4. Keep file descriptions in the same section where the file is created or used.
5. Do not create a separate file-map area unless explicitly requested.
6. Keep color palette semantic and minimal (max 5 classes).
7. Include legend and explicit PASS/FAIL logic.
8. Avoid HTML tags in Mermaid labels.
9. Keep wording readable at normal zoom.
10. Use full sentences for key explanations; avoid single-word stubs.
11. Use proper Polish diacritics in Polish output (`ą ę ł ń ó ś ż ź`).

## FigJam Text Formatting Policy (Mermaid Constraints)
Use formatting methods that are reliable in FigJam diagram generation.

1. Preferred structure markers:
- line breaks (`\\n`) for spacing,
- section headers in uppercase (`ACTION`, `ARTEFAKTY`, `CONTROL`),
- bullet points with `•`,
- numbered mini-lists (`1)`, `2)`, `3)`) when needed.
2. Do not rely on Markdown bold/italic in node labels.
3. Do not use HTML tags (`<b>`, `<code>`, `<i>`) in labels.
4. Simulate emphasis via heading lines and short, high-signal sentences.

## Documentation Quality Mode (Default)
Each operational step must be understandable by a non-technical reader without verbal explanation.

For every step section, include:
1. What this step is.
2. What is happening right now.
3. Why this step exists.
4. Which tools/APIs/frameworks are actually used.
5. What output is produced (file, status, URL, state change).
6. Transition condition to next step.
7. What blocks transition.

If the step creates multiple files, each file gets a one-sentence purpose line.

## Section Blueprint (Recommended)
Use this internal layout for each step section.

1. Action card
- narrative description of the step in complete sentences.
2. Artifact card
- list of files created/updated in this step,
- one sentence per file: what it contains and why it exists.
3. Control card
- transition condition,
- blockers,
- quality gate links (if applicable).

This pattern is preferred over short keyword-only cards.

## Output Contract
Final diagram must satisfy all items:

1. START -> steps -> decisions -> FAIL loop -> PASS -> END structure is explicit.
2. Edges are directionally coherent with LR flow.
3. Each step includes:
- Co to jest
- Co dzieje sie w tym momencie
- Po co
- Narzedzia/API/frameworky
- Output z narzedzi/API
- Warunek przejscia
- Co blokuje przejscie
4. File entries are contextual and explained (one sentence per file when listed).
5. If no external API is used, write explicitly: `API: brak (operacja lokalna)`.
6. Language defaults to Polish, concrete and documentation-oriented.

## Diagram Creation Workflow
Follow this sequence.

1. Determine audience and objective.
2. Analyze source workflow documents and scripts.
3. Build step mapping (action/tool/output/gate/blocker).
4. Draft structure-only skeleton.
5. Expand sections with action/artifact/control cards.
6. Add PASS/FAIL and iteration loop.
7. Add legend and thresholds.
8. Run rubric checks from `references/qa-rubric.md`.
9. Revise for readability and factual alignment.

## Required Tools and Formatting
Use Figma MCP `generate_diagram`.
Use Mermaid flowchart with LR global direction.
Use class-based semantic styling.

Name tools explicitly where relevant:
1. script filenames,
2. API names,
3. key frameworks/libraries only when they materially affect the step.

## If Diagram Is Too Dense
Reduce density without losing meaning.

1. Split one overloaded step into more substeps.
2. Keep action/artifact/control split.
3. Keep file one-sentence purpose lines.
4. Keep PASS/FAIL and transition logic unchanged.
5. Remove decorative text before removing factual content.

## Hard Constraints
Do not violate these unless user explicitly requests an exception.

1. No mixed global flow directions.
2. No detached file references by default.
3. No unlabeled decision branches.
4. No HTML tags in labels.
5. No guessed details about files, APIs, or outputs.
6. No telegraphic "keyword-only" explanation for documentation steps.
7. No direct copy of user draft text without documentation-quality rewrite.
8. No ASCII-only Polish text when Polish output is requested.

## References
Load only what is needed.

1. Visual system: `references/style-system.md`
2. Writing patterns: `references/content-patterns.md`
3. Templates: `references/diagram-templates.md`
4. QA rubric: `references/qa-rubric.md`
5. Anti-patterns: `references/anti-patterns.md`
6. Process documentation best practices: `references/process-mapping-best-practices.md`

## Quick Start Prompt Pattern
"Stworz diagram workflow w FigJam przez MCP. Najpierw przeanalizuj workflow i zmapuj krok po kroku action/tool/output/gate/blocker. Potem zbuduj LR diagram z sekcjami per krok i podkrokami. W kazdym kroku opisz co sie dzieje, po co, jakie narzedzia/API/frameworki sa uzyte, jaki output powstaje, oraz warunek przejscia i blokery. Opisy plikow trzymaj w kontekscie kroku i daj jednozdaniowy opis celu kazdego pliku."
