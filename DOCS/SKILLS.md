# Agent Skills & Capabilities

This document lists the active workflows and project-local capabilities in this repo.

## How to Use This File

When a user request matches any workflow below, the agent should:

1. Route to the corresponding workflow directive in `workflows/`
2. Use the colocated scripts in that workflow's `scripts/` directory
3. Write generated artifacts to `runtime/`
4. Report final artifact paths back to the user

## Active Workflows

### Agentic Articles
**Trigger phrases**: "article workflow", "seo article workflow", "agentic articles", "content pipeline", "blog workflow"

**What it does**: Runs the article production workflow for researched SEO/service-page content, including QA and Google Docs export.

**Workflow**: `workflows/agentic-articles/directive.md`

**Docs**:
- `workflows/agentic-articles/docs/article_workflow_research_2026.md`
- `workflows/agentic-articles/docs/seo_copywriting_workflow_v1.md`
- `workflows/agentic-articles/docs/article_brief_template.md`
- `workflows/agentic-articles/docs/service_page_brief_template.md`
- `workflows/agentic-articles/docs/company_context_profiles.md`

**Runtime output**:
- `runtime/agentic-articles/workspace/`
- `runtime/agentic-articles/deliverables/`

### Content Planning
**Trigger phrases**: "content planning", "planning sprint", "topic clustering", "run queue", "content backlog"

**What it does**: Creates planning sprints, ingests keyword/SERP/PAA/trends data, clusters topics, gates the backlog, and prepares items for the article workflow.

**Workflow**: `workflows/content-planning/directive.md`

**Docs**:
- `workflows/content-planning/docs/content_planning_sop_v1.md`
- `workflows/content-planning/docs/content_plan_sheet_schema.md`

**Runtime output**:
- `runtime/agentic-articles/planning/`

### Convert for AI
**Trigger phrases**: "convert pptx for ai", "convert files for ai", "NotebookLM-ready pdf", "pptx to ai pdf"

**What it does**: Converts PPTX input into AI-friendly PDF output with slide renders, extracted text, and optional AI-enriched descriptions.

**Workflow**: `workflows/convert-for-ai/directive.md`

**Runtime output**:
- `runtime/convert-for-ai/input/`
- `runtime/convert-for-ai/output/`
- `runtime/tmp/convert-for-ai/`

### Media Optimization
**Trigger phrases**: "optimize media", "optimize images", "optimize videos", "web media optimization"

**What it does**: Optimizes image and video assets for web delivery.

**Workflow**: `workflows/media-optimization/directive.md`

**Docs**:
- `workflows/media-optimization/docs/README.md`

**Runtime output**:
- `runtime/media-optimization/input/`
- `runtime/media-optimization/output/`

### YouTube Notes Pipeline
**Trigger phrases**: "zrób notatki z filmiku", "youtube notes", "transcript notes enrichment", "zrób transkrypt i notatki", "ulepsz notatki z youtube", "enrichment notatek"

**What it does**: Chains YouTube note workflows into one pipeline:
- `video -> transcript`
- `transcript -> base notes`
- `base notes + transcript -> enriched notes`

The enrichment stage is agent-run and uses lightweight multi-agent orchestration rather than a rigid deterministic script.

**Parent workflow**:
- `workflows/youtube-notes/pipeline.directive.md`

**Stages**:
- `workflows/youtube-notes/transcript.directive.md`
- `workflows/youtube-notes/notes.directive.md`
- `workflows/youtube-notes/enrichment.directive.md`

**Runtime output**:
- `runtime/youtube-notes/`

## Project-Local Skills

Most skills are available globally in Codex and are not duplicated in this repo.

The one project-local skill currently kept in-repo is:

### FigJam Workflow Diagramming
**Skill path**: `skills-local/figjam-workflow-diagramming/SKILL.md`

**What it does**: Provides project-specific workflow diagramming rules, references, and agent config for FigJam diagrams.

**Bundled references**:
- `skills-local/figjam-workflow-diagramming/references/style-system.md`
- `skills-local/figjam-workflow-diagramming/references/content-patterns.md`
- `skills-local/figjam-workflow-diagramming/references/diagram-templates.md`
- `skills-local/figjam-workflow-diagramming/references/qa-rubric.md`
- `skills-local/figjam-workflow-diagramming/references/anti-patterns.md`
- `skills-local/figjam-workflow-diagramming/references/process-mapping-best-practices.md`
