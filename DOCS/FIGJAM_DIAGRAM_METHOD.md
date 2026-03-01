# FigJam Diagram Method (MCP + Quality Standard)

## 1) Cel
Zdefiniowac powtarzalna metode tworzenia diagramow wysokiej jakosci w FigJam:
- czytelnych dla nietechnicznych osob,
- spojnych wizualnie,
- latwych do utrzymania i iteracji.

Ta metoda jest zoptymalizowana pod generowanie przez Figma MCP `generate_diagram` i dopracowanie finalu bezposrednio w FigJam.

---

## 2) Najwazniejsze wnioski z researchu

1. W Claude Code diagram jest generowany jako link do FigJam, a dalsze poprawki robimy juz w FigJam.
2. Figma MCP `generate_diagram` wspiera:
- Flowchart
- Gantt
- State diagram
- Sequence diagram
3. FigJam ma natywne formatowanie tekstu (bold, listy, markdown), wiec nie opieramy sie na tagach HTML.
4. Dla Mermaid:
- uzywamy markdown strings (`**bold**`, `*italic*`, nowe linie),
- stylowanie przez `classDef`,
- unikamy tekstowych pulapek (np. node z malym `end` moze psuc flowchart).
5. Dla jakosci diagramu warto stosowac checklisty C4:
- tytul + zakres + legenda,
- jednoznaczne etykiety relacji i kierunek strzalek,
- spojnosc kolorow i znaczen.

---

## 3) Skills: co juz mamy i co warto dodac

## Lokalnie (juz dostepne)
- `figma` (OpenAI/Codex local skill): workflow MCP i implementacja z Figma.

## Zewnetrzne (find-skills / skills.sh)
- `softaworks/agent-toolkit@mermaid-diagrams` (najbardziej trafiony pod diagramy Mermaid).
- `eraserlabs/eraser-io@eraser-diagrams` (alternatywa dla architektury i BPMN).
- `figma/mcp-server-guide@implement-design` (mocny workflow MCP od Figma).

Uwaga:
- Query `figjam` nie zwrocil dedykowanego skilla.
- Query `mermaid diagram` zwrocil dobrze dopasowane skille.

---

## 4) Standardowy workflow (powtarzalny)

## Faza A - Input Brief (przed rysowaniem)
Zawsze zbieramy:
1. Cel diagramu (po co i dla kogo).
2. Typ diagramu (flowchart / sequence / state / gantt).
3. Zakres (co jest IN, co jest OUT).
4. Poziom szczegolowosci (executive / operational / technical).
5. Decyzje krytyczne (gdzie sa bramki PASS/FAIL).

Definition of ready:
- brief ma 5 punktow powyzej,
- jest wskazana grupa odbiorcow.

## Faza B - Projekt informacji (bez kolorow)
1. Rozpisz kroki jako krotkie etykiety (max ~8-12 slow na node).
2. Jedna idea na jeden node.
3. Decyzje jako romby/punkty warunkowe.
4. Zasada: od lewej do prawej LUB z gory na dol (bez mieszania).
5. Jesli diagram jest duzy: podziel na sekcje (Setup, Execution, QA, Export).

## Faza C - Generowanie MCP
1. Generuj najpierw wersje "skeleton" (struktura + relacje).
2. Potem druga iteracja: opisy i czytelnosc.
3. Prompt powinien jawnie mowic:
- typ diagramu,
- orientacja (np. LR),
- limit kolorow (np. 3-4),
- koniecznosc legendy i decision nodes,
- tekst po polsku.

## Faza D - Dopracowanie w FigJam
Po wygenerowaniu:
1. Popraw teksty i skroty.
2. Uzyj natywnych funkcji FigJam:
- bold/listy/indentacja,
- connectors z etykietami,
- sections do grupowania etapow.
3. Ustaw stala palete:
- 1 kolor neutralny (kroki glowne),
- 1 kolor ostrzegawczy (decision/fail),
- 1 kolor sukcesu (pass/end),
- opcjonalnie 1 kolor notatek.

## Faza E - QA diagramu (gate)
Checklista PASS:
1. Tytul + zakres sa jasne.
2. Diagram ma legende.
3. Kazda strzalka ma sensowny kierunek.
4. Etykiety relacji sa konkretne (nie "uses", tylko np. "uruchamia walidacje").
5. Kolory sa spojne i maja stale znaczenie.
6. Brak crossing chaos (minimalna liczba przecinajacych sie linii).
7. Czytelne dla osoby nietechnicznej bez dodatkowego tlumaczenia.

Jesli FAIL:
- skracamy etykiety,
- dzielimy diagram na 2 plansze,
- redukujemy kolory,
- upraszczamy relacje.

---

## 5) Prompt template do MCP (start)

Uzyj tego szablonu:

```text
Stworz diagram w FigJam przez Figma MCP generate_diagram.

Kontekst:
- Cel: {cel}
- Odbiorca: {odbiorca}
- Typ: {flowchart|sequence|state|gantt}
- Zakres IN: {lista}
- Zakres OUT: {lista}

Wymagania:
- Jezyk polski.
- Uklad LR.
- Maksymalnie 4 kolory.
- Dodaj legende.
- Dodaj decision nodes dla PASS/FAIL.
- Rozbij etapy na sekcje: Setup, Plan/Research, Execution, QA, Export.
- Teksty w node: krotkie, konkretne, max 12 slow.
- Bez HTML tagow typu <b> lub <code>.
```

---

## 6) Anti-patterny (czego nie robic)
1. Nie wciskac HTML (`<b>`, `<code>`) do etykiet.
2. Nie naduzywac kolorow (teczowy diagram = slabsza czytelnosc).
3. Nie wrzucac dlugich akapitow do pojedynczego node.
4. Nie mieszac kilku logik kierunku przeplywu.
5. Nie zostawiac relacji bez etykiet przy procesach decyzyjnych.

---

## 7) Metryki jakosci (prosty score)
Skala 0-2 na kazdy punkt:
1. Czytelnosc dla laika
2. Jednoznacznosc przeplywu
3. Spojnosc kolorow i legendy
4. Jakosc opisow node
5. Uzytecznosc do decyzji/egzekucji

Suma:
- 8-10: gotowe
- 6-7: drobne poprawki
- <=5: przebudowa

---

## 8) Zrodla (research)
- Figma Help: Create FigJam diagrams with Claude  
  https://help.figma.com/hc/en-us/articles/37883260397975
- Figma Developer Docs: Tools and prompts (MCP)  
  https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/
- Figma Help: Create text and links in FigJam  
  https://help.figma.com/hc/en-us/articles/1500004291281-Create-text-and-links-in-FigJam
- Figma Help: Connectors and lines in FigJam  
  https://help.figma.com/hc/en-us/articles/1500004414542-Create-diagrams-and-flows-with-connectors-and-lines
- Figma Help: Organize board with sections  
  https://help.figma.com/hc/en-us/articles/4939765379351-Organize-your-FigJam-board-with-sections
- Mermaid docs: Flowchart syntax, markdown strings, classDef  
  https://mermaid.js.org/syntax/flowchart.html
- C4 model: notation and review checklist  
  https://c4model.com/diagrams/notation  
  https://c4model.com/diagrams/checklist
- OMG BPMN 2.0 specification  
  https://www.omg.org/spec/BPMN/2.0/

