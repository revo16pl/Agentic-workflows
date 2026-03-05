# Directive: Agentic Articles Workflow v3.1

## Goal
Create high-quality SEO content packages (PL local market) with a repeatable process that balances search intent, factual quality, and business outcomes.

## Inputs
- `article` profile: approved queue row from Workflow A (`run_queue.csv` with `workflow_b_ready=yes`)
- `service_page` profile: service URL (`--url`) + company (`--company`) in natural language
- Completed brief (`article_brief.md`)
- Topic and business context
- Optional local context (city/region)

## Primary Documentation
- `Agentic Articles/docs/article_workflow_research_2026.md`
- `Agentic Articles/docs/seo_copywriting_workflow_v1.md`
- `Agentic Articles/docs/content_planning_sop_v1.md`
- `Agentic Articles/docs/article_brief_template.md`
- `Agentic Articles/docs/service_page_brief_template.md`
- `Agentic Articles/docs/company_context_profiles.md`

## Execution Scripts
- `execution/article_workflow_init.py`
- `execution/prepare_article_from_queue.py`
- `execution/prepare_service_page_from_url.py`
- `execution/company_profile_resolver.py`
- `execution/extract_service_page_context.py`
- `execution/research_fetch.py`
- `execution/check_research_quality.py`
- `execution/article_workflow_validate.py`
- `execution/check_polish_language.py`
- `execution/check_polish_naturalness.py`
- `execution/check_polish_fluency_ml.py`
- `execution/check_humanization.py`
- `execution/check_workflow_context.py`
- `execution/export_to_gdocs.py`

## Content Profiles
- `article` (default): long-form SEO article workflow.
- `service_page`: short service subpage package with three sections:
  - `Subheading` (length similar to source page lead),
  - `Opis` (short, educational, intent-aware rich text),
  - `Najważniejsze informacje` (short content per inherited tab labels).
- `service_page` is URL-first and does not require `RUN_QUEUE` planning linkage.
- Both profiles require an agent-led editorial review loop captured in `editorial_review.md`.

## Process (Artifact-driven)
1. Start from approved queue row (Workflow A) using `prepare_article_from_queue.py`
2. Fill/refine brief
3. Run automated external research fetch (`research_fetch.py`)
4. Run research hard gate (`check_research_quality.py`)
5. Confirm required skills are loaded/applied in run context
6. Write the working draft (manual, na bazie `service_page_writer_packet.md` dla `service_page`)
7. Run editorial QA loop (logic -> content-strategy -> copywriting -> copy-editing) and document it in `editorial_review.md`
8. Run Polish language auto-fix + grammar/diacritics gate
9. Run Polish naturalness gate (title/collocations/punctuation/structure/rewrite)
10. Run pre-trained ML fluency signal
11. Run humanization + copy-editing gate
12. Agent applies fixes from machine QA and runs a short post-machine editorial pass; update `editorial_review.md`
13. Run workflow context gate
14. Iterate: validate -> apply fixes -> revalidate (max 5 iterations)
15. Export QA-approved draft to Google Docs

## Required Outputs (per article)
- `article_brief.md`
- `article_research_pack.md`
- `research_evidence_manifest.json`
- `quality_gate.json`
- `article_draft_v2.md`
- `editorial_review.md`
- `qa_iteration_feedback.md` (temp only if validation fails)
- `service_page_writer_packet.md` (service_page only)
- `company_profile_snapshot.json` (service_page only)
- after successful export cleanup leaves only:
  - `article_research_pack.md`
  - `final_output.md`

## Quality Gate (Hard Block)
- Source of truth for pass/fail is `quality_gate.json` plus approved `editorial_review.md`
- `polish_title_naturalness_pass`, `polish_collocation_pass`, `polish_punctuation_pass`, `polish_diacritics_pass`, `polish_grammar_pass`, `polish_fluency_ml_pass`, `structure_variance_pass_v2`, `semantic_rewrite_pass_v2` must be `PASS`
- `skills_policy_pass` and `evidence_provenance_pass` must be `PASS`
- `keyword_metrics_coverage_pass`, `serp_dataset_quality_pass`, `trends_dataset_quality_pass`, `competitor_matrix_pass`, `research_data_freshness_pass`, `research_hard_block_pass` must be `PASS`
- `skills_policy_pass` requires both:
  - required skills listed in `run_context.md` (`skills_loaded`, `skills_applied`)
  - local installs present in `./skills/<skill>/SKILL.md`
- `forbidden_phrase_pass`, `specificity_pass`, `voice_authenticity_pass`, `rewrite_loop_pass` must be `PASS`
- `topic_from_approved_plan_pass` must be `PASS` for `article` profile
- `service_page` profile bypasses queue linkage and instead requires `source_url` in `run_context.md`
- `service_page` profile requires `company_profile_snapshot.json` and `brand_voice_loaded: yes` in `run_context.md`
- `service_page` profile requires `editorial_review.md` with:
  - minimum 2 iteracje,
  - `logic_pass: PASS`,
  - `final_decision: approved`
- `hard_block_export_pass` must be `PASS`
- `detector_ensemble_pass` is advisory only (warning, not sole blocker)
- `editorial_review.md` must include:
  - minimum 2 iteracje,
  - `logic_pass: PASS`,
  - `post_machine_qa_revision_completed: yes`,
  - `final_decision: approved`
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
# ARTICLE PROFILE
# 1) Initialize workspace from approved queue row (Workflow A)
python3 execution/prepare_article_from_queue.py \
  --queue-row-id "rq-0001"

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
  --mode pre_export \
  --content-profile article

# 6) If validation fails, fix article + manifests and rerun checks
# export_to_gdocs.py writes qa_iteration_feedback.md automatically on failure

# 7) Export final draft to Google Docs
python3 execution/export_to_gdocs.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug" \
  --content-profile article \
  --export-mode prod

# Po eksporcie dostaniesz komunikat:
# DOKUMENT GOTOWY: <google_docs_url>

# ----------------------------------------------------------
# SERVICE_PAGE PROFILE (URL-first)
# 1) Bootstrap workspace from URL + auto analysis
python3 execution/prepare_service_page_from_url.py \
  --url "https://studio-balans-staging.pages.dev/zabiegi/masaz-goracymi-kamieniami" \
  --company "studio balans"

# 2) Run lightweight external research + gates
python3 execution/research_fetch.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug" \
  --content-profile service_page

python3 execution/check_research_quality.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug"

# 3) Run quality checks
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

# 4) Uzupełnij editorial_review.md po min. 2 iteracjach logiczno-redakcyjnych
# kolejność perspektyw: content-strategy -> copywriting -> copy-editing
# po machine QA zrób jeszcze krótki pass i ustaw `post_machine_qa_revision_completed: yes`
# agent zwraca link do Google Docs bez tworzenia osobnego pliku z URL

# 5) Validate + export
python3 execution/article_workflow_validate.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug" \
  --mode pre_export \
  --content-profile service_page

python3 execution/export_to_gdocs.py \
  --workspace "Agentic Articles/workspace/YYYY-MM-DD_topic-slug" \
  --content-profile service_page \
  --export-mode prod

# Debug only (NOT_FOR_PUBLISH): allows --skip-* flags
# python3 execution/export_to_gdocs.py ... --export-mode debug --skip-validation
```
