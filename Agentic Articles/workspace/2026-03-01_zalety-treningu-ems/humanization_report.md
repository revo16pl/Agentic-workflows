# humanization_report.md

- overall: PASS

## Gates
- forbidden_phrase_pass: PASS
- structure_variance_pass: PASS
- specificity_pass: PASS
- voice_authenticity_pass: PASS
- detector_ensemble_pass: PASS
- rewrite_loop_pass: PASS

## Style metrics
- words: 1459
- sentence_cv: 0.48825570592462
- sentence_uniform_share: 0.24691358024691357
- sentence_opening_repeat_share: 0.08641975308641975
- sentence_opening_max_run: 1
- paragraph_cv: 0.37694506665260935
- short_paragraph_share: 0.35714285714285715
- paragraph_opening_repeat_share: 0.0
- forbidden_hits: {}
- filler_density_per_1000: 0.0
- jargon_density_per_1000: 0.6854009595613434
- nominalization_density_per_1000: 2.7416038382453736
- triad_density_per_1000: 0.0
- generic_lead_hits: 0
- digits_count: 26
- numeric_context_count: 3
- example_markers: 6
- links_count: 3
- question_marks: 9
- local_hits: 5
- service_hits: 19
- second_person_hits: 45
- specificity_points: 6

## Detector ensemble
- detectors_run: 3
- mean_ai_risk: 0.001
- max_single_ai_risk: 0.001
- max_ai_prob: 0.580
- max_single_ai_prob: 0.700
- model openai-community/roberta-base-openai-detector: avg_ai_risk=0.001, pass=PASS
- model Hello-SimpleAI/chatgpt-detector-roberta: avg_ai_risk=0.000, pass=PASS
- model nbroad/openai-detector-base: avg_ai_risk=0.001, pass=PASS
