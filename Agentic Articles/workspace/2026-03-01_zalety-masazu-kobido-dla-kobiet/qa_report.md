# Template: article_qa_checklist.md

> Uzyj tego dokumentu po przygotowaniu `article_draft_v1.md`. Publikacja dozwolona dopiero po spelnieniu hard gate.
> Uwaga: checklista sluzy do review czlowieka; ostateczny PASS/FAIL machine gates jest liczony w `quality_gate.json`.

## 1. Hard Gate (must pass)
- [ ] Total score >= 85/100
- [ ] Critical failures = 0
- [ ] final_decision = approved (agent QA)
- [ ] publish_ready status = Ready_for_manual_review or Approved
- [ ] E-E-A-T metadata complete (author/bio/updated date/sources)
- [ ] LLM/snippet readiness checks completed
- [ ] Structured data reviewed and valid (if used)
- [ ] Company alignment checks completed
- [ ] Polish language validation passed (diacritics + grammar)
- [ ] Humanization validation passed (style + detector ensemble)
- [ ] quality_gate.json exists and all hard gates = PASS

## 2. Scoring (5 x 20)

### A. Intent fit (0-20)
Sprawdz:
- [ ] Artykul odpowiada dominujacej intencji z sekcji `Intent Map` w `article_research_pack.md`
- [ ] Format tresci pasuje do zapytania (guide/comparison/local)
- [ ] CTA jest adekwatny do etapu lejka

Score (0-20):
Komentarz:

### B. Depth & uniqueness (0-20)
Sprawdz:
- [ ] Jest unikalna wartosc (framework, checklista, case, insight)
- [ ] Tresc nie jest parafraza konkurencji
- [ ] Sekcje maja konkret i actionable guidance

Score (0-20):
Komentarz:

### C. Factual accuracy (0-20)
Sprawdz:
- [ ] Kluczowe tezy maja potwierdzenie w sekcji `Fact Bank` w `article_research_pack.md`
- [ ] Brak niesprawdzonych danych/liczb
- [ ] Zrodla sa aktualne i wiarygodne

Score (0-20):
Komentarz:

### D. On-page SEO (0-20)
Sprawdz:
- [ ] H1/H2/H3 logiczne i zgodne z blueprint
- [ ] Primary keyword obecny naturalnie (bez stuffing)
- [ ] Secondary keywords i entities rozmieszczone naturalnie
- [ ] Meta title/meta description gotowe
- [ ] Internal linking plan gotowy
- [ ] Snippet controls sa celowe (brak przypadkowego `nosnippet`/za niskiego `max-snippet`)

Score (0-20):
Komentarz:

### E. Readability & copy quality (0-20)
Sprawdz:
- [ ] Mocny lead (jasny "dla kogo i po co")
- [ ] Krotkie akapity, dobra skanowalnosc
- [ ] Klarowny jezyk i dobra logika argumentacji
- [ ] Brak AI fillerow i powtorzen

Score (0-20):
Komentarz:

