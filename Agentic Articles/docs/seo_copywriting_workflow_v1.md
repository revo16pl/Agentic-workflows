# SOP v2.2: SEO + Copywriting Workflow (Agentic Articles)

## Update v3.2 (Content Profiles: article + service_page)
- Dodano profile tresci:
  - `article` (long-form, workflow z RUN_QUEUE),
  - `service_page` (URL-first, krotki pakiet tresci pod podstrone uslugowa).
- Dodano URL bootstrap dla service pages:
  - `python3 execution/prepare_service_page_from_url.py --url ... --company ...`
- Dodano extractor kontekstu strony:
  - `execution/extract_service_page_context.py` (Playwright first, curl fallback).
- Dodano profile-aware walidacje:
  - `python3 execution/article_workflow_validate.py --content-profile service_page`
  - walidacja sekcji: `Subheading`, `Opis`, `Najważniejsze informacje`.
- Dodano profile-aware export:
  - `python3 execution/export_to_gdocs.py --content-profile service_page`.
- Dodano lekki research pack dla `service_page`:
  - mniejsze minima datasetu w `research_evidence_manifest.json` (`minimum_dataset`).

## Update v3.0 (Data-Driven Research Layer)
- Dodano automatyczny etap `research_fetch` oparty o dane z:
  - Google Ads Keyword Planner API (keyword metrics),
  - Serper API + SerpApi fallback (SERP/PAA),
  - pytrends (trend signals),
  - Google Suggest (autosuggest).
- Dodano nowy hard gate researchu: `check_research_quality.py`.
- Rozszerzono `research_evidence_manifest.json` do wersji `3.0` o:
  - `providers`, `query_seeds`, `keyword_metrics`, `serp_results`, `trend_points`, `competitor_matrix`.
- Eksport do Google Docs zostaje zablokowany, jeśli `research_hard_block_pass != PASS`.

## Update v3.3 (Service Page Quality Hardening)
- Wprowadzono fallback research (`ok_with_fallback`) przy braku Google Ads:
  - workflow nadal zbiera SERP/PAA/Suggest/Trends/competitor,
  - w `run_context.md` zapisywane są: `research_fallback_reason`, `research_confidence`,
  - w `research_evidence_manifest.json` zapisywane są: `providers_status`, `data_quality_note`.
- Dodano machine-readable profile firmy:
  - `Agentic Articles/docs/company_context_profiles.yaml`,
  - resolver: `execution/company_profile_resolver.py`,
  - snapshot w workspace: `company_profile_snapshot.json`.
- Dla `service_page` draft nie jest prefillowany istniejącym copy z URL.
- Dodano artefakt `service_page_writer_packet.md` jako obowiązkowy brief redakcyjny pod manualny draft.
- Dodano artefakt `editorial_review.md` jako obowiązkowy zapis iteracji redakcyjnej dla `article` i `service_page`.
- Dodano nowe service gates:
  - `service_tab_content_nonempty_pass`,
  - `service_faq_min_items_pass`,
  - `service_no_placeholder_pass`,
  - `service_brand_voice_alignment_pass`.
- Dodano editorial QA gates:
  - `service_editorial_review_exists`,
  - `service_editorial_review_structure`,
  - `service_editorial_review_complete`,
  - `service_editorial_iterations_pass`,
  - `service_editorial_logic_pass`,
  - `service_editorial_final_decision`.
- Eksport ma tryby:
  - `--export-mode prod` (domyślny, blokuje wszystkie `--skip-*`),
  - `--export-mode debug` (dozwolone skipy + warning `NOT_FOR_PUBLISH`).

### Minimal Artifact Policy
Po udanym eksporcie workflow sprząta pliki robocze i zostawia lokalnie tylko:
- `article_research_pack.md`
- `final_output.md`

Pozostałe pliki są traktowane jako robocze / tymczasowe i mogą być usunięte po sukcesie.

