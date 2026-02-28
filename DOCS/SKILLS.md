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
