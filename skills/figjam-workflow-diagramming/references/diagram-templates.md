# Diagram Templates (Mermaid) for Documentation-Grade Workflows

Use these templates as a structure baseline, then inject workflow-specific facts.

## Template A: Step Section with Action + Artifacts + Control

```mermaid
flowchart LR
  START["START"]:::process

  subgraph S1["KROK 1: ..."]
    direction TB
    S1A["1.1 Action\nCo to jest: ...\nCo dzieje sie teraz: ...\nPo co: ...\nNarzedzia/API/frameworky: ...\nOutput z narzedzi/API: ..."]:::process
    S1B["1.2 Artifacts\nTworzone pliki:\n- file_a: co zawiera i po co istnieje\n- file_b: co zawiera i po co istnieje"]:::process
    S1C["1.3 Control\nWarunek przejscia: ...\nCo blokuje przejscie: ..."]:::quality
    S1A --> S1B --> S1C
  end

  subgraph S2["KROK 2: ..."]
    direction TB
    S2A["2.1 Action ..."]:::process
    S2B["2.2 Artifacts ..."]:::process
    S2C["2.3 Control ..."]:::quality
    S2A --> S2B --> S2C
  end

  START --> S1A
  S1C --> S2A

  classDef process fill:#F5F8FF,stroke:#3B5AA3,color:#102A56,stroke-width:1.2px;
  classDef quality fill:#FFF6E8,stroke:#BA7A1F,color:#6A3E00,stroke-width:1.2px;
```

## Template B: Decision + Recovery Loop

```mermaid
flowchart LR
  CHECK["WALIDACJA\nCo sprawdzamy: ...\nOutput: PASS/FAIL"]:::quality --> DEC{"Czy PASS?"}:::decision
  DEC -->|"NIE"| FAIL["FAIL\nCo sie dzieje: tworzenie feedbacku\nOutput: qa_iteration_feedback.md"]:::fail
  FAIL --> FIX["POPRAWKI\nCo sie dzieje: update draft/artifacts"]:::fail --> CHECK
  DEC -->|"TAK"| PASS["PASS\nPrzejscie do exportu"]:::pass

  classDef quality fill:#FFF6E8,stroke:#BA7A1F,color:#6A3E00,stroke-width:1.2px;
  classDef fail fill:#FDECEC,stroke:#C62828,color:#7F1D1D,stroke-width:1.2px;
  classDef pass fill:#EAF7EE,stroke:#2E7D32,color:#1B5E20,stroke-width:1.2px;
  classDef decision fill:#FFF2CC,stroke:#9A6700,color:#5B3B00,stroke-width:1.8px;
```

## Template C: Legend Block

```mermaid
flowchart LR
  L1["Proces"]:::process
  L2["Quality/Gate"]:::quality
  L3["Fail/Iteracja"]:::fail
  L4["Pass/Koniec"]:::pass
  L5["Critical state"]:::critical
```

## Template D: Full Step Example (Compact but Complete)

```mermaid
flowchart LR
  K["KROK N\n1) Co to jest: ...\n2) Co dzieje sie teraz: ...\n3) Po co: ...\n4) Narzedzia/API/frameworky: ...\n5) Output z narzedzi/API: ...\n6) Pliki: nazwa + jednozdaniowy cel\n7) Warunek przejscia: ...\n8) Blokery: ..."]:::process
```

## Template Usage Notes
1. Use full sentences for documentation fields.
2. Keep one-sentence purpose per listed file.
3. Do not invent unknown details; verify first.
4. Keep LR globally, TB internally.
5. Keep decision logic explicit with labeled branches.