### Manual Draft Protocol (service_page)
1. Uruchom `prepare_service_page_from_url.py` i potwierdź, że powstały:
- `service_page_context.json`,
- `company_profile_snapshot.json`,
- `service_page_writer_packet.md`.
2. Uruchom `research_fetch.py` i upewnij się, że:
- `research_fetch_status` jest `ok` lub `ok_with_fallback`,
- `article_research_pack.md` zawiera dane (bez pustych sekcji),
- writer packet ma sekcję `Top research insights` uzupełnioną.
3. Napisz ręcznie `article_draft_v2.md` na podstawie writer packet:
- nowy subheading (bez kopiowania aktualnego leadu),
- 3 akapity opisu,
- komplet treści pod każdą zakładkę i min 2 pozycje FAQ.
4. Wykonaj obowiązkowy editorial QA loop i uzupełnij `editorial_review.md`:
- Pass 1: logika i sens zdań,
- Pass 2: content-strategy (intent, odpowiedzi na pytania, kolejność sekcji),
- Pass 3: copywriting (clarity, benefits, przeformułowanie pełnych fragmentów),
- Pass 4: copy-editing (naturalność, rytm, usunięcie sztucznych konstrukcji).
5. Zapisz minimum 2 iteracje i ustaw:
- `logic_pass: PASS`
- `post_machine_qa_revision_completed: yes` po finalnym krótkim passie po machine QA
- `final_decision: approved`
6. Przepuść pełne gate’y jakości (bez skipów).
7. Eksportuj tylko przez `--export-mode prod`.

## Update v3.1 (Workflow A -> Workflow B Integration)
- Dodano osobny Workflow A (bi-weekly content planning sprint) z artefaktami:
  - `Agentic Articles/planning/{YYYY-MM-DD}_sprint/`
  - `planning_dataset.json`, `content_plan_candidates.csv`, `content_plan_backlog.csv`, `planning_gate.json`, `run_queue.csv`.
- Workflow B startuje wyłącznie z `RUN_QUEUE` przez:
  - `python3 execution/prepare_article_from_queue.py --queue-row-id \"rq-0001\"`
- Dodano hard gate `topic_from_approved_plan_pass`:
  - artykuł musi mieć w `run_context.md` referencję do approved topicu z Workflow A.
- Dodano strict planning gates (Workflow A):
  - keyword/serp/paa/trends coverage,
  - cluster quality,
  - backlog minimum per company.

## 1. Cel SOP
Zdefiniowac powtarzalny, decision-complete proces tworzenia artykulow SEO dla rynku PL lokalnego, z naciskiem na jakosc merytoryczna, intent fit i wynik biznesowy.

## 2. Zakres i zasady operacyjne
- Primary channel: artykul tworzony pod publikacje na stronie internetowej.
- Dlugosc: strategia adaptacyjna (intent + SERP), nie sztywny jeden zakres dla kazdego tematu.
- Manual approval: odbywa sie po eksporcie do Google Docs (final owner review).
- Endpoint workflow: zapis finalnego artykulu do Google Docs.
- AI usage: dozwolone do researchu i draftu, ale nie zwalnia z fakt-check i review.

## 3. Role
- Owner (human): zatwierdza brief i finalny artykul.
- SEO/Content Agent: przygotowuje research, blueprint, draft i QA.
- Reviewer (human): wykonuje finalny sanity check (fakty, ton, zgodnosc brandowa).

## 4. Struktura artefaktow na artykul
Dla kazdego tematu tworz katalog roboczy:

`Agentic Articles/workspace/{YYYY-MM-DD}_{slug}/`

Wymagane pliki:
1. `article_brief.md`
2. `article_research_pack.md` (intent + SERP + facts + keywords + blueprint)
3. `research_evidence_manifest.json` (source-of-truth dla danych research)
4. `quality_gate.json` (source-of-truth dla machine gates)
5. `article_draft_v2.md`
6. `editorial_review.md`

## 5. Research quality protocol (obowiazkowy)
Agent moze uzyc tylko zrodel, ktore przejda ponizszy filtr:
1. Source tiers:
   - Tier 1: dokumentacja oficjalna, akty prawne, dane publiczne, publikacje naukowe.
   - Tier 2: wiarygodne media branzowe i raporty firm badawczych.
   - Tier 3: blogi/opinie (tylko pomocniczo, nigdy jako jedyne potwierdzenie tezy).
2. Regula krytycznych tez:
   - kazda krytyczna teza musi miec min. 1 zrodlo Tier 1 lub 2.
3. Regula triangulacji:
   - jesli temat jest sporny, wymagane sa min. 2 niezalezne zrodla.
