# humanization_report.md

- overall: PASS

## Gates
- forbidden_phrase_pass: PASS
- structure_variance_pass: PASS
- specificity_pass: PASS
- voice_authenticity_pass: PASS
- rewrite_loop_pass: PASS
- detector_ensemble_pass: PASS

## Style metrics
- words: 1563
- sentence_cv: 0.6352074795024718
- sentence_uniform_share: 0.22522522522522523
- sentence_opening_repeat_share: 0.12612612612612611
- sentence_opening_max_run: 2
- paragraph_cv: 0.6581638315694556
- short_paragraph_share: 0.46808510638297873
- paragraph_opening_repeat_share: 0.06382978723404253
- forbidden_hits: {}
- filler_density_per_1000: 0.0
- jargon_density_per_1000: 0.0
- nominalization_density_per_1000: 1.2795905310300704
- triad_density_per_1000: 1.9193857965451055
- generic_lead_hits: 0
- digits_count: 40
- numeric_context_count: 7
- example_markers: 3
- links_count: 3
- question_marks: 7
- local_hits: 4
- service_hits: 20
- second_person_hits: 21
- specificity_points: 6

## Detector ensemble
- detectors_run: 3
- mean_ai_risk: 0.006
- max_single_ai_risk: 0.008
- max_ai_prob: 0.580
- max_single_ai_prob: 0.700
- model openai-community/roberta-base-openai-detector: avg_ai_risk=0.008, pass=PASS
- model Hello-SimpleAI/chatgpt-detector-roberta: avg_ai_risk=0.000, pass=PASS
- model nbroad/openai-detector-base: avg_ai_risk=0.008, pass=PASS
