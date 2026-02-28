# Notes: How to Use Claude Code Better Than 99% of People

## 🚀 Główna Koncepcja (Core Concept)
Film przedstawia **Claude Code** (oraz nowy tryb **Co-work**) jako potężne narzędzie do automatyzacji zadań, wykraczające poza zwykłe pisanie kodu. Głównym celem jest pokazanie, jak osoby nietechniczne mogą budować zaawansowane systemy (np. "YouTube Command Center" czy automatyzacja social media) łącząc Claude Code z narzędziami takimi jak **Apify** (scraping) i **SQLite** (baza danych), używając terminala jako centrum dowodzenia.

## 🛠️ Metody i Workflow (Actionable Methods & Workflows)

### 1. Instalacja i Setup
- **Claude Code**: Narzędzie działające w terminalu.
- **Warp**: Nowoczesny terminal polecany dla początkujących (posiada funkcje AI, które pomagają naprawiać błędy przy wpisywaniu komend).
- **Proces**: Instalacja Claude Code odbywa się przez terminal (np. `npm install ...`), a Warp może poprowadzić przez ten proces "za rękę".

### 2. Integracja z Apify (Scraping)
- Wykorzystanie **MCP (Model Context Protocol)** do połączenia Claude z platformą Apify.
- **Setup**: Użytkownik podaje klucz API Apify, a Claude (przez polecenie np. `claude mcp add apify`) konfiguruje połączenie.
- **Automatyzacja**: Claude potrafi samodzielnie przeszukać "sklep" Apify, znaleźć odpowiedni scraper (np. do Instagrama), przetestować go i wybrać najkorzystniejszą opcję.
- **Zastosowanie**: Scrapowanie danych o postach konkurencji (treść, wyniki, transkrypcje) do analizy.

### 3. Lokalna Baza Danych (SQLite)
- Zamiast drogich rozwiązań chmurowych, Claude może stworzyć lokalną bazę **SQLite** na komputerze użytkownika.
- **Struktura**: Przechowywanie zescrapowanych hooków, postów i transkrypcji w tabelach.
- **Wizualizacja**: Claude może wygenerować prosty interfejs webowy (HTML/JS) do przeglądania i edycji danych w tej bazie, co ułatwia pracę osobom nietechnicznym.

### 4. Algorytm "Wirusowości" (Virality Score)
- Tworzenie własnego systemu oceny potencjału treści.
- **Kryteria oceny**:
    - Ciekawość (Curiosity)
    - Emocje (Emotion)
    - Zwięzłość (Brevity)
    - Trafność/Trendy (Relevance)
- **Workflow**: Scrapowanie -> Analiza wg kryteriów -> Generowanie rankingu -> Tworzenie nowych treści na wzór najlepszych.

### 5. Claude MD (Knowledge Base)
- Kluczowa technika: Tworzenie pliku (często nazywanego `CLAUDE.md`) w folderze projektu.
- **Funkcja**: Służy jako "pamięć długotrwała" dla agenta. Zapisuje się tam instrukcje, jak wykonywać specyficzne zadania (np. komenda "make me viral"), jakie aktory Apify działają najlepiej, oraz preferencje użytkownika.
- Eliminuje to konieczność powtarzania tych samych instrukcji przy każdej nowej sesji.

## 💡 Kluczowe Spostrzeżenia (Key Insights)
- **Co-work jako "Brama"**: Tryb Co-work w Claude Desktop jest świetny na start, ale to terminal (Claude Code) daje pełną moc i kontrolę ("going to the source").
- **Human-in-the-Loop**: Pełna automatyzacja bez nadzoru jest ryzykowna (przykład z filmu: scraper błędnie zapisywał opisy jako transkrypcje). Człowiek musi weryfikować i korygować proces, aby system się uczył.
- **Jeden Input, Wiele Outputów (Leverage)**: Celem jest zbudowanie systemu, gdzie jedno polecenie (np. temat filmu) uruchamia łańcuch zdarzeń generujący wiele wyników (miniaturki, skrypty, posty, SEO).
- **Nauka przez Osmozę**: Używając Claude Code do budowania narzędzi, użytkownik naturalnie uczy się terminologii i logiki programistycznej, nawet jeśli nie pisze kodu ręcznie.

## 🔗 Narzędzia i Zasoby (Tools & Resources)
- **Claude Code**: Agent AI w terminalu.
- **Warp**: Terminal z wbudowanym AI.
- **Apify**: Platforma do scrapingu (dostępna przez MCP).
- **SQLite**: Lekka, plikowa baza danych (alternatywa dla Supabase).
- **Perplexity Labs**: Używane do generowania "Mega Promptów" – szczegółowych instrukcji dla Claude Code, aby precyzyjnie wykonał zadanie.
