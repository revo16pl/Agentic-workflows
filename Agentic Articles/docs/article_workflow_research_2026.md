# Research 2026: Workflow pisania artykulow SEO + copywriting (PL lokalny)

## 1. Cel i zakres
Ten dokument zbiera aktualne zasady i praktyki (stan na 2026-02-28), zeby zaprojektowac workflow tworzenia artykulow, ktore:
- sa zgodne z aktualnymi wytycznymi SEO,
- sa dobre redakcyjnie (czytelne, uzyteczne, wiarygodne),
- wspieraja cele biznesowe (lead generation i wzrost ruchu),
- maja powtarzalny proces i twarde quality gates.

Zakres v1:
- kanal glowny: wlasna strona (SEO first),
- jezyk/rynek: PL lokalny,
- dlugosc domyslna: 1200-2500 slow,
- manualny review czlowieka przed publikacja.

## 2. Metodologia researchu
1. Przejrzane zrodla pierwszorzedowe: Google Search Central, Google Search Console API, Google Search Quality Evaluator Guidelines, Medium Help Center, GOV.UK writing guidance, dokumentacje narzedzi SEO API.
2. Zebrane sygnaly praktyczne: jak laczyc intencje, strukture tresci i SEO on-page bez keyword stuffingu.
3. Porownanie z Twoim pierwotnym 9-step flow i identyfikacja brakow operacyjnych.

Uwaga metodyczna:
- Tam, gdzie Google opisuje "system rankingowy" ogolnie, a nie podaje twardego progu, traktujemy to jako kierunek strategiczny (nie twarda formula).

## 3. Najwazniejsze wnioski (executive summary)
1. SEO w 2026 nadal premiuje "helpful, reliable, people-first content" i wartosc dla uzytkownika; sama techniczna optymalizacja nie wystarczy.
2. Tresc AI jest akceptowalna, ale niskiej jakosci tresc masowo generowana pod manipulacje rankingiem jest ryzykiem spam policy violation.
3. Najwiekszy brak w typowych workflowach to brak formalnego fakt-check i brak mapowania intencji przed pisaniem.
4. Najlepsze efekty daje workflow artefaktowy: brief -> intent map -> SERP snapshot -> fact bank -> keyword cluster -> blueprint -> draft -> QA -> export to Google Docs.
5. Manualny review czlowieka powinien zostac staly, szczegolnie dla tematow YMYL (zdrowie/finanse/prawo).

## 4. Aktualne reguly SEO (Google)

### 4.1 People-first i helpful content
- Google wskazuje, ze nie ma "sekretow SEO", a stabilna strategia to tworzenie tresci uzytecznej dla ludzi i technicznie dobrze dostepnej dla crawlowania.
- Helpful content guidance podkresla dopasowanie tresci do potrzeb odbiorcy i realnej wartosci merytorycznej.

Implikacja dla workflow:
- Kazdy artykul musi miec sekcje "unique value" (co wnosi ponad TOP10),
- Outline musi odpowiadac konkretnej intencji zapytania, nie tylko frazie.

### 4.2 Spam policies (kluczowe ryzyka)
Google spam policies precyzuja m.in.:
- scaled content abuse,
- expired domain abuse,
- site reputation abuse.

Implikacja dla workflow:
- Brak masowej produkcji podobnych stron bez wartosci,
- Brak "przepisywania konkurencji" bez nowej wartosci,
- Obowiazkowy fact bank i section-level value check.

### 4.3 AI-generated content
Google nie zakazuje samego AI. Krytyczne jest, czy tresc jest pomocna i wiarygodna.

Implikacja dla workflow:
- AI moze pisac draft, ale:
  - musi przejsc factual QA,
  - musi miec jawna liste zrodel,
  - nie moze byc publikowana bez review czlowieka.

### 4.4 Ranking systems i page experience
- Google stale aktualizuje systemy rankingowe.
- Page experience nie jest jednym "master signal", ale ma znaczenie wspierajace (m.in. Core Web Vitals i UX).

