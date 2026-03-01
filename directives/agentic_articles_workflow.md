# Directive: Agentic Articles Workflow v3.0

## Goal
Create high-quality SEO articles (PL local market) with a repeatable process that balances search intent, factual quality, and business outcomes.

## Inputs
- Completed article brief (`article_brief.md`)
- Topic and business context
- Optional local context (city/region)
- Selected company (`company`, natural language)

## Primary Documentation
- `Agentic Articles/docs/article_workflow_research_2026.md`
- `Agentic Articles/docs/seo_copywriting_workflow_v1.md`
- `Agentic Articles/docs/article_brief_template.md`
- `Agentic Articles/docs/article_qa_checklist.md`
- `Agentic Articles/docs/company_context_profiles.md`

## Execution Scripts
- `execution/article_workflow_init.py`
- `execution/research_fetch.py`
- `execution/check_research_quality.py`
- `execution/article_workflow_validate.py`
- `execution/check_polish_language.py`
- `execution/check_polish_naturalness.py`
- `execution/check_polish_fluency_ml.py`
- `execution/check_humanization.py`
- `execution/check_workflow_context.py`
- `execution/export_to_gdocs.py`

## Process (Artifact-driven)
1. Fill brief
2. Run automated external research fetch (`research_fetch.py`)
3. Run research hard gate (`check_research_quality.py`)
4. Confirm required skills are loaded/applied in run context
5. Write draft v1
6. Run Polish language auto-fix + grammar/diacritics gate
7. Run Polish naturalness gate (title/collocations/punctuation/structure/rewrite)
8. Run pre-trained ML fluency signal
9. Run humanization + copy-editing gate
10. Run workflow context gate
11. Iterate: validate -> apply fixes -> revalidate (max 5 iterations)
12. Mark package as ready for manual review
13. Export QA-approved article to Google Docs

## Required Outputs (per article)
- `article_brief.md`
- `article_research_pack.md`
- `research_evidence_manifest.json`
- `quality_gate.json`
- `article_draft_v1.md`
- `qa_report.md`
- `article_draft_v2.md`
- `publish_ready.md`
- `qa_iteration_feedback.md` (only if validation fails)

## Quality Gate (Hard Block)
- Source of truth for pass/fail is `quality_gate.json` (not checkboxes in `qa_report.md`)
- `polish_title_naturalness_pass`, `polish_collocation_pass`, `polish_punctuation_pass`, `polish_diacritics_pass`, `polish_grammar_pass`, `polish_fluency_ml_pass`, `structure_variance_pass_v2`, `semantic_rewrite_pass_v2` must be `PASS`
- `skills_policy_pass` and `evidence_provenance_pass` must be `PASS`
- `keyword_metrics_coverage_pass`, `serp_dataset_quality_pass`, `trends_dataset_quality_pass`, `competitor_matrix_pass`, `research_data_freshness_pass`, `research_hard_block_pass` must be `PASS`
- `skills_policy_pass` requires both:
  - required skills listed in `run_context.md` (`skills_loaded`, `skills_applied`)
  - local installs present in `./skills/<skill>/SKILL.md`
- `forbidden_phrase_pass`, `specificity_pass`, `voice_authenticity_pass`, `rewrite_loop_pass` must be `PASS`
- `hard_block_export_pass` must be `PASS`
- `detector_ensemble_pass` is advisory only (warning, not sole blocker)
- `publish_ready.md` status must be `Ready_for_manual_review` or `Approved`
- Service links and CTA must match the selected company profile
- Exported Google Doc must be rich-text ready (headings/lists/links), not raw Markdown
- Polish grammar gate is evaluated on prose-only extraction (not raw Markdown structure) to avoid false positives from headings/lists.
- Proper nouns from company/domain context (e.g. `Kobido`, `Studio Balans`, `EMS`, `Niepołomice`) are protected in spell-check filtering.

## Edge Cases
1. Low-data niche topic: use intent + PAA + entity-first fallback.
2. High-risk topic (health/finance/legal): force stricter source validation and extra human review.
3. Local intent ambiguity: pause and clarify geographic scope before blueprint.
4. Ambiguous company alias: stop and resolve company before drafting.
5. Missing OAuth credentials: block export and return setup error.

## Notes
- In v3.0, workflow still ends at Google Docs export.
- Data mode in this stage is `external_only` (SERP/Trends/Keyword Planner/competitor data).
- Premium SEO APIs are optional and can be introduced after pilot validation.
- Keep local markdown as source of truth, then export final article to Google Docs.
- Manual review by owner happens after export, directly in Google Docs.

## Usage
```bash
# 1) Initialize workspace for one article
python3 execution/article_workflow_init.py \
  --topic "Zalety treningu EMS w Niepolomicach" \
  --company "studio balans"

# 2) Fill artifacts manually/agentically in workspace
# Agentic Articles/workspace/YYYY-MM-DD_topic-slug/

# 3) Run data-driven research fetch and research quality gates
python3 execution/research_fetch.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

python3 execution/check_research_quality.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

# 4) Run language/naturalness/ML/humanization/context checks
python3 execution/check_polish_language.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug" \
  --apply

python3 execution/check_polish_naturalness.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

python3 execution/check_polish_fluency_ml.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

python3 execution/check_humanization.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

python3 execution/check_workflow_context.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

# 5) Validate final gates before export
python3 execution/article_workflow_validate.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug" \
  --mode pre_export

# 6) If validation fails, fix article + manifests and rerun checks
# export_to_gdocs.py writes qa_iteration_feedback.md automatically on failure

# 7) Export final draft to Google Docs
python3 execution/export_to_gdocs.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

# Po eksporcie dostaniesz komunikat:
# ARTYKUL GOTOWY: <google_docs_url>
```
