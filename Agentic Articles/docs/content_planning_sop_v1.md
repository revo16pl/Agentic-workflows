# SOP v1: Content Planning Sprint (Workflow A)

## 1. Co to jest
To jest Twoj cykliczny proces planowania tematow blogowych na podstawie danych (co 2 tygodnie).
Cel: przygotowac sensowny backlog tematow, z ktorego dopiero uruchamiamy pisanie artykulow.

## 2. Co robisz Ty (manualnie)
1. Ustalasz priorytety sprintu:
- jakie firmy,
- jakie uslugi chcesz promowac,
- jakie lokalizacje,
- ile artykulow chcesz przygotowac na 2 tygodnie.

2. Pobierasz dane:
- Keyword Planner (UI): eksport CSV z frazami i wolumenem,
- Google SERP: top wyniki i PAA (w CSV),
- Google Trends: 12m + zapytania powiazane,
- opcjonalnie: dodatkowe seedy i sugestie z Google.

3. Wrzucasz pliki CSV do `research_inputs/`.

## 2b. Najprostsza opcja (autopilot, rekomendowane)
Jesli nie chcesz recznie ogarniac SERP/PAA/Trends, robisz tylko to:
1. Eksportujesz CSV z frazami (Keyword Planner lub inne narzedzie).
2. Uruchamiasz jedna komende:
```bash
python3 execution/content_planning_autopilot.py \
  --company "studio balans" \
  --keyword-files "/sciezka/do/keywords_1.csv" "/sciezka/do/keywords_2.csv"
```
3. Skrypt sam:
- tworzy sprint,
- normalizuje CSV,
- dociaga SERP/PAA (Serper/SerpApi),
- dociaga Trends (pytrends),
- buduje backlog i kolejke (`run_queue.csv`).

## 3. Jak odpalasz pipeline
```bash
python3 execution/content_planning_init.py --sprint-date 2026-03-15 --companies "studio balans,druga firma"
python3 execution/content_planning_ingest.py --sprint "Agentic Articles/planning/2026-03-15_sprint"
python3 execution/content_planning_cluster.py --sprint "Agentic Articles/planning/2026-03-15_sprint"
python3 execution/content_planning_gate.py --sprint "Agentic Articles/planning/2026-03-15_sprint"
python3 execution/content_planning_to_queue.py --sprint "Agentic Articles/planning/2026-03-15_sprint"
```

Alternatywnie (autopilot, 1 komenda):
```bash
python3 execution/content_planning_autopilot.py \
  --company "studio balans" \
  --keyword-files "/sciezka/do/keywords_export.csv"
```

## 4. Co musi przejsc (strict gate)
- min 60 fraz z wolumenem na firme,
- min 30 SERP rekordow + min 8 domen na firme,
- min 10 pytan PAA na firme,
- min 5 trend queries na firme,
- min 4 approved tematy na firme,
- approved temat musi miec: primary, min 8 secondary, intent, service URL, CTA.

Jesli `planning_hard_block_pass=FAIL`, nie przechodzisz dalej do pisania.

## 5. Jak uruchomic pisanie artykulu z planu
```bash
python3 execution/prepare_article_from_queue.py --queue-row-id "rq-0001"
```

To automatycznie:
- tworzy workspace artykulu,
- prefilluje brief,
- zapisuje referencje do sprintu i topicu w `run_context.md`.

## 6. Zasada krytyczna
Nie uruchamiamy Workflow B z "losowego" tematu.
Zawsze start z `RUN_QUEUE` gdzie `workflow_b_ready=yes`.

## 7. Checklista operacyjna
- [ ] Sprint initialized
- [ ] Keyword CSV wgrane
- [ ] SERP CSV wgrane
- [ ] PAA CSV wgrane
- [ ] Trends CSV wgrane
- [ ] planning_hard_block_pass=PASS
- [ ] run_queue.csv gotowe
- [ ] Artykuly startowane tylko przez `prepare_article_from_queue.py`