Implikacja dla workflow:
- W v1 konczymy workflow na eksporcie do Google Docs.
- Monitoring po publikacji (CTR, query mix, pozycje, indexation, CWV) jest etapem v2.

## 5. Praktyki jakosci artykulow (Medium + redakcja)

### 5.1 Wnioski z Medium
- Medium rozdziela dystrybucje na kanal followers i kanal network distribution.
- Lepsza jakosc merytoryczna i czytelnosc zwieksza szanse na dalsza dystrybucje.
- Dla SEO i syndykacji istotne sa canonical links i poprawny metadata setup.

Implikacja dla workflow:
- Tworzymy "distribution-ready content": mocny lead, czytelne scannable sekcje, dobra struktura tytulu i podtytulu, semantyczne naglowki.
- Dla publikacji poza strona glowna (np. Medium) stosujemy canonical strategy.

### 5.2 GOV.UK writing for web (uniwersalny standard czytelnosci)
Kluczowe zasady:
- start from user needs,
- front-load najwazniejszych informacji,
- pisz krotko i konkretnie,
- projektuj tekst do skanowania (naglowki, listy, krotkie akapity).

Implikacja dla workflow:
- Każda sekcja w blueprint musi miec:
  - cel sekcji,
  - 1-2 kluczowe tezy,
  - "so what" dla czytelnika.

## 6. Model intencji i mapowania tresci

### 6.1 Typy intencji
- Informational: "jak", "co to jest", "poradnik".
- Commercial investigation: porownania, opinie, alternatywy.
- Transactional/local: intencja zakupu/kontaktu, zapytania lokalne.
- Navigational: dotarcie do konkretnej marki/podstrony.

### 6.2 Dlaczego intencja musi byc przed keyword research
Jesli zaczniemy od samych fraz, czesto konczymy na sztucznej tresci. Intencja ustawia:
- format (guide, checklist, comparison, local landing article),
- glebokosc,
- CTA i miejsce CTA.

### 6.3 Mapping intent -> struktura artykulu
- Informational: problem -> wyjasnienie -> praktyczne kroki -> bledy -> FAQ -> CTA soft.
- Commercial: kryteria wyboru -> porownanie -> rekomendacja -> CTA medium/hard.
- Local: usluga + lokalizacja -> trust signals -> lokalne case'y -> map/contact CTA.

## 7. Porownanie: Twoje 9 krokow vs workflow docelowy

| Twoj krok | Co jest dobre | Co trzeba doprecyzowac | Zmiana w v1 |
|---|---|---|---|
| 1. Brief | Dobry start | Brak formalnych pol celu/intencji | Dodany template `article_brief` |
| 2. Research konkurencji | Trafne | Brak standaryzacji outputu | `article_research_pack.md` (sekcja SERP) |
| 3. Research wiedzy | Trafne | Ryzyko halucynacji bez zrodel | `article_research_pack.md` (sekcja Fact Bank) |
| 4. Research SEO | Trafne | Brak modelu cluster + entities | `article_research_pack.md` (sekcja Keyword Cluster) |
| 5. Plan artykulu | Bardzo dobre | Brak jednolitego formatu | `article_research_pack.md` (sekcja Blueprint) |
| 6. Pisanie artykulu | Dobre | Za duzo swobody bez constraints | Writing constraints + source binding |
| 7. Weryfikacja | Dobre | Brak scoringu i hard gate | QA 5x20 pkt + critical failures |
| 8. Finalizacja artykulu | Dobre | Brak standaryzacji miejsca docelowego | Export checklist do Google Docs |
| 9. Monitoring po publikacji | Dobre (jako v2) | Niepotrzebne na etapie draft workflow | Odsuniete do roadmapy v2 |

