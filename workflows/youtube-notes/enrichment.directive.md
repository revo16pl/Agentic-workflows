# Directive: Transcript Notes Enrichment (Multi-Agent v2)

**Goal**: Wziąć bazowe notatki wygenerowane z transkryptu i przekształcić je w bardziej dopracowany dokument: konkretniejszy, praktyczniejszy, lepiej ustrukturyzowany i bardziej przydatny jako materiał do przekazania dalej.

## Inputs
- `notes_path` (required): ścieżka do pliku `Notes - ...md`
- `transcript_path` (recommended): ścieżka do pliku `Transcript - ...md`

## Outputs
- `Enriched Notes - [Truncated Title].md`

## Status
Ta dyrektywa definiuje aktywny etap enrichmentu po bazowych notatkach.
To jest workflow agent-run, nie skrypt-first.

## Core Principle
Enrichment nie tworzy dokumentu od zera. Jego zadaniem jest:
- doprecyzować zbyt skrótowe fragmenty,
- rozwinąć kluczowe idee,
- dodać praktyczne wyjaśnienia,
- dodać przykłady i kontekst użycia,
- poprawić strukturę i użyteczność skanowania,
- podnieść jakość dokumentu jako handoff/tutorial.

## Execution Model
Ten workflow powinien być realizowany przez głównego agenta z użyciem uproszczonej orkiestracji multi-agent.

Minimalny układ:
- główny agent = orkiestrator i redaktor końcowy,
- subagent 1 = wykrywanie luk i miejsc do rozwinięcia,
- subagent 2 = enrichment/review jakości dokumentu.

Nie trzeba dodawać większej liczby ról, jeśli 2 lekkie subagenty wystarczą.

## Required Multi-Agent Behavior
Główny agent powinien:
1. wczytać `notes_path` i `transcript_path`,
2. zlecić analizę luk jednemu subagentowi,
3. zlecić krytykę jakości / handoff-readiness drugiemu subagentowi,
4. scalić wyniki,
5. samodzielnie napisać finalną wersję `Enriched Notes - ...md`.

Subagenci nie powinni zapisywać finalnego dokumentu.
Ich zadaniem jest dostarczyć materiał wejściowy do finalnej redakcji.

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
- Pozostaw agentowi swobodę decyzji, które fragmenty rzeczywiście warto rozwinąć.
- Nie próbuj rozwijać każdej sekcji na siłę.

## What Not To Force
Nie narzucaj:
- twardych word countów,
- obowiązkowej liczby sekcji,
- obowiązkowej liczby przykładów,
- jednego sztywnego szablonu dokumentu,
- obowiązkowego rozwijania każdego punktu,
- sztucznego podziału na typ materiału.

To ma być enrichment sensowny redakcyjnie, a nie mechaniczny.

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
3. Uruchom subagenta `Gap Finder`, który wskaże miejsca zbyt skrótowe, zbyt ogólne albo niewystarczająco praktyczne.
4. Uruchom subagenta `Enrichment Reviewer`, który oceni handoff quality, strukturę i przydatność dokumentu dla innej osoby.
5. Scal wyniki obu ról.
6. Rozwiń tylko te sekcje, które rzeczywiście zyskają na enrichmentcie.
7. Dodaj przykłady, doprecyzowania, praktyczne wskazówki i lepszą strukturę tam, gdzie to podnosi użyteczność.
8. Zapisz wynik jako `Enriched Notes - [Truncated Title].md`.

## Suggested Subagent Contracts

### Subagent 1: Gap Finder
Wejście:
- `notes_path`
- `transcript_path`

Wyjście:
- krótka lista sekcji lub fragmentów do rozwinięcia,
- czego w nich brakuje,
- opcjonalnie krótki sygnał z transkryptu, który uzasadnia rozwinięcie.

### Subagent 2: Enrichment Reviewer
Wejście:
- `notes_path`
- opcjonalnie wynik `Gap Finder`

Wyjście:
- uwagi o strukturze,
- uwagi o handoff/tutorial quality,
- uwagi o miejscach, które nadal brzmią zbyt roboczo albo zbyt skrótowo,
- uwagi o brakujących przykładach lub praktycznych wskazówkach.

## Validation Direction
Po enrichmentcie główny agent powinien sprawdzić:
- czy dokument jest wyraźnie bardziej użyteczny niż wersja bazowa,
- czy nie wrócił meta-opis typu `autor mówi`, `w materiale`, `na tym filmie`,
- czy zostały dodane sensowne rozwinięcia, a nie tylko większa objętość,
- czy struktura pomaga w przekazaniu dokumentu komuś dalej.

## Relationship To Other Workflows
- Upstream:
  - `workflows/youtube-notes/transcript.directive.md` -> tworzy transkrypt
  - `workflows/youtube-notes/notes.directive.md` -> tworzy bazowe notatki
- Downstream:
  - brak; to ostatni etap w pipeline `video -> transcript -> notes -> enrichment`
