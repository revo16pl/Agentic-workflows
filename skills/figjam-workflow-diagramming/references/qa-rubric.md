# QA Rubric for Workflow Documentation Diagrams

Use this rubric before final handoff.

## 1. Hard Checks (Must Pass)
1. Global flow direction is left-to-right.
2. Each major step is a separate section.
3. Each section has internal substeps.
4. Each section includes action, artifact, and control context.
5. Files are described in the same step context (no detached references by default).
6. PASS/FAIL decision logic is explicit.
7. Legend is present and semantically consistent.
8. No HTML tags in Mermaid labels.
9. Tools/APIs/frameworks are explicit for operational steps.
10. Output is explicit for operational steps.
11. No guessed details: file/tool/output statements align with source workflow.

If any hard check fails, revise before delivery.

## 2. Scoring (0-2 each)
1. Structural clarity
- 0: hard to follow structure
- 1: mostly clear
- 2: fully clear and consistent

2. Process completeness
- 0: key stages missing
- 1: minor missing pieces
- 2: all key stages present

3. Context fidelity
- 0: contains generic or guessed statements
- 1: partially grounded
- 2: clearly grounded in workflow sources

4. Documentation depth
- 0: keyword-level notes only
- 1: mixed quality
- 2: complete-sentence, meaningful explanations

5. File documentation quality
- 0: file names only
- 1: partial descriptions
- 2: one-sentence purpose per file where listed

6. Decision quality
- 0: decisions implicit
- 1: partially explicit
- 2: explicit binary logic + clear recovery path

7. Readability at normal zoom
- 0: dense wall of text
- 1: acceptable with effort
- 2: scannable and balanced

8. Visual consistency
- 0: inconsistent styles/colors
- 1: minor inconsistencies
- 2: consistent visual semantics

Total score: 0-16.

Interpretation:
- 15-16: production-ready
- 13-14: minor polish needed
- 10-12: meaningful revision needed
- <=9: redesign required

## 3. Acceptance Scenarios
1. Non-technical viewer can explain each step without verbal help.
2. Viewer can state what happens in each step now (not just step name).
3. Viewer can identify which tool/API produced which output.
4. Viewer can explain why each listed file exists.
5. Viewer can trace FAIL -> recovery -> PASS path quickly.

## 4. Density Recovery Checklist
1. Split overloaded sections into more substeps.
2. Keep full-sentence explanations.
3. Preserve file purpose sentences.
4. Preserve decision and transition logic.
5. Re-run hard checks and scoring.
