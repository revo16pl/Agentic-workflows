# FigJam Diagram Method (MCP + Visual Standard)

## 1) Cel
Zdefiniować powtarzalną metodę tworzenia diagramów wysokiej jakości w FigJam:
- czytelnych dla nietechnicznych osób,
- spójnych wizualnie,
- lekkich w odbiorze,
- łatwych do iteracji.

Ta metoda jest zoptymalizowana pod generowanie przez Figma MCP `generate_diagram` i dopracowanie finalu bezpośrednio w FigJam.

---

## 2) Główna decyzja projektowa
Domyślny styl to teraz `overview-first`, a nie ciężki diagram SOP.

To oznacza:
1. Diagram ma najpierw dobrze tłumaczyć proces.
2. Styl wizualny ma być zbliżony do prostych explainerów:
- pastelowe kolory,
- szerokie, czytelne boxy,
- jedna idea na jeden node,
- krótki tytuł + 1-2 linie opisu.
3. Tryb `detailed` zostawiamy tylko do workflow operacyjnych, gdzie trzeba pokazać pliki, bramki, narzędzia i blokery.

Uwaga:
- Mermaid i `generate_diagram` nie dadzą 1:1 ręcznie rysowanego stylu ze screenshotów.
- Możemy jednak bardzo dobrze odtworzyć ich charakter przez paletę, spacing, prostotę copy i ograniczenie gęstości.

---

## 3) Najważniejsze wnioski techniczne
1. Diagram jest generowany jako link do FigJam, a dalsze poprawki można zrobić już w FigJam.
2. Figma MCP `generate_diagram` wspiera:
- flowchart,
- gantt,
- state diagram,
- sequence diagram.
3. Dla Mermaid:
- używamy `flowchart LR` jako domyślnego układu,
- stylujemy przez `classDef`,
- używamy quoted labels i markdown strings tylko tam, gdzie pomagają w łamaniu linii,
- nie używamy HTML w etykietach.
4. Największy wpływ na jakość ma nie sama składnia Mermaid, tylko:
- właściwy poziom abstrakcji,
- zwięzłość treści,
- minimalna liczba crossing lines,
- spójna semantyka kolorów.

---

## 4) Tryby pracy

## Tryb A - `overview` (default)
Używaj dla:
- prezentacji,
- tłumaczenia procesu,
- onboardingowych explainers,
- workflow do szybkiego zrozumienia.

Zasady:
1. Jeden node = jedna idea.
2. Tekst w node:
- krótki tytuł,
- jedna linia: co się dzieje,
- opcjonalnie druga linia: po co / jaki efekt.
3. Maksymalnie 4-5 kolorów.
4. Decision nodes tylko tam, gdzie rozgałęzienie naprawdę ma znaczenie.
5. Legenda tylko jeśli kolory nie są samowyjaśniające.

## Tryb B - `detailed`
Używaj dla:
- SOP-ów,
- procesów operacyjnych,
- runbooków,
- diagramów do audytu i handoffu.

Zasady:
1. Można użyć sekcji per krok.
2. Można użyć układu action / artifacts / control.
3. Pokazujemy pliki, narzędzia, outputy, blokery i warunki przejścia.
4. Legenda i jawna logika PASS/FAIL są zalecane.

---

## 5) Standardowy workflow

## Faza A - Input Brief
Zawsze zbieramy:
1. Cel diagramu.
2. Odbiorcę.
3. Typ diagramu.
4. Zakres IN / OUT.
5. Poziom szczegółowości: `overview` albo `detailed`.

Definition of ready:
- brief ma 5 punktów powyżej,
- jest wskazana grupa odbiorców,
- wiadomo, czy priorytetem jest prezentacja czy dokumentacja.