## 8. Rekomendowany pipeline end-to-end (v1)
1. Intake briefu -> `article_brief.md`
2. Research pack (intent + SERP + facts + keywords + blueprint) -> `article_research_pack.md`
3. Draft v1 -> `article_draft_v1.md`
4. QA + rewrite -> `qa_report.md`, `article_draft_v2.md`
5. Agent QA approval + package ready for owner review -> `publish_ready.md`
6. Export final article to Google Docs -> komunikat `ARTYKUL GOTOWY: <doc_url>`

## 9. Ryzyka i anty-wzorce
1. Thin content: dluga tresc bez realnej wartosci.
2. Keyword stuffing i over-optimization anchorow.
3. Brak aktualnosci zrodel (stare statystyki/nieaktualne przepisy).
4. "Parafraza konkurencji" bez unikalnych insightow.
5. Brak intent fit (np. transakcyjny CTA w czysto informacyjnym zapytaniu).
6. Brak lokalnych sygnalow przy local intent (adres, obszar dzialania, kontekst lokalny).

Mitigacje:
- obowiązkowy fact bank,
- minimalny score QA 85/100,
- krytyczne fail conditions.

## 10. Narzedzia: MVP free/low-cost -> skala premium

### 10.1 MVP (start)
- Google Search + manual SERP review (Top 10),
- Google Trends (trend i sezonowosc),
- Google Docs + Drive API (finalny export),
- AlsoAsked/PAA scraping light (jesli dostepne),
- ChatGPT/Gemini jako wsparcie researchu, ale zawsze z weryfikacja zrodel.

### 10.2 Mid-tier
- DataForSEO API do zautomatyzowanych danych keyword/SERP,
- Semrush API (jesli budzet i plan contentowy uzasadnia koszt).

### 10.3 Enterprise
- Ahrefs API v3 (wg dokumentacji pomocowej: ograniczenia dostepu, model enterprise-only).

Wniosek biznesowy:
- dla v1 najlepszy ROI daje MVP + dobry proces redakcyjny,
- premium API ma sens po potwierdzeniu PMF workflow i wolumenu publikacji.

## 11. Kryteria sukcesu workflowu
1. Proces
- 100% artykulow ma komplet artefaktow (brief, intent, SERP, fact bank, cluster, blueprint, QA).
2. Jakosc
- minimum 85/100 w QA, 0 critical failures.
3. Delivery
- finalny artykul jest wyeksportowany do Google Docs z poprawnym linkiem.
4. Biznes
- rosnacy CTR i wzrost konwersji wspieranych przez content.

## 12. Walidacja best practices (Hostinger + Google) - 2026 check
Weryfikacja pokrycia naszego workflow:

1. Search intent, struktura naglowkow, internal linking, aktualizacja tresci
- Pokryte w naszym SOP (Step 2, 3, 6, 10).
- Zgodne z praktykami opisanymi w aktualnym tutorialu Hostinger.

2. Quality-first zamiast "keyword-only"
- Pokryte przez fact bank, uniqueness gate i QA 85/100.
- Zgodne z Google people-first i helpful content.

3. Uzycie AI
- Pokryte: AI do researchu/draftu jest dozwolone, ale spamowe automatyczne tresci pod ranking sa zabronione.
- Zgodne z Google guidance o tresci AI.

4. Luki, ktore nalezy domknac (dodane teraz)
- E-E-A-T/authorship gate,
- snippet/AI extraction gate,
- source freshness rule,
- schema consistency gate.

## 13. LLM visibility (Google first, inne LLM second)
Stan na 2026-02-28:

1. Google AI features
- Google komunikuje, ze nie ma dodatkowych wymagan do pojawiania sie w AI Overviews i AI Mode poza solidnym SEO i Search Essentials.

2. Snippet controls i AI usage
- Google snippet controls (`nosnippet`, `max-snippet`, `data-nosnippet`) dzialaja szeroko.
- Zbyt restrykcyjne ustawienia moga ograniczyc wykorzystanie tresci przez AI features.

