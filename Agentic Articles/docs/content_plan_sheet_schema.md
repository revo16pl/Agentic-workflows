# Content Plan Sheet Schema (operacyjny)

Arkusz: `Content Plan - Agentic Articles`

## Zakladka: TOPIC_CLUSTERS
Wymagane kolumny:
- `company`
- `topic_cluster_name`
- `primary_keyword`
- `secondary_keywords`
- `avg_monthly_searches_sum`
- `intent`
- `trend_direction`
- `serp_competition_level`
- `content_gap_note`
- `demand_score`
- `intent_fit_score`
- `business_fit_score`
- `priority_score`
- `recommended_length_min`
- `recommended_length_max`
- `target_service_url`
- `cta_type`
- `status` (`candidate|approved|rejected|queued|in_progress|done`)

## Zakladka: RUN_QUEUE
Wymagane kolumny:
- `queue_row_id`
- `topic_id`
- `company`
- `topic_cluster_name`
- `article_title_working`
- `primary_keyword`
- `target_length_words`
- `intent`
- `target_service_url`
- `cta_type`
- `workflow_b_ready`
- `reason_if_no`
- `source_sprint`

## Scoring policy (default)
`priority_score = demand(35%) + intent_fit(25%) + business_fit(25%) + trend(15%) - competition_penalty`

## Status workflow
- `candidate`: temat po klasteryzacji, jeszcze niezatwierdzony
- `approved`: temat gotowy merytorycznie i biznesowo
- `queued`: temat wyslany do RUN_QUEUE
- `in_progress`: artykul jest tworzony w Workflow B
- `done`: artykul przeszedl Workflow B i trafil do Google Docs

## Minimalny approved topic
Temat moze miec status `approved` tylko jesli ma:
- primary keyword,
- min. 8 secondary keywords,
- intent,
- target_service_url,
- cta_type.
