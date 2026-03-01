# Process Mapping Best Practices for FigJam Workflow Documentation

Use this guide to keep diagrams operationally accurate and readable.

## 1. Map Before You Draw
1. Identify process boundaries (start/end).
2. Identify major phases and decision points.
3. For each phase capture: inputs, action, output, owner/actor.
4. Confirm transition conditions and blockers.

## 2. Use an Action-Artifact-Control Model
For each step section:
1. Action: what happens now and why.
2. Artifacts: files/data generated or updated.
3. Control: gate, transition condition, blockers.

This prevents vague process cards.

## 3. Distinguish Facts vs Interpretation
1. Facts: names of scripts, files, gate keys, thresholds.
2. Interpretation: explanation of role and impact.
3. If a fact is not confirmed, mark as unknown rather than guessing.

## 4. Document Outputs as Contracts
Each output should answer:
1. What is produced?
2. Who consumes it next?
3. What decision depends on it?

Example:
- `quality_gate.json` is consumed by pre-export validation and blocks export when hard gates fail.

## 5. Make Decisions Auditable
1. Use explicit decision nodes.
2. Label both branches (PASS/FAIL or TAK/NIE).
3. Show recovery target on FAIL branch.
4. Include iteration cap if the workflow has one.

## 6. Write for Non-Technical Readers
1. Prefer complete sentences over tags and shorthand.
2. Explain intent of each step, not only execution mechanics.
3. Avoid unexplained acronyms.
4. Keep text concrete and contextual.

## 7. Keep Visual Noise Low
1. Use a limited semantic color set.
2. Avoid decorative styling.
3. Keep arrows meaningful and avoid unnecessary cross-links.
4. Split dense sections into substeps.

## 8. Definition of Done for a Diagram
A process diagram is done when a new team member can:
1. explain what happens in each step,
2. identify what output is produced and why,
3. trace failure handling to recovery,
4. understand what blocks transition to next stage.