4. Regula swiezosci:
   - dane operacyjne/statystyki: domyslnie <= 24 miesiace (chyba ze brief mowi inaczej).
5. Regula transparentnosci:
   - w sekcji `Fact Bank` w `article_research_pack.md` zawsze zapisuj URL i date publikacji/aktualizacji.

## 6. Workflow krok po kroku

### Step 1: Intake briefu
Input:
- temat,
- grupa docelowa,
- cel biznesowy,
- lokalizacja,
- CTA,
- ograniczenia,
- company (wpis naturalny; dopasowanie po aliasach z company context profiles),
- source_freshness_max_months.

Output:
- `article_brief.md` (wg template).

Gate:
- brief ma wypelnione wszystkie pola wymagane.
- firma jest dopasowana jednoznacznie do jednego profilu.
- brand voice laduje sie automatycznie z profilu firmy.

### Step 2: Klasyfikacja intencji i typu tresci
Dzialania:
- okresl dominujaca intencje: informational/commercial/transactional/navigational/local,
- okresl typ artykulu: guide, comparison, local service, FAQ, thought leadership.

Output:
- sekcja `Intent Map` w `article_research_pack.md`:
  - dominant intent,
  - secondary intent,
  - uzasadnienie,
  - format recommended.

Gate:
- jest jasny "intent-fit hypothesis" (1-2 zdania: dlaczego ten format pasuje do zapytania).

### Step 3: SERP i konkurencja (Top 10)
Dzialania:
- przeanalizuj Top 10 wynikow,
- zapisz: tytuly, H2, orientacyjna dlugosc, assets (FAQ/lista/tabela/wideo), local signals,
- wykryj content gaps.

Output:
- sekcja `SERP Snapshot` w `article_research_pack.md`.

Gate:
- min. 10 URLi,
- min. 5 konkretnych content gaps.
- min. 5 wynikow powinno byc realnymi konkurentami dla intencji (nie tylko duze portale ogolne).

### Step 4: Research merytoryczny (fakty i zrodla)
Dzialania:
- buduj bank faktow: teza -> dowod -> URL -> data,
- flaguj informacje niepewne,
- preferuj zrodla primary.

Output:
- sekcja `Fact Bank` w `article_research_pack.md`.

Gate:
- kazda kluczowa teza ma co najmniej 1 wiarygodne zrodlo,
- brak tez bez przypisanego dowodu.
- krytyczne tezy oparte o Tier 1/Tier 2.

### Step 5: Keyword research i clustering
Dzialania:
- wybierz primary keyword,
- zbuduj secondary keywords,
- dodaj entities i PAA,
- dopisz note o intent alignment.

Output:
- sekcja `Keyword Cluster` w `article_research_pack.md`.

Gate:
- primary + min. 8 secondary + min. 5 entities + min. 5 PAA,
- brak keyword stuffing targetow (no forced repetition targets).

### Step 6: Strategia artykulu i outline
Dzialania:
- zbuduj H1/H2/H3,
- przypisz cel kazdej sekcji,
- zdefiniuj word budget per section,
- zaplanuj internal links zgodnie z profilem firmy,
- zaplanuj schema recommendation (Article/FAQ/LocalBusiness - zalezne od intentu),
- zaplanuj answer-first blocks pod kluczowymi H2/H3 (40-80 slow).

Output:
- sekcja `Article Blueprint` w `article_research_pack.md`.

Gate:
- kazda sekcja ma "reader outcome",
- jest sekcja unikalnej wartosci (original insight/case/checklist).
- blueprint ma co najmniej 3 answer-first blocks.
- blueprint ma min. 1 i max. 3 linki do stron uslug z profilu firmy.

### Step 7: Draft
Dzialania:
- napisz caly tekst wg blueprint,
- trzymaj ton marki,
- stosuj human-quality constraints (naturalny rytm, zroznicowana skladnia, konkrety zamiast fillerow),
- osadz cytowania faktow z sekcji `Fact Bank` w `article_research_pack.md` (parafraza + source note),
- nie tworz nowych "faktow" bez zrodel,
- linkuj tylko do uslug i stron z aktywnego profilu firmy.

Output:
- `article_draft_v2.md` (jedyny roboczy draft tekstu)