3. Strukturyzacja pod cytowalnosc
- Answer-first fragmenty pod H2/H3, z jasna odpowiedzia i dopiero potem rozwiniecie.
- Widoczne dowody i zrodla przy kluczowych tezach.

4. Dla ChatGPT search
- Jesli chcemy widocznosc, nie blokujemy `OAI-SearchBot` w `robots.txt`.

Wniosek:
- "GEO/LLM SEO" to nie osobny system zamiast SEO. To dobrze wykonane SEO + jasna struktura odpowiedzi + kontrola snippet/crawler policy.

## 14. Przechowywanie researchu i finalnych artykulow (Google Docs)
Rekomendowany model: hybryda lokalne repo + chmura Google.

1. Source of truth
- Lokalny Markdown w repo (`Agentic Articles/workspace/...`) jako audytowalna historia zmian.

2. Warstwa wspolpracy
- Finalny `article_draft_v2.md` i `publish_ready.md` eksportowane do Google Docs w dedykowanym folderze.

3. Praktyczne podejscie API
- Uzyj Google Docs API do tworzenia/aktualizacji dokumentu.
- Uzyj Google Drive API do osadzenia pliku w konkretnym folderze i zarzadzania dostepami.
- Trzymaj `GOOGLE_DRIVE_FOLDER_ID` i dane OAuth w `.env`/`credentials.json` (nie commitowac sekretow).

4. Model folderow (Drive)
- `/Agentic Articles/Research/`
- `/Agentic Articles/Published Drafts/`
- `/Agentic Articles/Archive/`

5. Minimalne artefakty eksportu
- Title, final body, metadata (topic, intent, voice, date), link do lokalnego workspace.

## 15. Szybki research narzedzi 2026 (co ma sens)

### 15.1 Must-have (realny ROI)
1. Google Docs + Drive API
- Pewny export finalnych artykulow do chmury.
2. DataForSEO (Keywords + SERP)
- Skalowalny keyword/SERP dataset z lokalizacja i jezykiem.
3. Google Search + Trends
- Podstawowe sygnaly popytu i intencji na etapie researchu.

### 15.2 Should-have (przy skali)
1. Semrush API
- Rozszerzony competitive intel i dodatkowe raporty (model jednostek API).
2. Structured data validation flow
- Rich Results Test + schema policy checks przed publikacja.
3. Google Search Console API
- Przyda sie po rozszerzeniu workflow o etap publikacji/audytu.

### 15.3 Optional / zalezne od budzetu
1. Ahrefs API
- Wg help center: dostep API jest ograniczony planowo; czesto nie jest to narzedzie startowe dla MVP.

### 15.4 Rekomendacja wdrozenia (kolejnosc)
1. Etap A (teraz): Google Docs export + manual SERP + obecny SOP.
2. Etap B: DataForSEO do Step 3/5 (SERP + frazy).
3. Etap C: Semrush API, gdy wolumen i budzet uzasadniaja.

## 16. Dalsze kroki po tym researchu
1. Utrzymac SOP v1 i od razu przetestowac na 1 pilocie lokalnym.
2. Trzymac brand voice wewnatrz `company_context_profiles.md` i wybierac go automatycznie po `company`.
3. Po 3-5 artykulach: ocena KPI i decyzja o pelnej integracji DataForSEO/Semrush.

## 17. Multi-company architecture (uniwersalne podejscie)
Problem:
- Sam brand voice nie wystarczy, bo agent musi znac uslugi, CTA i strony firmy.

Rozwiazanie:
- Dodac pojedyncza warstwe konfiguracji: `company` (naturalna nazwa firmy + aliasy).
- Ten profil okresla:
  - czym zajmuje sie firma,
  - jakie uslugi i URL-e wolno linkowac,
  - jakie CTA sa dozwolone na ToFu/MoFu/BoFu,
  - jakie claimy sa zakazane,
  - jaki brand voice obowiazuje dla tej firmy.

