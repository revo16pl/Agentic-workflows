# Style System for FigJam Workflow Diagrams

Use this style system for consistent, low-noise workflow visualization.

## 1. Global Layout
1. Use global flow direction `LR`.
2. Group major phases as separate `subgraph` sections.
3. Keep section order consistent with process chronology.
4. Keep legend in a distinct block, preferably near bottom-right.

## 2. Semantic Color Classes
Use maximum 5 semantic classes.

1. `process`: main steps and operational actions.
2. `quality`: gates, checks, thresholds, validations.
3. `fail`: failure path and recovery loop.
4. `pass`: success path and end states.
5. `critical` or `decision`: source-of-truth control points.

## 3. Recommended ClassDef Baseline
Use this as baseline and adjust only minimally.

```mermaid
classDef process fill:#F5F8FF,stroke:#3B5AA3,color:#102A56,stroke-width:1.2px;
classDef quality fill:#FFF6E8,stroke:#BA7A1F,color:#6A3E00,stroke-width:1.2px;
classDef fail fill:#FDECEC,stroke:#C62828,color:#7F1D1D,stroke-width:1.2px;
classDef pass fill:#EAF7EE,stroke:#2E7D32,color:#1B5E20,stroke-width:1.2px;
classDef critical fill:#FDECEC,stroke:#B42318,color:#7A1C18,stroke-width:1.8px;
classDef decision fill:#FFF2CC,stroke:#9A6700,color:#5B3B00,stroke-width:1.8px;
```

## 4. Typographic Guidance
1. Keep lines short; avoid long paragraphs in a single line.
2. Break content into bullet-like line blocks.
3. Prefer concrete nouns and verbs over abstract phrasing.
4. Keep label casing consistent across sections.

## 5. Readability Rules
1. Keep node text scannable at 75-100% zoom.
2. Avoid dense cross-links and crisscross arrows.
3. Keep edge labels short and explicit (`TAK`, `NIE`, `PASS`, `FAIL`).
4. Prefer one decision node per major gate cluster.

## 6. Section Naming Conventions
Use stable names so different agents produce similar outputs.

1. `KROK N: ...`
2. `GATE N: ...`
3. `WALIDACJA ...`
4. `EXPORT ...`
5. `LEGENDA ...`

## 7. When to Deviate
Deviate only if user explicitly asks for:
1. top-down flow,
2. stylized/creative board,
3. separate file map panel,
4. additional color semantics.