Gate:
- 1200-2500 slow (domyslnie),
- logiczny flow i zgodnosc z intent_map.

### Step 7a: Editorial QA loop (obowiazkowy dla article i service_page)
Dzialania:
- agent czyta draft jak redaktor, nie jak walidator regexowy,
- robi osobny pass na logike, sens, flow argumentu i naturalnosc polszczyzny,
- poprawia cale fragmenty, a nie pojedyncze slowa,
- stosuje kolejno perspektywy:
  - `content-strategy`,
  - `copywriting`,
  - `copy-editing`,
- zapisuje najwazniejsze poprawki i decyzje w `editorial_review.md`.

Gate dla `service_page`:
- `editorial_review.md` istnieje,
- ma komplet sekcji review,
- ma min. 2 iteracje,
- `logic_pass = PASS`,
- po machine QA agent robi jeszcze krotki pass wdrozeniowy i ustawia `post_machine_qa_revision_completed = yes`,
- `final_decision = approved`.

### Step 7b: Polish language auto-fix (obowiazkowy)
Dzialania:
- uruchom `execution/check_polish_language.py` na `article_draft_v2.md` (lub przygotowanym draftcie roboczym),
- zastosuj auto-poprawki gramatyki i pisowni (PL),
- wygeneruj `language_quality_report.md`,
- jesli gate jezykowy nie przechodzi: popraw i uruchom ponownie.

Gate:
- diacritics gate = PASS,
- grammar gate = PASS,
- raport jezykowy bez error status.

### Step 7c: Polish naturalness gate v2 (obowiazkowy)
Dzialania:
- uruchom `execution/check_polish_naturalness.py`,
- waliduj tytul, kolokacje, interpunkcje, zroznicowanie struktury oraz rewrite semantyczny v1->v2.

Gate:
- `polish_title_naturalness_pass` = PASS,
- `polish_collocation_pass` = PASS,
- `polish_punctuation_pass` = PASS,
- `structure_variance_pass_v2` = PASS,
- `semantic_rewrite_pass_v2` = PASS.

### Step 7d: Polish fluency ML signal (obowiazkowy)
Dzialania:
- uruchom `execution/check_polish_fluency_ml.py` (pre-trained model, bez treningu lokalnego),
- ocen plynnosc jezykowa przez pseudo-perplexity.

Gate:
- `polish_fluency_ml_pass` = PASS.

### Step 7e: Humanization gate v2 (obowiazkowy)
Dzialania:
- uruchom `execution/check_humanization.py` na finalnym drafcie roboczym,
- sprawdz zakazane frazy AI-slop, rytm skladni, poziom konkretu i zgodnosc tonu,
- uruchom open-source detector ensemble i zapisz wynik,
- jesli gate nie przechodzi: redaguj i uruchom ponownie.

Gate:
- `forbidden_phrase_pass` = PASS,
- `specificity_pass` = PASS,
- `voice_authenticity_pass` = PASS,
- `rewrite_loop_pass` = PASS,
- `detector_ensemble_pass` traktuj jako advisory (nie jest jedynym hard fail).

### Step 7f: Context/evidence gate (obowiazkowy)
Dzialania:
- uruchom `execution/check_workflow_context.py`,
- sprawdz komplet `research_evidence_manifest.json` oraz zgodnosc `run_context.md` (skills + data_mode).

Gate:
- `evidence_provenance_pass` = PASS,
- `skills_policy_pass` = PASS.

### Step 8: QA wielowarstwowe + rewrite
Dzialania:
- oceń draft wg 5 kategorii (0-20 kazda):
  - intent_fit,
  - depth_uniqueness,
  - factual_accuracy,
  - on_page_seo,
  - readability_copy,
- wykonaj mandatory checks:
  - E-E-A-T metadata readiness,
  - source freshness rule,
  - snippet/AI extraction readiness,
  - structured data consistency (jesli schema planowana),
  - company-profile alignment (uslugi, CTA, link range),
- wypisz critical failures,
- popraw tekst bez tworzenia kolejnych finalnych wersji pliku; pracujesz na jednym drafcie roboczym,
- jesli gate nie przechodzi: wracaj do poprawki i powtarzaj Step 8 iteracyjnie (max 5 iteracji) do PASS.
- przy problemach z sensem tekstu nie \"latasz\" pojedynczych fraz; przepisujesz akapit lub kolejnosc argumentu.