W praktyce:
1. Brief zawiera tylko `company` (np. "studio balans").
2. Step 6 blueprint planuje linkowanie uslugowe wg profilu (min/max).
3. QA sprawdza, czy linki i CTA sa zgodne z profilem.
4. Ten sam workflow obsluguje wiele firm, bo agent laduje inny profil bez zmian logiki procesu.

Przykladowy prompt seed:
- "Robimy artykul ogolny o zaletach treningu EMS dla studio balans."

## 18. Human-quality writing (anti-slop) - research update 2026
Wnioski laczace Twoje notatki + zrodla zewnetrzne:
1. Detektory AI nie sa stabilnym gate'em jakosci:
- OpenAI wycofal publiczny AI classifier (niska skutecznosc).
- NIST pokazuje, ze nowoczesne modele coraz latwiej myla detektory.
2. Dlatego workflow nie powinien optymalizowac pod "ominięcie detektora", tylko pod:
- konkretnosc,
- wiarygodnosc,
- naturalny rytm jezykowy,
- lokalne osadzenie i unikalna wartosc.
3. Sygaly anty-slop do twardego QA:
- brak monotonnego rytmu zdan i powtarzalnych otwarc,
- brak "gładkich", pustych akapitow bez nowej informacji,
- ostrozne formulowanie tez (bez absolutow typu "zawsze", "gwarantuje"),
- obecne ograniczenia/kontrperspektywy tam, gdzie temat jest zlozony,
- konkrety operacyjne (kroki, liczby, przykłady lokalne), nie ogolniki.
4. Dodatkowa zasada redakcyjna (z notatek):
- unikac "word swap only"; skuteczna humanizacja dzieje sie na poziomie calego akapitu, nie pojedynczych slow,
- przy rewrite dopuszczalne jest przestawianie kolejnosci argumentow/list, jesli poprawia logike i czytelnosc.
5. Praktyczna implikacja:
- detektor AI moze byc sygnalem pomocniczym, ale nie jest kryterium publikacji.
- kryterium publikacji jest PASS w human-quality QA i gates SEO/factual.

