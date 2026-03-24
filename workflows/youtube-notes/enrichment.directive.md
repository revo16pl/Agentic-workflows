# Directive: Transcript Notes Enrichment (v1)

**Goal**: Wziąć bazowe notatki wygenerowane z transkryptu i przekształcić je w bardziej dopracowany dokument: konkretniejszy, praktyczniejszy, lepiej ustrukturyzowany i bardziej przydatny jako materiał do przekazania dalej.

## Inputs
- `notes_path` (required): ścieżka do pliku `Notes - ...md`
- `transcript_path` (recommended): ścieżka do pliku `Transcript - ...md`

## Outputs
- `Enriched Notes - [Truncated Title].md`

## Status
Ta dyrektywa definiuje osobny etap enrichmentu po bazowych notatkach.
Jest source of truth dla przyszłego narzędzia wykonawczego.

## Core Principle
Enrichment nie tworzy dokumentu od zera. Jego zadaniem jest:
- doprecyzować zbyt skrótowe fragmenty,
- rozwinąć kluczowe idee,
- dodać praktyczne wyjaśnienia,
- dodać przykłady i kontekst użycia,
- poprawić strukturę i użyteczność skanowania,
- podnieść jakość dokumentu jako handoff/tutorial.

## What Enrichment Should Improve
- zbyt krótkie sekcje,
- zbyt ogólne tezy,
- brak przykładów,
- brak praktycznych wskazówek wdrożeniowych,
- brak czytelnej hierarchii sekcji,
- dokument, który brzmi jak notatka robocza zamiast materiał do przekazania dalej.

## Enrichment Rules
- Zachowuj główny sens bazowych notatek.
- Rozwijaj treść, nie rozwadniaj jej.
- Dodawaj więcej kontekstu typu:
  - co to jest,
  - po co tego używać,
  - kiedy to ma sens,
  - jak wdrożyć to w praktyce,
  - na co uważać,
  - przykłady zastosowania.
- Poprawiaj strukturę:
  - lepsze nagłówki,
  - podsekcje,
  - logiczne grupowanie treści,
  - lekkie znaczniki wizualne, jeśli poprawiają czytelność.
- Unikaj przepisywania dokumentu w stylu marketingowym albo zbyt akademickim.

## Anti-Patterns
Unikaj:
- pisania wszystkiego od nowa bez związku z bazowymi notatkami,
- sztucznego pompowania objętości,
- rozwijania sekcji, które nic nie zyskują na rozwinięciu,
- dodawania pustych ozdobników bez poprawy użyteczności,
- powrotu do meta-opisu typu `autor mówi`, `w materiale`, `na tym filmie`.

## Workflow
1. Wczytaj bazowe notatki.
2. Wczytaj transkrypt jako materiał wspierający i źródło doprecyzowań.
3. Zidentyfikuj sekcje, które są zbyt skrótowe albo zbyt ogólne.
4. Rozwiń je o dodatkowe objaśnienia, przykłady, praktyczne zastosowanie i lepszą strukturę.
5. Dodaj tylko takie elementy, które zwiększają użyteczność dokumentu.
6. Zapisz wynik jako `Enriched Notes - [Truncated Title].md`.

## Relationship To Other Workflows
- Upstream:
  - `workflows/youtube-notes/transcript.directive.md` -> tworzy transkrypt
  - `workflows/youtube-notes/notes.directive.md` -> tworzy bazowe notatki
- Downstream:
  - brak; to ostatni etap w pipeline `video -> transcript -> notes -> enrichment`