Output:
- zaktualizowane `article_draft_v2.md`,
- zaktualizowane `editorial_review.md`,
- raporty machine QA jako pliki tymczasowe.

Gate (hard):
- total >= 85/100,
- `critical_failures` = empty,
- mandatory checks = PASS.
- source of truth dla gate'ow: `quality_gate.json` + zatwierdzone `editorial_review.md`.
- machine hard gates = PASS:
  - `polish_title_naturalness_pass`,
  - `polish_collocation_pass`,
  - `polish_punctuation_pass`,
  - `polish_diacritics_pass`,
  - `polish_grammar_pass`,
  - `polish_fluency_ml_pass`,
  - `structure_variance_pass_v2`,
  - `semantic_rewrite_pass_v2`,
  - `forbidden_phrase_pass`,
  - `specificity_pass`,
  - `voice_authenticity_pass`,
  - `rewrite_loop_pass`,
  - `evidence_provenance_pass`,
  - `skills_policy_pass`,
  - `hard_block_export_pass`.

### Step 9: Export final article to Google Docs
Dzialania:
- wyeksportuj `article_draft_v2.md` do Google Docs,
- eksportuj jako rich text (naglowki/listy/linki), a nie surowy Markdown,
- po sukcesie zapisz lokalny `final_output.md`,
- wyczysc pliki robocze i zostaw tylko minimalny zestaw finalnych artefaktow,
- link do Google Docs zwroc w odpowiedzi agenta zamiast zapisywac osobny plik z URL.

Output:
- komunikat terminalowy:
  - `ARTYKUL GOTOWY: <doc_url>`

Gate:
- `doc_url` dziala i prowadzi do finalnego dokumentu.