### F. Mandatory non-scored checks (must pass)
Sprawdz:
- [ ] Source freshness: statystyki i dane operacyjne maja <= 24 miesiace (chyba ze uzasadnione)
- [ ] Answer-first blocks: kluczowe H2/H3 maja krotkie odpowiedzi 40-80 slow
- [ ] E-E-A-T signals gotowe do publikacji (author line, credentials/proof points, updated date)
- [ ] Structured data jest zgodne z trescia widoczna na stronie
- [ ] Brak przypadkowych blokad dla AI/Search snippet extraction
- [ ] Linki uslugowe sa zgodne z dopasowanym profilem firmy (min/max i URL-e)
- [ ] CTA jest zgodny z funnel stage i profilem firmy
- [ ] Human-quality pass: brak monotonnego rytmu, brak nadmiaru szablonowych lacznikow, jest naturalna zmiennosc skladni
- [ ] Semantic rewrite pass: redakcja byla na poziomie sensu/fragmentow (nie sam \"word swap\") i poprawila przeplyw argumentacji
- [ ] Keyword coverage pass: primary + secondary + entities pokryte naturalnie (bez stuffing)
- [ ] Length strategy pass: dlugosc zgodna z brief (`word_count_min`/`word_count_max`) i intent/SERP
- [ ] SEO on-page pass: title/H1/H2/meta/internal links zgodne z blueprint
- [ ] Polish diacritics pass: tekst zawiera poprawne polskie znaki (ą, ć, ę, ł, ń, ó, ś, ż, ź)
- [ ] Polish grammar pass: automatyczna walidacja gramatyki/spellingu zaliczona
- [ ] Forbidden phrase pass: brak zakazanych fraz AI-slop (np. \"procesowo\")
- [ ] Structure variance pass: zroznicowana skladnia i brak monotonnego rytmu
- [ ] Specificity pass: tekst zawiera konkrety (liczby, przyklady, osadzenie lokalne)
- [ ] Voice authenticity pass: ton zgodny z profilem firmy, niski poziom korpo-zargonu
- [ ] Detector ensemble pass: open-source detector ensemble nie flaguje tekstu jako wysokiego ryzyka AI
- [ ] Rewrite loop pass: jesli jakikolwiek gate FAIL, wykonana iteracja redakcyjna i ponowna walidacja

Wynik:
- [ ] PASS
- [ ] FAIL

## 3. Critical Failures (dowolny = fail)
Zaznacz jesli wystepuje:
- [ ] Niezweryfikowane twierdzenia merytoryczne
- [ ] Niezgodnosc z dominujaca intencja
- [ ] Brak unikalnej wartosci
- [ ] Keyword stuffing / nienaturalne nasycenie fraz
- [ ] Niezgodnosc z celem biznesowym lub CTA
- [ ] Ryzyko prawne/compliance bez eskalacji
- [ ] Nieaktualne lub niewiarygodne zrodla w kluczowych tezach
- [ ] Blokada snippet/AI extraction przez bledne ustawienia meta
- [ ] Linkowanie do uslug spoza aktywnego profilu firmy

## 4. Score Summary
- intent_fit_score: 20
- depth_uniqueness_score: 18
- factual_accuracy_score: 19
- on_page_seo_score: 19
- readability_copy_score: 19
- total_score: 95

## 5. Decyzja
- final_decision: `approved`
- owner: revo
- review_date: YYYY-MM-DD
- iteration_count: 1
- max_iterations: 5

## 5b. Machine gates (required by validator)
- polish_title_naturalness_pass: PASS | FAIL
- polish_collocation_pass: PASS | FAIL
- polish_punctuation_pass: PASS | FAIL
- semantic_rewrite_pass_v2: PASS | FAIL
- polish_diacritics_pass: PASS | FAIL
- polish_grammar_pass: PASS | FAIL
- polish_fluency_ml_pass: PASS | FAIL
- forbidden_phrase_pass: PASS | FAIL
- structure_variance_pass_v2: PASS | FAIL
- specificity_pass: PASS | FAIL
- voice_authenticity_pass: PASS | FAIL
- detector_ensemble_pass: PASS | FAIL (advisory)
- rewrite_loop_pass: PASS | FAIL
- evidence_provenance_pass: PASS | FAIL
- skills_policy_pass: PASS | FAIL
- hard_block_export_pass: PASS | FAIL

## 6. Lista poprawek (jesli revise)
1.
2.
3.

## 7. JSON block (opcjonalnie do automatyzacji)
```json
{
  "intent_fit_score": 20,
  "depth_uniqueness_score": 18,
  "factual_accuracy_score": 19,
  "on_page_seo_score": 19,
  "readability_copy_score": 19,
  "mandatory_checks_passed": true,
  "critical_failures": [],
  "final_decision": "approved"
}
```

- structure_variance_pass: PASS