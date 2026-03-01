# Company Context Profiles (single company variable)

## 1. Purpose
To jest pojedynczy plik konfiguracyjny dla wielu firm.
Jedyna zmienna wybierana w promptcie to `company` (naturalna nazwa firmy).
Brand voice jest zawsze przypisany do firmy i laduje sie automatycznie.

## 2. How to use
1. W promptcie podajesz tylko firme naturalnie, np.:
- "artykul dla studio balans"
- "artykul dla balansu"
- "artykul dla studio masazu"
2. Agent dopasowuje wpis do profilu firmy po aliasach.
3. Po dopasowaniu agent bierze z profilu:
- tone of voice,
- uslugi i linki wewnetrzne,
- CTA,
- ograniczenia i claimy zakazane.

## 3. Matching rules (natural language)
1. Normalizacja wejscia:
- lowercase,
- bez dodatkowych spacji,
- zamiana polskich znakow na podstawowe (np. "masażu" -> "masazu").
2. Match order:
- exact alias match,
- contains match (fraza zawiera alias),
- jesli brak jednoznacznego dopasowania: agent prosi o doprecyzowanie.
3. Jesli alias pasuje do 2 firm, agent nie zgaduje i zatrzymuje sie na pytaniu.

## 4. Universal rules (dla kazdej firmy)
1. Artykul ma wspierac biznes, ale bez nachalnej sprzedazy.
2. Liczba linkow do stron uslugowych wynika z `internal_linking_rules` profilu firmy.
3. Linkuj tylko do stron logicznie powiazanych z intencja i sekcja.
4. Anchor text ma byc naturalny (bez keyword stuffing).
5. CTA musi byc zgodny z funnel stage i profilem firmy.
6. Nie promuj uslug spoza oferty firmy.
7. Przy local intent dodaj lokalny kontekst firmy (obszar dzialania, kontakt, realia lokalne).

## 5. Company profile schema (copy/paste for new company)
```yaml
company: "studio balans"              # nazwa kanoniczna
aliases: ["studio balans", "balans"]  # wpisy naturalne, po ktorych agent ma rozpoznac firme
website_domain: ""
business_type: ""
core_offer_summary: ""
brand_voice:
  name: ""
  narrator: ""
  tone_rules: []
  avoid_rules: []
  sample_lines: []
services:
  - service_name: ""
    service_url: ""
    target_use_cases: []
priority_services_for_content: []
excluded_topics_or_claims: []
ideal_customer_profiles: []
primary_locations: []
trust_signals:
  - ""
default_cta:
  tofu: ""
  mofu: ""
  bofu: ""
internal_linking_rules:
  min_links_to_service_pages: 1
  max_links_to_service_pages: 3
  allow_blog_to_blog_links: true
  allow_external_references: true
conversion_pages:
  booking_page_url: ""
  contact_page_url: ""
legal_compliance_notes: []
```

## 6. Example profile: StudioBalans (first case)
```yaml
company: "studio balans"
aliases:
  - "studio balans"
  - "studiobalans"
  - "balans"
  - "studio masazu"
  - "studio masażu"
  - "studio balansu"
website_domain: "studiobalans.pl"
business_type: "salon masazu, kosmetologii i treningu"
core_offer_summary: "Laczymy pielegnacje ciala, terapie manualne i treningi, zeby klientka czula sie lepiej i wygladala lepiej bez agresywnych obietnic."
brand_voice:
  name: "kolezanka ekspertka"
  narrator: "kobieta do kobiety, doradczyni"
  tone_rules:
    - "przyjaznie, konkretnie, szczerze"
    - "mow w 2. osobie i dawaj praktyczne kroki"
    - "empatia bez lukru, bez pustych obietnic"
  avoid_rules:
    - "moralizowanie i zawstydzanie"
    - "agresywna sprzedaz"
    - "obietnice efektu po 1 zabiegu"
  sample_lines:
    - "Jesli masz napiete plecy po pracy, zacznijmy od prostego planu: najpierw odciazenie, potem wzmacnianie."
    - "Powiem Ci wprost: jeden zabieg moze ulzyc, ale trwaly efekt robi regularnosc i dobrze dobrany trening."
services:
  - service_name: "Trening EMS"
    service_url: "https://studiobalans.pl/uslugi/trening-ems"
    target_use_cases: ["redukcja tkanki tluszczowej", "wzmocnienie po dlugiej przerwie", "powrot do formy"]
  - service_name: "Masaz terapeutyczny"
    service_url: "https://studiobalans.pl/uslugi/masaz-terapeutyczny"
    target_use_cases: ["napiecie karku", "bol plecow", "regeneracja"]
  - service_name: "Kosmetologia"
    service_url: "https://studiobalans.pl/uslugi/kosmetologia"
    target_use_cases: ["pielegnacja skory", "terapie zabiegowe", "plan pielegnacyjny"]
priority_services_for_content: ["Trening EMS", "Masaz terapeutyczny"]
excluded_topics_or_claims:
  - "medyczne diagnozy bez uprawnien"
ideal_customer_profiles:
  - "kobiety 25-45, pracujace glownie siedzaco"
  - "kobiety wracajace do aktywnosci po dluzszej przerwie"
primary_locations: ["Niepolomice", "Wieliczka", "Krakow"]
trust_signals:
  - "indywidualna konsultacja przed planem zabiegowym"
  - "polaczenie ruchu i terapii manualnej"
  - "realistyczne podejscie bez pustych obietnic"
default_cta:
  tofu: "Sprawdz, ktora metoda bedzie dla Ciebie najbezpieczniejsza i najskuteczniejsza."
  mofu: "Umow konsultacje i dobierz plan EMS + regeneracja."
  bofu: "Zarezerwuj pierwsza wizyte online."
internal_linking_rules:
  min_links_to_service_pages: 1
  max_links_to_service_pages: 3
  allow_blog_to_blog_links: true
  allow_external_references: true
conversion_pages:
  booking_page_url: "https://studiobalans.pl/rezerwacja"
  contact_page_url: "https://studiobalans.pl/kontakt"
legal_compliance_notes:
  - "nie uzywac twierdzen medycznych bez podstaw"
  - "przy efektach estetycznych podawac, ze efekty sa indywidualne"
```

## 7. Prompt seed example
"Zrobmy artykul dla studio balans o zaletach treningu EMS."

## 8. QA checks for alignment
- [ ] Czy firma zostala poprawnie dopasowana po aliasach?
- [ ] Czy ton zgadza sie z voice z profilu firmy?
- [ ] Czy wszystkie linki uslugowe pochodza z aktywnego profilu firmy?
- [ ] Czy CTA pasuje do funnel stage i default_cta z profilu?
- [ ] Czy nie ma uslug lub claimow spoza profilu?
