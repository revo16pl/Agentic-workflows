# qa_report.md

## 1. Hard Gate (must pass)
- [x] Total score >= 85/100
- [x] Critical failures = 0
- [x] final_decision = approved (agent QA)
- [x] publish_ready status = Ready_for_manual_review or Approved
- [x] E-E-A-T metadata complete (author/bio/updated date/sources)
- [x] LLM/snippet readiness checks completed
- [x] Structured data reviewed and valid (if used)
- [x] Company alignment checks completed
- [x] Polish language validation passed (diacritics + grammar)
- [x] Humanization validation passed (style + detector ensemble)

## 2. Scoring (5 x 20)

### A. Intent fit (0-20)
Score (0-20): 19
Komentarz: Artykuł odpowiada na intencję informacyjną, zawiera kontekst lokalny i miękkie przejście do konsultacji.

### B. Depth & uniqueness (0-20)
Score (0-20): 18
Komentarz: Jest praktyczny plan 4-8 tygodni i sekcja ograniczeń, co wyróżnia treść na tle generycznych list "zalet".

### C. Factual accuracy (0-20)
Score (0-20): 19
Komentarz: Kluczowe tezy podparte badaniami WB-EMS, FDA i WHO; brak agresywnych, nieudokumentowanych claimów.

### D. On-page SEO (0-20)
Score (0-20): 18
Komentarz: Logiczna struktura H2/H3, meta title + meta description, naturalne pokrycie klastra fraz i linkowanie wewnętrzne.

### E. Readability & copy quality (0-20)
Score (0-20): 19
Komentarz: Dobry rytm, konkret, prosty język, ton "koleżanka ekspertka", brak AI-fillerów.

### F. Mandatory non-scored checks (must pass)
- [x] Source freshness: statystyki i dane operacyjne mają <= 24 miesiące (chyba że uzasadnione)
- [x] Answer-first blocks: kluczowe H2/H3 mają krótkie odpowiedzi 40-80 słów
- [x] E-E-A-T signals gotowe do publikacji (author line, credentials/proof points, updated date)
- [x] Structured data jest zgodne z treścią widoczną na stronie
- [x] Brak przypadkowych blokad dla AI/Search snippet extraction
- [x] Linki usługowe są zgodne z dopasowanym profilem firmy (min/max i URL-e)
- [x] CTA jest zgodny z funnel stage i profilem firmy
- [x] Human-quality pass: brak monotonnego rytmu, brak nadmiaru szablonowych łączników, jest naturalna zmienność składni
- [x] Semantic rewrite pass: redakcja była na poziomie sensu/fragmentów (nie sam "word swap") i poprawiła przepływ argumentacji
- [x] Keyword coverage pass: primary + secondary + entities pokryte naturalnie (bez stuffing)
- [x] Length strategy pass: długość zgodna z brief (`word_count_min`/`word_count_max`) i intent/SERP
- [x] SEO on-page pass: title/H1/H2/meta/internal links zgodne z blueprint
- [x] Polish diacritics pass: tekst zawiera poprawne polskie znaki (ą, ć, ę, ł, ń, ó, ś, ż, ź)
- [x] Polish grammar pass: automatyczna walidacja gramatyki/spellingu zaliczona
- [x] Forbidden phrase pass: brak zakazanych fraz AI-slop
- [x] Structure variance pass: zróżnicowana składnia i brak monotonnego rytmu
- [x] Specificity pass: tekst zawiera konkrety (liczby, przykłady, osadzenie lokalne)
- [x] Voice authenticity pass: ton zgodny z profilem firmy, niski poziom korpo-żargonu
- [x] Detector ensemble pass: open-source detector ensemble nie flaguje tekstu jako wysokiego ryzyka AI
- [x] Rewrite loop pass: po wykryciu FAIL wykonano iterację redakcyjną i ponowną walidację

Wynik:
- [x] PASS
- [ ] FAIL

## 3. Critical Failures (dowolny = fail)
- [ ] Niezweryfikowane twierdzenia merytoryczne
- [ ] Niezgodność z dominującą intencją
- [ ] Brak unikalnej wartości
- [ ] Keyword stuffing / nienaturalne nasycenie fraz
- [ ] Niezgodność z celem biznesowym lub CTA
- [ ] Ryzyko prawne/compliance bez eskalacji
- [ ] Nieaktualne lub niewiarygodne źródła w kluczowych tezach
- [ ] Blokada snippet/AI extraction przez błędne ustawienia meta
- [ ] Linkowanie do usług spoza aktywnego profilu firmy

## 4. Score Summary
- intent_fit_score: 19
- depth_uniqueness_score: 18
- factual_accuracy_score: 19
- on_page_seo_score: 18
- readability_copy_score: 19
- total_score: 93

## 5. Decyzja
- final_decision: approved
- owner: revo
- review_date: 2026-03-01
- iteration_count: 2
- max_iterations: 3

## 5b. Machine gates (required by validator)
- human_quality_pass: PASS
- semantic_rewrite_pass: PASS
- keyword_coverage_pass: PASS
- internal_linking_pass: PASS
- length_strategy_pass: PASS
- seo_on_page_pass: PASS
- polish_diacritics_pass: PASS
- polish_grammar_pass: PASS
- forbidden_phrase_pass: PASS
- structure_variance_pass: PASS
- specificity_pass: PASS
- voice_authenticity_pass: PASS
- detector_ensemble_pass: PASS
- rewrite_loop_pass: PASS

## 6. Lista poprawek (jesli revise)
1. Usunięto szablonowe frazy i zwiększono zróżnicowanie składni.
2. Doprecyzowano sekcję bezpieczeństwa i oczekiwań wobec efektów.
3. Uporządkowano CTA i linkowanie zgodnie z profilem firmy.

## 7. JSON block (opcjonalnie do automatyzacji)
```json
{
  "intent_fit_score": 19,
  "depth_uniqueness_score": 18,
  "factual_accuracy_score": 19,
  "on_page_seo_score": 18,
  "readability_copy_score": 19,
  "mandatory_checks_passed": true,
  "critical_failures": [],
  "final_decision": "approved"
}
```
