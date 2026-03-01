# qa_iteration_feedback.md

generated_at: 2026-03-01T12:33:17
status: revise_required
iteration_count: 1
max_iterations: 5

## Validation errors
- polish naturalness check failed
- {
  "ok": false,
  "gates": {
    "polish_title_naturalness_pass": false,
    "polish_collocation_pass": true,
    "polish_punctuation_pass": false,
    "structure_variance_pass_v2": false,
    "semantic_rewrite_pass_v2": false
  },
  "metrics": {
    "title_issues": [
      "Pattern not allowed in title: \\bkomu\\b.{0,60}\\bsi[eę]\\s+sprawdza\\b",
      "Pattern not allowed in title: \\bco\\s+naprawd[eę]\\s+daje\\s+i\\s+komu\\b"
    ],
    "collocation_hits": {},
    "unknown_uppercase_tokens": [
      "DA",
      "PMC"
    ],
    "punctuation_issues": [
      "Unknown uppercase abbreviations: DA, PMC"
    ],
    "sentence_cv": 0.48825570592462,
    "paragraph_cv": 0.37694506665260935,
    "max_sentence_bucket_share": 0.2345679012345679,
    "changed_ratio": 4.6072333563684786e-05,
    "changed_paragraphs": 0
  },
  "report_path": "/Users/revo/Documents/Coding Projects/Agentic workflow learning/Agentic Articles/workspace/2026-03-01_zalety-treningu-ems/polish_naturalness_report.md"
}

## Suggested actions
- Uruchom `execution/check_polish_naturalness.py`, popraw tytuł/kolokacje/rytm i powtórz walidację.
- Uzupelnij i ustaw `semantic_rewrite_pass: PASS` po holistycznym przepisaniu fragmentow (nie tylko word swap).
