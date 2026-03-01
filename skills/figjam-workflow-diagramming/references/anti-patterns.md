# Anti-Patterns for Workflow Documentation Diagrams

## 1. Keyword-Only Description
Anti-pattern:
- step cards use short labels without explanatory sentences.

Why it hurts:
- reader sees words but does not understand process behavior.

Fix:
- require complete-sentence explanation for what happens and why.

## 2. Literal Copy of User Draft
Anti-pattern:
- agent repeats user placeholder wording instead of rewriting into documentation quality.

Why it hurts:
- unfinished or vague text propagates into final artifact.

Fix:
- rewrite into clear SOP-style language while preserving intended meaning.

## 3. Detached File Mentions
Anti-pattern:
- file names appear without context or are separated from step logic.

Why it hurts:
- impossible to map file purpose to process moment.

Fix:
- keep file descriptions in the same step section where they are created/used.

## 4. File Name Without Purpose
Anti-pattern:
- file is listed but no sentence explains what it contains and why it exists.

Why it hurts:
- documentation is incomplete for onboarding/debugging.

Fix:
- one sentence per file purpose when file list is shown.

## 5. Tool/API Black Box
Anti-pattern:
- step does not identify what executes it.

Why it hurts:
- no operational traceability.

Fix:
- explicitly list script/tool/API/framework, or say `API: brak (operacja lokalna)`.

## 6. Output Black Box
Anti-pattern:
- tool/API listed but output missing.

Why it hurts:
- transition criteria and debugging become unclear.

Fix:
- state concrete output (file/status/URL/state change).

## 7. Missing Transition Logic
Anti-pattern:
- step descriptions omit transition condition and blockers.

Why it hurts:
- process cannot be run or audited consistently.

Fix:
- add control card with transition condition and blockers.

## 8. Hidden Decision Branches
Anti-pattern:
- PASS/FAIL logic implied in text only.

Why it hurts:
- failure path and recovery loop are invisible.

Fix:
- explicit binary decision node with labeled branches.

## 9. Mixed Global Directions
Anti-pattern:
- diagram mixes LR and top-down as primary flow.

Why it hurts:
- chronology is ambiguous.

Fix:
- keep LR as global direction; use TB only inside sections.

## 10. Decorative Overload
Anti-pattern:
- too many colors/styles/icons overshadow content.

Why it hurts:
- decreases readability and semantic consistency.

Fix:
- use fixed semantic palette and clear legend.

## 11. Hallucinated Workflow Details
Anti-pattern:
- agent invents files, APIs, or gate behavior not present in source workflow.

Why it hurts:
- documentation becomes untrustworthy.

Fix:
- ground statements in directive/scripts/artifacts; mark unknowns explicitly.

## 12. ASCII-Only Polish Output
Anti-pattern:
- Polish diagram content written without diacritics.

Why it hurts:
- lowers readability and perceived quality of documentation.

Fix:
- use full Polish characters (`ą ę ł ń ó ś ż ź`) in final labels and descriptions.

## 13. Fake Rich-Text with HTML
Anti-pattern:
- using HTML tags in Mermaid labels to force bold/italic.

Why it hurts:
- tags render as plain text and reduce clarity.

Fix:
- use structural emphasis: uppercase headers, bullets, and clean line breaks.
