# Directive: Content Planning Workflow A (bi-weekly, data-first)

## Goal
Create a repeatable, data-driven content backlog every 2 weeks for multiple companies, using free/manual research exports.

## Scope
- In: keyword/trend/SERP/PAA ingestion, topic clustering, prioritization, strict planning gate, run queue output.
- Out: article drafting, CMS publishing, post-publish analytics gates.

## Inputs
- `planning_brief.md`
- Manual exports in `research_inputs/`:
  - `keyword*.csv`
  - `serp*.csv`
  - `paa*.csv`
  - `trend*.csv`

## Outputs
- `planning_dataset.json`
- `content_plan_candidates.csv`
- `content_plan_backlog.csv`
- `planning_gate.json`
- `content_plan_report.md`
- `run_queue.csv`

## Hard Gate Policy
`planning_hard_block_pass` must be `PASS` before publishing queue.

Gate thresholds:
- `keyword_dataset_pass`: >= 60 keywords with volume per company
- `serp_dataset_pass`: >= 30 SERP rows per company and >= 8 unique domains
- `paa_dataset_pass`: >= 10 PAA questions per company
- `trends_dataset_pass`: >= 5 trend queries per company
- `cluster_quality_pass`: approved topics must have primary + >=8 secondary + intent + target_service_url + cta_type
- `backlog_minimum_pass`: >= 4 approved topics per company

## Process
1. Initialize sprint
2. Place raw exports in `research_inputs/`
3. Ingest and normalize data
4. Build topic clusters + scoring
5. Run planning gate
6. Publish approved topics to run queue
7. Start Workflow B only from queue rows marked `workflow_b_ready=yes`

## Commands
```bash
# FAST TRACK (recommended for non-SEO users)
# Provide keyword CSV export(s), optional extra CSVs; script auto-fetches SERP/PAA/Trends.
python3 execution/content_planning_autopilot.py \
  --company "studio balans" \
  --keyword-files "/absolute/path/keywords_export_1.csv" "/absolute/path/keywords_export_2.csv" \
  --extra-files "/absolute/path/optional_serp.csv" "/absolute/path/optional_trends.csv"

# 1) Init sprint
python3 execution/content_planning_init.py \
  --sprint-date 2026-03-15 \
  --companies "studio balans,druga firma"

# 2) Copy manual exports to:
# Agentic Articles/planning/2026-03-15_sprint/research_inputs/

# 3) Ingest
python3 execution/content_planning_ingest.py \
  --sprint "Agentic Articles/planning/2026-03-15_sprint"

# 4) Cluster + score
python3 execution/content_planning_cluster.py \
  --sprint "Agentic Articles/planning/2026-03-15_sprint"

# 5) Evaluate strict gate
python3 execution/content_planning_gate.py \
  --sprint "Agentic Articles/planning/2026-03-15_sprint"

# 6) Publish queue (only if planning_hard_block_pass=PASS)
python3 execution/content_planning_to_queue.py \
  --sprint "Agentic Articles/planning/2026-03-15_sprint"

# 7) Start Workflow B from approved queue row
python3 execution/prepare_article_from_queue.py \
  --queue-row-id "rq-0001"
```

## Edge Cases
1. Missing Trends files -> gate FAIL.
2. SERP without domains -> likely gate FAIL on domain diversity.
3. Approved topic missing service URL/CTA -> cluster quality FAIL.
4. Queue row not ready -> article initialization blocked.

## Notes
- This workflow is free-first and manual-source friendly.
- Google Sheet remains operational source-of-truth; CSV outputs are compatible with sheet import.
- Workflow B export to Google Docs remains unchanged, but now requires approved planning reference.
- For non-SEO users, use `content_planning_autopilot.py` with keyword CSV exports as the default entrypoint.
