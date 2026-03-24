# Directive: Transcript to Notes (Soft Hybrid v1)

**Goal**: Zamienić gotowy transkrypt w czytelne, użyteczne notatki, które brzmią jak własne notatki z oglądania materiału, a nie jak opis filmu albo meta-streszczenie.

## Inputs
- `transcript_path` (required): ścieżka do pliku `Transcript - ...md`

## Outputs
- `Notes - [Truncated Title].md`

## Tools
- `workflows/youtube-notes/scripts/generate_youtube_notes.py`

## Status
Ta dyrektywa opisuje aktywny workflow `transcript -> notes`.
Jest źródłem prawdy dla implementacji w `workflows/youtube-notes/scripts/generate_youtube_notes.py`.

## Core Principle
Notatki mają wyglądać tak, jakby człowiek oglądał film i zapisywał dla siebie najważniejsze rzeczy:
- idee,
- metody,
- workflowy,
- narzędzia,
- praktyczne wnioski,
- ograniczenia,
- dobre praktyki,
- rzeczy warte zapamiętania.

To nie ma być opis materiału z zewnątrz.

## Writing Style
- Pisz jak własne notatki, nie jak recenzja ani streszczenie filmu.
- Nie używaj sformułowań typu:
  - `autor mówi, że...`
  - `użytkownik pokazuje...`
  - `w materiale omówiono...`
  - `na tym filmie zobaczymy...`
- Zamiast tego zapisuj treść bezpośrednio:
  - czym jest dana metoda,
  - kiedy jej użyć,
  - jak działa,
  - dlaczego ma sens,
  - na co uważać,
  - jak wdrożyć ją w praktyce.

## Content Heuristics
- Zamieniaj „gadanie do kamery” na wiedzę użytkową.
- Jeśli pojawia się metoda, proces, heurystyka, framework, narzędzie, decyzja albo trade-off, zapisz to wprost.
- Jeśli fragment jest fluffem, autopromką, dygresją, powtórzeniem albo wypełniaczem, pomiń go.
- Jeśli z materiału wynika konkretny workflow, rozpisz go jako kroki.
- Jeśli z materiału wynika raczej zbiór zasad lub sposobu myślenia, zapisz to jako zasady i wnioski.
- Jeśli materiał miesza poziom strategiczny i operacyjny, notatki też mogą to mieszać. Nie trzeba tego sztucznie rozdzielać.

## Structure Guidance
Struktura ma pomagać, ale nie ma być sztywna.
Agent może dobierać nagłówki zależnie od materiału.

Najczęściej przydatne są sekcje takie jak:
- `Najważniejsze idee`
- `Metody i workflow`
- `Narzędzia / elementy systemu`
- `Praktyczne uwagi`
- `Do zapamiętania`

Można:
- łączyć sekcje,
- pomijać sekcje,
- zmieniać nazwy sekcji,
- dodawać podsekcje dla konkretnych metod.

Nie trzeba zawsze używać dokładnie tego samego układu.

## Quality Direction
- Priorytetem jest użyteczność przy ponownym wracaniu do materiału.
- Notatki mają być konkretne i naturalne.
- Lepiej zapisać mniej, ale sensownie, niż dużo i szablonowo.
- Lepiej przepisać wiedzę do formy praktycznej niż zostawić ją w formie opisu rozmowy.

## Anti-Patterns
Unikaj:
- metakomentarza o tym, co robi speaker,
- zdań w stylu szkolnego streszczenia,
- sztucznego „upychania” wszystkiego do jednej ramy,
- wymuszonego tonu eksperckiego,
- twardych limitów długości,
- obowiązkowych sekcji obecnych w każdym materiale,
- ocen typu `to było ciekawe`, jeśli nie niosą wartości użytkowej.

## Example Direction
Zamiast:

`Autor opowiada o metodzie follow-up i pokazuje, że warto z niej korzystać.`

Lepiej:

`Follow-up nurture: automatyczne domykanie codziennej pracy na pipeline leadów.`

- przechodzi po leadach na różnych etapach,
- zbiera historię rozmów,
- dopasowuje ton wiadomości do etapu relacji,
- czyści ręczną pracę sprzedawcy z powtarzalnych follow-upów,
- ma sens tam, gdzie follow-up jest codzienny i łatwo go zaniedbać.

## Workflow
1. Wczytaj transkrypt.
2. Odrzuć fragmenty, które nie niosą wartości notatkowej.
3. Wyciągnij wiedzę, metody, workflowy, zasady i praktyczne obserwacje.
4. Ułóż je w naturalne notatki z luźną, pomocną strukturą.
5. Zapisz wynik jako `Notes - [Truncated Title].md` obok transkryptu.

## Separation Rule
Ten workflow korzysta z gotowego transkryptu jako wejścia i nie odpowiada za pobieranie filmu ani ekstrakcję napisów.

## Pipeline Relationship
- Upstream:
  - `workflows/youtube-notes/transcript.directive.md`
- Downstream:
  - `workflows/youtube-notes/enrichment.directive.md`

If the parent request explicitly includes enrichment, this workflow should produce the base notes and then pass `notes_path` plus `transcript_path` to the enrichment stage instead of stopping after `Notes - ...md`.