### 18b. Detector ensemble policy (wdrozenie v2)
Wdrozenie praktyczne (stricte operacyjne):
1. Uzywamy open-source detector ensemble jako dodatkowego hard gate (`detector_ensemble_pass`), ale:
- traktujemy wynik jako sygnal ryzyka statystycznego, nie dowod autorstwa.
- laczymy go z gate'ami stylistycznymi (zakazane frazy, rytm skladni, konkretnosc, voice).
2. Powod:
- pojedynczy detector ma wysoka wariancje i false positive (potwierdzaja benchmarki typu RAID i raporty NIST).
- ensemble + stylometryczne gate'y daje stabilniejszy wynik operacyjny niz jeden classifier.
3. Zasada bezpieczenstwa:
- jesli detector FAIL, tekst wraca do rewizji merytoryczno-stylistycznej (nie \"word swap\").
- publikacja tylko po PASS wszystkich gate'ow.

## 19. Dlugosc tresci (adaptive length) - research update 2026
Najwazniejsze:
1. Google nie podaje minimalnej ani "idealnej" liczby slow.
2. Dlugosc ma wynikac z intencji i pelnego pokrycia tematu, nie z arbitralnego targetu.
3. Narzedzia SEO (np. Semrush SEO Content Template) rekomenduja dlugosc na bazie Top10 konkurencji.
4. Badania contentowe (np. Orbit Media) pokazuja, ze dluzsze wpisy czesto koreluja z lepszymi wynikami, ale to korelacja, nie uniwersalna regula.

Rekomendacja do workflow:
1. Ustawiaj dlugosc adaptacyjnie:
- `word_count_min` ~ mediana Top10,
- `word_count_max` ~ p75/p90 Top10.
2. Domyslne zakresy startowe:
- local service: 900-1800,
- informational deep-dive: 1400-3000,
- comparison/commercial: 1200-2600,
- pillar: 2500-4500.
3. Priorytet: "intent coverage + unikalna wartosc + czytelnosc", nie "wieksza liczba slow za wszelka cene".

## 20. Iteracyjny loop jakosci (przed eksportem do Docs)
Docelowy mechanizm:
1. Agent pisze draft v2.
2. Agent uruchamia `pre_export` validation.
3. Jesli FAIL:
- generuje `qa_iteration_feedback.md`,
- wraca do poprawki (rewrite),
- ponownie uruchamia walidacje.
4. Dopiero po PASS eksportuje do Google Docs.
5. W Google Docs trafia tylko paczka "Ready_for_manual_review".

---

## Zrodla (sprawdzone 2026-02-28)
1. Google SEO Starter Guide  
   https://developers.google.com/search/docs/fundamentals/seo-starter-guide
2. Google: Creating helpful, reliable, people-first content  
   https://developers.google.com/search/docs/fundamentals/creating-helpful-content
3. Google Search Essentials: Spam policies  
   https://developers.google.com/search/docs/essentials/spam-policies
4. Google: Guidance about AI-generated content  
   https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
5. Google: AI features and your website  
   https://developers.google.com/search/docs/appearance/ai-features
6. Google: Snippet controls  
   https://developers.google.com/search/docs/appearance/snippet
7. Google: Ranking systems guide  
   https://developers.google.com/search/docs/appearance/ranking-systems-guide
8. Google: Page experience  
   https://developers.google.com/search/docs/appearance/page-experience
9. Google Search Console API reference  
   https://developers.google.com/webmaster-tools/v1/api_reference_index
10. Google structured data policies  
    https://developers.google.com/search/docs/appearance/structured-data/sd-policies
11. Google Search Quality Evaluator Guidelines (PDF, 2025 edition)  
    https://static.googleusercontent.com/media/guidelines.raterhub.com/en//searchqualityevaluatorguidelines.pdf
12. Medium Help: What happens to your story after you hit publish  
    https://help.medium.com/hc/en-us/articles/214677068-What-happens-to-your-story-after-you-hit-publish
13. Medium Help: SEO setting and canonical link option  
    https://help.medium.com/hc/en-us/articles/360003053992-Set-up-your-story-s-search-engine-optimization-SEO-settings
14. GOV.UK: Writing for GOV.UK  
    https://www.gov.uk/guidance/content-design/writing-for-gov-uk
15. Hostinger: How to write SEO-friendly content (updated 2026-02-27)  
    https://www.hostinger.com/tutorials/write-seo-friendly-content
16. DataForSEO docs: Keywords Data API overview  
    https://docs.dataforseo.com/v3/keywords_data-overview/
17. Semrush API: Get started + FAQ  
    https://developer.semrush.com/api/basics/get-started/  
    https://developer.semrush.com/api/basics/faq/
18. Ahrefs Help: API access by subscription context  
    https://help.ahrefs.com/en/articles/72096-is-it-possible-to-use-your-api-functions-with-a-usual-ahrefs-subscription
19. OpenAI crawler controls (OAI-SearchBot/GPTBot/ChatGPT-User)  
    https://developers.openai.com/api/docs/bots
20. Google PageSpeed Insights API  
    https://developers.google.com/speed/docs/insights/v5/get-started
21. OpenAI: AI classifier for indicating AI-written text (retired update)  
    https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/
22. NIST: Can you trust AI text detectors?  
    https://www.nist.gov/news-events/news/2024/07/can-you-trust-ai-text-detectors
23. Orbit Media: Annual Blogger Survey 2025 (article length correlations)  
    https://www.orbitmedia.com/blog/blogger-survey/
24. Semrush: SEO Content Template (length based on top rivals)  
    https://www.semrush.com/kb/1276-seo-content-template
25. Google Search Central: Automated ranking systems and self-assessment questions (word count guidance)  
    https://developers.google.com/search/docs/fundamentals/creating-helpful-content