## Faza B - Projekt informacji
1. Rozpisz główne kroki procesu.
2. Zdecyduj, które z nich muszą być osobnymi node'ami.
3. Upewnij się, że każdy node niesie jedną myśl.
4. W `overview` skróć opisy zanim dodasz nowe boxy.
5. W `detailed` dołóż szczegóły dopiero po ustaleniu szkieletu przepływu.

## Faza C - Generowanie MCP
1. Generuj najpierw skeleton.
2. Potem dopracuj czytelność.
3. Prompt powinien jawnie mówić:
- tryb (`overview` albo `detailed`),
- typ diagramu,
- orientację LR,
- limit kolorów,
- język polski,
- oczekiwany charakter wizualny.

## Faza D - Dopracowanie w FigJam
Po wygenerowaniu:
1. Skróć lub wygładź copy tam, gdzie boxy są za ciężkie.
2. Popraw spacing i relacje.
3. Użyj natywnych funkcji FigJam, jeśli trzeba:
- sections,
- connectors z etykietami,
- drobne poprawki tekstu.

## Faza E - QA diagramu
Checklista PASS:
1. Główna ścieżka jest jasna po kilku sekundach.
2. Diagram wygląda lekko i nie jest przeładowany.
3. Kolory są spójne i mają stałe znaczenie.
4. Każda strzałka ma sensowny kierunek.
5. Etykiety relacji są konkretne.
6. Brak chaosu od przecinających się linii.
7. Poziom szczegółowości pasuje do odbiorcy.

Jeśli FAIL:
- skracamy etykiety,
- dzielimy diagram na 2 plansze,
- usuwamy detale z `overview`,
- redukujemy kolory,
- upraszczamy relacje.

---

## 6) Prompt template do MCP

Użyj tego szablonu:

```text
Stwórz diagram w FigJam przez Figma MCP generate_diagram.

Kontekst:
- Cel: {cel}
- Odbiorca: {odbiorca}
- Typ: {flowchart|sequence|state|gantt}
- Zakres IN: {lista}
- Zakres OUT: {lista}
- Tryb: {overview|detailed}

Wymagania:
- Język polski.
- Układ LR.
- Maksymalnie 4-5 kolorów.
- Styl wizualny: prosty explainer procesu, pastelowe boxy, dużo czytelności.
- Każdy node ma zawierać jedną ideę.
- W trybie overview: krótki tytuł + 1-2 linie opisu.
- W trybie detailed: pokaż action / artifacts / control oraz potrzebne narzędzia i outputy.
- Dodaj decision nodes tylko tam, gdzie są potrzebne.
- Bez HTML tagów typu <b> lub <code>.
```

---

## 7) Anti-patterny
1. Nie wciskać HTML (`<b>`, `<code>`) do etykiet.
2. Nie nadużywać kolorów.
3. Nie wrzucać długich akapitów do pojedynczego node.
4. Nie mieszać kilku logik kierunku przepływu.
5. Nie robić diagramu SOP, jeśli celem jest prosty explainer.
6. Nie próbować sztucznie wymusić "ręcznie rysowanego" stylu hackami Mermaid.

---

## 8) Metryki jakości
Skala 0-2 na każdy punkt:
1. Czytelność dla laika
2. Jednoznaczność przepływu
3. Lekkość wizualna
4. Jakość opisów node'ów
5. Dopasowanie poziomu szczegółowości do celu

Suma:
- 8-10: gotowe
- 6-7: drobne poprawki
- <=5: przebudowa

---

## 9) Źródła
- Figma Help: Create FigJam diagrams with Claude  
  https://help.figma.com/hc/en-us/articles/37883260397975
- Figma Developer Docs: Tools and prompts (MCP)  
  https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/
- Figma Help: Connectors and lines in FigJam  
  https://help.figma.com/hc/en-us/articles/1500004414542-Create-diagrams-and-flows-with-connectors-and-lines
- Mermaid docs: Flowchart syntax, markdown strings, classDef  
  https://mermaid.js.org/syntax/flowchart.html
