# Agent Skills & Capabilities

This document lists specialized workflows and capabilities available to the agent orchestration system.

## Website Extraction

### Extract Framer Sites
**Trigger phrases**: "extract framer site", "download framer website", "export from framer"

**What it does**: Downloads a complete website (Framer or any site) including all pages and assets (images, CSS, JS, fonts, videos), and rewrites all references to work locally.

**Directive**: `directives/extract_framer_site.md`

**Example usage**:
- "Extract https://example.framer.website"
- "Download this site: mysite.framer.website with max 100 pages"

**Output**: `framer_extracts/<site-name>/` with all pages and assets

**Documentation**: [DOCS/FRAMER_EXTRACTION.md](FRAMER_EXTRACTION.md)

---

## How to Use This File

When a user request matches any of the trigger phrases or capabilities listed above, the agent should:

1. Reference the corresponding directive in `directives/`
2. Gather required inputs from the user
3. Execute the appropriate script from `execution/`
4. Report results using the documented output format

## Adding New Skills

When you create a new capability/workflow, update this file with:
- **Name** of the skill
- **Trigger phrases** users might say
- **Brief description** of what it does
- **Path to directive** and execution script
- **Example usage**
- **Documentation link** (if applicable)

---

## Content Workflow

### Agentic Articles Workflow v1
**Trigger phrases**: "article workflow", "seo article workflow", "agentic articles", "content pipeline", "blog workflow"

**What it does**: Defines a complete artifact-driven SOP for writing high-quality SEO articles (PL local market), from brief and intent mapping through QA and final export to Google Docs.

**Directive**: `directives/agentic_articles_workflow.md`

**Primary docs**:
- `Agentic Articles/docs/article_workflow_research_2026.md`
- `Agentic Articles/docs/seo_copywriting_workflow_v1.md`
- `Agentic Articles/docs/article_brief_template.md`
- `Agentic Articles/docs/article_qa_checklist.md`
- `Agentic Articles/docs/company_context_profiles.md`

**Output**: Per-article workspace with standardized artifacts (`article_brief.md`, `article_research_pack.md`, `research_evidence_manifest.json`, `quality_gate.json`, `qa_report.md`, etc.)

### Required External Skills (skills.sh / marketingskills)
Workflow v2.1 wymaga tych skilli na etapie pisania i QA:
- `content-strategy` (brief + angle + struktura intent)
- `copywriting` (outline + draft v1)
- `copy-editing` (sweeps jakościowe i humanizacja redakcyjna)
- `seo-audit` (on-page SEO checks)
- `schema-markup` (spójność schema z treścią)
- `ai-seo` (LLM/snippet readiness)

---

## Diagramming Workflow

### FigJam Workflow Diagramming
**Trigger phrases**: "workflow diagram", "process map", "SOP diagram", "pipeline diagram", "figjam workflow", "zrób diagram workflow", "opisz proces na figjamie", "mapowanie procesu"

**What it does**: Tworzy dokumentacyjne (SOP-grade) diagramy workflow w FigJam dla onboardingu i operacji. Domyślnie wymusza układ lewo->prawo, sekcje per krok, podkroki w sekcjach, opisy plików osadzone w tym samym kroku oraz czytelną logikę PASS/FAIL z legendą.
Każdy krok musi opisać: co się dzieje teraz, po co krok istnieje, jakie narzędzia/API/frameworky są użyte, jaki jest output, jaki jest warunek przejścia i co blokuje przejście.

**Skill path (project-local)**: `skills/figjam-workflow-diagramming/SKILL.md`

**Bundled references**:
- `skills/figjam-workflow-diagramming/references/style-system.md`
- `skills/figjam-workflow-diagramming/references/content-patterns.md`
- `skills/figjam-workflow-diagramming/references/diagram-templates.md`
- `skills/figjam-workflow-diagramming/references/qa-rubric.md`
- `skills/figjam-workflow-diagramming/references/anti-patterns.md`
- `skills/figjam-workflow-diagramming/references/process-mapping-best-practices.md`

**Example usage**:
- "Zrób diagram workflow onboardingu klienta na FigJam"
- "Create a process map for our release workflow in FigJam"