## 7. Writing constraints (obowiazkowe)
1. Start od user need i problemu, nie od historii firmy.
2. Pierwsze 120-180 slow: jasno "dla kogo" i "co dostanie".
3. Kazda sekcja odpowiada na konkretne pytanie usera.
4. Unikaj lania wody i fillerow AI.
5. Uzywaj konkretow: liczby, kroki, przykłady, checklisty.
6. CTA dopasowany do etapu lejka i intencji.
7. Przy local intent: uwzglednij lokalny kontekst i trust signals.
8. Dodaj czytelne answer-first fragmenty pod kluczowymi naglowkami.
9. Nie blokuj przypadkowo snippet extraction (chyba ze to celowa decyzja).
10. Unikaj AI-slop:
    - nie buduj calego tekstu na szablonie tych samych otwarc zdan,
    - ogranicz puste laczniki i ogolniki bez tresci,
    - stosuj umiarkowany hedging przy twierdzeniach nieabsolutnych (np. \"moze\", \"zwykle\", \"w wielu przypadkach\"),
    - dodaj co najmniej 2 konkretne elementy osadzenia: lokalny przyklad, ograniczenie tezy, praktyczna obserwacja,
    - nie ograniczaj redakcji do podmiany synonimow; przepisuj sens na poziomie calego fragmentu (2-3 zdania naraz),
    - kiedy to poprawia flow, zmieniaj kolejnosc argumentow/list (unikaj stalego schematu A-B-C).
11. Jesli zdanie brzmi dziwnie po przeczytaniu na glos, traktuj to jako bug copy i przepisz je od zera.
12. Nie uzywaj pseudo-obrazowych konstrukcji bez sensu logicznego (np. metafor, ktore nic nie wyjasniaja).

## 7b. Adaptive length policy (2026)
1. Nie ma oficjalnego \"ideal word count\" od Google - dlugosc ma wynikać z pelnego pokrycia intencji.
2. Ustal zakres na podstawie SERP:
   - oblicz mediane i p75 dlugosci Top10,
   - ustaw `word_count_min` blisko mediany i `word_count_max` blisko p75/p90.
3. Domyslne zakresy startowe:
   - local service: 900-1800,
   - informational deep-dive: 1400-3000,
   - comparison/commercial: 1200-2600,
   - pillar/definitive: 2500-4500.
4. Priorytet: kompletna odpowiedz + czytelnosc + unikalna wartosc, nie \"dobijanie\" slow.

## 8. QA scoring framework (100 pkt)
- Intent fit: 0-20
- Depth & uniqueness: 0-20
- Factual accuracy: 0-20
- On-page SEO: 0-20
- Readability & copy quality: 0-20

Krytyczne fail conditions (dowolne = blokada):
1. Niezweryfikowane twierdzenia merytoryczne.
2. Tresc sprzeczna z intencja zapytania.
3. Brak unikalnej wartosci (parafraza konkurencji).
4. Agresywne keyword stuffing.
5. Brak zgodnosci z wymaganym CTA/business goal.
6. Brak E-E-A-T metadata (autor, data aktualizacji, zrodla).
7. Stare lub niewiarygodne zrodla dla kluczowych tez.
8. Bledne ustawienia snippet controls blokujace zamierzona widocznosc.
9. Linki/CTA niezgodne z aktywnym profilem firmy.

## 9. Acceptance criteria (v1)
Artykul jest "publish-ready" tylko gdy:
1. Ma komplet minimalnych artefaktow roboczych potrzebnych do walidacji.
2. Wszystkie hard gates w `quality_gate.json` sa na `PASS`.
3. `editorial_review.md` ma `logic_pass: PASS`, `post_machine_qa_revision_completed: yes` i `final_decision: approved`.
4. Artykul jest poprawnie wyeksportowany do Google Docs.
5. Po eksporcie zostaja tylko `article_research_pack.md` i `final_output.md`.

## 10. Pilot walidacyjny (obowiazkowy)
Cel: przetestowac workflow na realnym temacie lokalnym.

Temat pilota:
- `EMS Niepolomice` (local service).

Spodziewane wyniki pilota:
1. Poprawna klasyfikacja local intent.
2. Sekcja lokalna i realistyczny CTA.
3. Fact bank z lokalnym kontekstem i wiarygodnymi zrodlami.
4. QA >= 85/100.

Po pilocie:
- wypelnij "Lessons learned" i zaktualizuj SOP jesli potrzebne.

## 11. Narzedzia i integracje
MVP:
- Google Search manual review,
- Google Trends,
- Google Ads Keyword Planner,
- AI assistant do draftu/rewrite.
- LanguageTool (lokalnie przez `language-tool-python` + Java) do automatycznej korekty PL,
- pre-trained Polish LM signal (pseudo-perplexity) przez `execution/check_polish_fluency_ml.py`,
- Hugging Face open-source text detector models (lokalnie) do walidacji `detector_ensemble_pass`,
- Rich Results Test (walidacja schema, recznie),
- Google Docs + Drive API (eksport finalnych artefaktow).

Skalowanie:
- DataForSEO API,
- Semrush API,
- ewentualnie Ahrefs API (zaleznie od dostepnosci planu).
- Google Search Console + PageSpeed Insights API (gdy workflow bedzie rozszerzony o etap publikacji i audyt).

## 12. Company context profiles (single company variable)
- Wszystkie artykuly musza wskazywac `company` (wpis naturalny), mapowany do:
  - `Agentic Articles/docs/company_context_profiles.md`
- Company profile definiuje:
  - uslugi i URL-e dozwolone do linkowania,
  - min/max linkow uslugowych,
  - CTA per funnel stage,
  - claimy zakazane,
  - brand voice dla tej firmy.
- Jesli firma nie jest dopasowana jednoznacznie, proces wraca do Step 1.

## 13. Definicje gotowosci
Definition of Ready (DoR):
- `article_brief.md` kompletny,
- `article_research_pack.md` ma wypelniona sekcje Intent Map,
- `research_evidence_manifest.json` spelnia minimum dataset i Evidence Contract,
- firma dopasowana do jednego profilu,
- source freshness policy ustawione,
- `run_context.md` ma `data_mode: external_only` i komplet skills.
- wymagane skills istnieja lokalnie w `./skills/<skill>/SKILL.md`:
  - `content-strategy`
  - `copywriting`
  - `copy-editing`
  - `seo-audit`
  - `schema-markup`
  - `ai-seo`

Definition of Done (DoD):
- artefakty 1-6 gotowe,
- QA + review zaliczone,
- finalny artykul wyeksportowany do Google Docs,
- skrypt export zwrocil komunikat `ARTYKUL GOTOWY` z poprawnym linkiem.
