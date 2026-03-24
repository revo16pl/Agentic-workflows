#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from youtube_notes_common import build_segments, parse_transcript_markdown, split_sentences
from youtube_notes_config import TOOL_HINTS


TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-/\.']+")
NON_WORD_RE = re.compile(r"[^a-z0-9 ]+")

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "into", "about", "have", "there", "their",
    "would", "could", "should", "then", "than", "just", "like", "really", "thing", "things", "make",
    "makes", "made", "being", "also", "some", "very", "what", "when", "where", "your", "you", "guys",
    "here", "they", "them", "over", "under", "because", "through", "using", "used", "use", "workflows",
    "workflow", "agentic", "course", "video", "okay", "well", "know", "stuff", "pretty", "little",
}

FILLER_PATTERNS = (
    r"\bsubscribe\b",
    r"\bsmash that like\b",
    r"\bbookmark this\b",
    r"\bif you don't know who i am\b",
    r"\bthank you from the bottom of my heart\b",
    r"\bmaker school\b",
    r"\bmy channel\b",
    r"\bif you guys\b",
    r"\blet's get started\b",
    r"\bwhat i'm going to show you\b",
    r"\bi'm going to cover\b",
    r"\bi'll show you later\b",
    r"\bcheck the link\b",
    r"\bdown in the description\b",
    r"\bplease check out\b",
    r"\bmore generally\b",
)

LEADING_PHRASE_REPLACEMENTS = (
    (r"^(so\s+)?the whole point of (it|this) is to\s+", ""),
    (r"^to make a long story short,\s*", ""),
    (r"^the point that i'm making is\s*", ""),
    (r"^what i mean by [^,]+ is\s*", ""),
    (r"^what i want to do is\s*", ""),
    (r"^another way i want you to think about (this|it) is\s*", ""),
    (r"^rather than thinking about\s+", "Think about "),
    (r"^the idea is (that\s+)?", ""),
    (r"^in practice,\s*", ""),
    (r"^obviously,\s*", ""),
)

AUDIENCE_PHRASES = (
    "you guys",
    "if you think about it",
    "to be clear",
    "in case you didn't know",
    "hopefully it's clear",
)

THEME_RULES = (
    {
        "id": "business_case",
        "title": "Biznesowy sens agentic workflows",
        "section": "key_ideas",
        "keywords": (
            "wealth transfers", "financial means", "revenue", "arbitrage", "river of value",
            "horizontal leverage", "90% of 10,000 roles", "next stage of the economy",
        ),
        "summary": "Agentic workflows to warstwa dźwigni biznesowej, a nie tylko kolejna sztuczka produktywnościowa.",
        "details": (
            "Największa przewaga bierze się z tego, że można przejąć wartość wcześniej niż reszta rynku nauczy się operacyjnie wykorzystywać obecne możliwości modeli.",
            "Lepszy model myślenia to „automatyzacja 90% pracy w wielu rolach” zamiast obsesji na punkcie pełnego zastąpienia jednej roli end-to-end.",
            "Największy efekt daje dźwignia horyzontalna: wiele małych odciążeń rozłożonych szeroko po organizacji.",
            "Okno arbitrażu nie będzie trwało długo, bo kompetencje rynku będą doganiać realne możliwości modeli.",
        ),
    },
    {
        "id": "overhang",
        "title": "Overhang AI",
        "section": "key_ideas",
        "keywords": (
            "overhang", "copy and paste tools", "low bandwidth", "external sort of third party thing",
        ),
        "summary": "Overhang AI to luka między tym, co modele już potrafią, a tym, jak mało osób umie to dziś wykorzystać operacyjnie.",
        "details": (
            "Większość zespołów nadal używa modeli jak lepszych narzędzi copy/paste zamiast włączać je w realne pętle wykonawcze.",
            "Wąskim gardłem bardzo często nie jest inteligencja modelu, tylko ubogi interfejs człowiek -> model -> systemy.",
            "Prawdziwa dźwignia zaczyna się wtedy, gdy AI staje się częścią systemu operacyjnego firmy, a nie zewnętrznym dodatkiem.",
        ),
    },
    {
        "id": "agents_vs_chatbots",
        "title": "Agenci vs chatboty",
        "section": "key_ideas",
        "keywords": (
            "agent is not a chatbot", "dynamic knowledge", "dynamic action", "documents", "chats",
            "chat bots", "chatbot", "the chat is just like the app",
        ),
        "summary": "Chatbot jest interfejsem wiedzy; agent zaczyna być naprawdę użyteczny dopiero wtedy, gdy może działać przez narzędzia i utrzymywać ciąg pracy w czasie.",
        "details": (
            "Drabinka `docs -> chats -> agents` dobrze pokazuje przejście od statycznej wiedzy do systemów wykonawczych.",
            "Chat jest tylko powłoką. Agent to właściwy system działający wewnątrz tej powłoki.",
            "Dynamiczna wiedza jest przydatna, ale realną wartość biznesową daje dopiero dynamiczne działanie.",
        ),
    },
    {
        "id": "planning",
        "title": "Planowanie",
        "section": "methods",
        "keywords": (
            "planning", "goal decomposition", "dependencies", "sequence", "error bars",
            "high-level objective", "highle objective", "plan when things change",
        ),
        "summary": "Planowanie to rozbijanie celu na kroki, zależności i sensowną kolejność wykonania.",
        "details": (
            "Małe błędy planowania narastają później kaskadowo, dlatego największą wartość człowiek zwykle wnosi właśnie na etapie planu.",
            "Dobre planowanie to nie tylko lista kroków, ale też rozpoznanie zależności i korekta planu, gdy zmienia się rzeczywistość.",
            "Frameworki pomagają między innymi dlatego, że zawężają margines błędu już na starcie.",
        ),
    },
    {
        "id": "tools",
        "title": "Narzędzia",
        "section": "methods",
        "keywords": (
            "tools", "tool use", "api", "executing code", "database", "browse the web", "agents hands",
        ),
        "summary": "Narzędzia są rękami modelu.",
        "details": (
            "To właśnie tool use zamienia model językowy w system, który może realnie wpływać na świat zewnętrzny.",
            "Najważniejsze kategorie narzędzi to API, wykonywanie kodu, bazy danych i przeglądanie zasobów.",
            "Niezawodność biznesowa bierze się ze standaryzacji korzystania z narzędzi, a nie z liczenia na swobodną improwizację modelu.",
        ),
    },
    {
        "id": "memory",
        "title": "Pamięć",
        "section": "methods",
        "keywords": (
            "memory", "short-term", "midterm", "long-term", "retain and recall information",
        ),
        "summary": "Pamięć pozwala agentowi utrzymywać stan między krokami zamiast traktować każdą interakcję jak świeży chat.",
        "details": (
            "Pamięć krótkoterminowa, pośrednia i długoterminowa pełnią w workflow różne role.",
            "Zaśmiecenie kontekstu zabija jakość odzyskiwania informacji, więc projekt pamięci jest częścią projektu całego systemu.",
            "Duża część pozornej „słabości” modeli wynika tak naprawdę z zatkanego i chaotycznego kontekstu.",
        ),
    },
    {
        "id": "reflection",
        "title": "Refleksja i review",
        "section": "methods",
        "keywords": (
            "reflection", "evaluate and correct", "corrects its own work", "review with fresh eyes",
            "reviewer sub agent",
        ),
        "summary": "Reflection to pętla review, która łapie problemy jakości zanim zdążą wrosnąć w workflow.",
        "details": (
            "Reviewer z czystym kontekstem widzi problemy, których główny agent może już nie zauważać przez przeciążenie własnymi decyzjami.",
            "Reflection jest najważniejsze po napisaniu skryptów, spięciu narzędzi i zmianie założeń.",
            "Gdy workflow dotyka realnych systemów, pętla review przestaje być dodatkiem, a staje się obowiązkowym bezpiecznikiem.",
        ),
    },
    {
        "id": "orchestration",
        "title": "Orkiestracja",
        "section": "methods",
        "keywords": (
            "orchestration", "coordinate multiple agents", "complex workflows", "main agent",
            "parent agent", "sub agents work in parallel",
        ),
        "summary": "Orkiestracja to warstwa, która decyduje co się uruchamia, w jakiej kolejności i z jakim zakresem odpowiedzialności.",
        "details": (
            "Orkiestracja rozdziela pracę między planowanie, wykonanie, review i konsolidację wyników.",
            "Równoległość ma sens tylko wtedy, gdy realnie skraca czas wykonania, a nie dokłada zbędną ceremonię.",
            "Parent agent powinien koordynować, a nie bezmyślnie delegować wszystko dalej.",
        ),
    },
    {
        "id": "do_framework",
        "title": "Directive / Orchestration / Execution",
        "section": "methods",
        "keywords": (
            "directive orchestration execution", "directives", "execution scripts", "orchestrator",
            "directive", "execution",
        ),
        "summary": "Rozdzielenie warstw directive, orchestration i execution pozwala zamienić elastyczne modele w bardziej przewidywalne systemy biznesowe.",
        "details": (
            "Directive definiuje, jak ma wyglądać dobry rezultat i jakie są zasady gry.",
            "Orchestration decyduje, jak praca ma przepłynąć przez system.",
            "Execution scripts przechowują te elementy, które powinny być deterministyczne i nie zależeć od improwizacji LLM-a.",
            "To rozdzielenie obniża error rate, bo ogranicza miejsca, w których elastyczność modelu może psuć niezawodność.",
        ),
    },
    {
        "id": "skills",
        "title": "Skills",
        "section": "methods",
        "keywords": (
            "skills", "claude skills", "front matter", "skill matching", "markdown files", "skill spec",
        ),
        "summary": "Skills to SOP-y dla agentów opakowane w format, który model potrafi niezawodnie rozpoznać i załadować.",
        "details": (
            "Skill to w praktyce zestaw instrukcji operacyjnych zapisanych w markdownzie.",
            "Front matter istnieje po to, żeby wykrywanie było tanie, a ładowanie kontekstu selektywne.",
            "Progressive disclosure jest kluczowe: pełną treść skilla ładujesz dopiero wtedy, gdy zadanie rzeczywiście go wymaga.",
        ),
    },
    {
        "id": "mcp",
        "title": "MCP i integracja narzędzi",
        "section": "methods",
        "keywords": (
            "model context protocol", "mcp", "external tools", "tool integration", "protocol",
        ),
        "summary": "MCP to ustandaryzowany most między modelami a zewnętrznymi narzędziami i zasobami.",
        "details": (
            "Sednem MCP nie jest nowość, tylko standaryzacja dostępu do narzędzi.",
            "Sama obsługa MCP nie wystarczy, bo jakość konkretnych serwerów i tooli nadal bardzo się różni.",
            "Dobry workflow zależy od świadomego wyboru stabilnych narzędzi MCP i znajomości ich punktów awarii.",
        ),
    },
    {
        "id": "testing",
        "title": "Testowanie i review",
        "section": "practical",
        "keywords": (
            "test", "validate", "review", "reviewer", "document sub agent", "quality",
            "fresh eyes", "double check",
        ),
        "summary": "Najpierw test na małej próbce, potem review z czystym kontekstem, a dopiero na końcu skala.",
        "details": (
            "Reviewer agent jest przydatny, bo ocenia wynik bez dziedziczenia ślepych punktów po agencie, który budował rozwiązanie.",
            "Document agent pilnuje zgodności między dyrektywami a skryptami po poprawkach i zmianach self-annealing.",
            "Pomijanie walidacji zwykle tylko przesuwa koszt debugowania na później i go zwiększa.",
        ),
    },
    {
        "id": "self_healing",
        "title": "Workflowy self-annealing",
        "section": "practical",
        "keywords": (
            "self annealing", "heal themselves", "patch the skill", "update the directive",
            "improve constantly",
        ),
        "summary": "Mocny workflow powinien uczyć się na błędach i sam się wzmacniać, zamiast powtarzać w kółko ten sam problem.",
        "details": (
            "Poprawienie samego skryptu bez aktualizacji dyrektywy tworzy drift między dokumentacją a rzeczywistym zachowaniem systemu.",
            "Workflow rośnie w siłę wtedy, gdy porażki zamieniają się w poprawki zarówno kodu, jak i instrukcji.",
            "Self-healing nie polega na „teatrze autonomii”, tylko na szybszej iteracji po realnych edge case'ach.",
        ),
    },
    {
        "id": "cloud",
        "title": "Chmura, webhooki i schedulowanie",
        "section": "practical",
        "keywords": (
            "web hooks", "schedule triggers", "move out of the ide", "into the cloud", "modal",
            "webhook",
        ),
        "summary": "Lokalny prototyp to dopiero początek; prawdziwa dźwignia pojawia się wtedy, gdy workflow można wywołać na żądanie albo według harmonogramu.",
        "details": (
            "Webhooki zamieniają workflow w usługę, a nie ręczny rytuał odpalany z IDE.",
            "Schedulowanie zaczyna mieć znaczenie, gdy workflow rozwiązuje powtarzalne zadanie biznesowe.",
            "Wdrożenie do chmury to krok, który zamienia efektowne demo w system operacyjny dla realnej pracy.",
        ),
    },
    {
        "id": "subagents",
        "title": "Subagenci i praca równoległa",
        "section": "practical",
        "keywords": (
            "sub agent", "sub agents", "parallelization", "parallel", "least privilege",
            "reviewer sub agent", "document sub agent",
        ),
        "summary": "Subagenci mają sens wtedy, gdy czyszczą kontekst, poprawiają jakość review albo realnie skracają czas wykonania.",
        "details": (
            "Najlepsze zastosowania to wyspecjalizowane review, wyrównanie dokumentacji i równoległe zadania poboczne.",
            "Nie warto odpalać subagentów do każdego drobiazgu, bo narzut i opóźnienie są realne.",
            "Zasada least privilege jest kluczowa, bo autonomia zwielokrotnia nie tylko szybkość, ale też skutki błędów.",
        ),
    },
)

EXAMPLE_RULES = (
    {
        "id": "meal_prep",
        "keywords": ("meal prep", "downtown vancouver", "3500 calories", "200 grams of protein"),
        "text": "Cold outreach do firm meal-prep: agent sam znajduje lokalne firmy, wyszukuje kontakt, buduje wiadomość zgodną z wymaganiami i wysyła serię maili bez ręcznego przechodzenia przez strony.",
    },
    {
        "id": "lead_scraping",
        "keywords": ("linkedin sales navigator", "hvac owners", "google sheet", "200 hvac"),
        "text": "Lead scraping jako workflow: agent uruchamia test scrape, sprawdza jakość dopasowania, koryguje filtry i dopiero potem robi pełne pobranie oraz eksport wyników do Google Sheets.",
    },
    {
        "id": "thumbnail",
        "keywords": ("thumbnail", "john ham", "variants", "face"),
        "text": "Generator miniaturek: agent bierze obraz referencyjny, łączy go z dodatkowymi assetami, generuje kilka wariantów i zostawia użytkownikowi wybór najlepszego rezultatu zamiast pojedynczego strzału.",
    },
    {
        "id": "website",
        "keywords": ("website builder", "netlify", "prospects", "highquality websites"),
        "text": "Website builder jako asset sprzedażowy: agent tworzy szybkie strony dla leadów lub klientów i od razu publikuje je w hostingu, dzięki czemu wartość jest dostarczana szybciej niż w klasycznym modelu usługowym.",
    },
    {
        "id": "reviewer",
        "keywords": ("reviewer sub agent", "document sub agent", "fresh eyes"),
        "text": "Reviewer i document subagent: jeden agent ocenia jakość skryptów z czystym kontekstem, a drugi aktualizuje dyrektywy, żeby dokumentacja nie rozjechała się z wykonaniem.",
    },
    {
        "id": "webhooks",
        "keywords": ("web hooks", "schedule triggers", "modal", "webhook url"),
        "text": "Przeniesienie workflowu do chmury: webhook daje punkt wejścia do zewnętrznych systemów, a harmonogram zamienia jednorazowy eksperyment w proces uruchamiany automatycznie.",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate practical notes from a YouTube transcript.")
    parser.add_argument("transcript_path", help="Path to transcript markdown file.")
    parser.add_argument("--notes-profile", default="auto", choices=["auto", "short", "standard", "deep"])
    parser.add_argument("--output", default=None, help="Optional custom output path.")
    parser.add_argument("--language-policy", default=None, help="Deprecated (no-op).")
    parser.add_argument("--evidence-mode", default=None, help="Deprecated (no-op).")
    parser.add_argument("--context-output", default=None, help="Deprecated (no-op).")
    return parser.parse_args()


def notes_output_path(transcript_path: str, explicit_output: str | None) -> Path:
    if explicit_output:
        return Path(explicit_output)
    base = Path(transcript_path)
    if base.name.startswith("Transcript - "):
        return base.with_name("Notes - " + base.name[len("Transcript - "):])
    return base.with_name(f"Notes - {base.stem}.md")


def _detail_limits(profile_name: str, duration_minutes: int) -> dict[str, int]:
    if profile_name == "short":
        return {"key_ideas": 4, "methods": 5, "practical": 6, "keep": 5, "examples": 3}
    if profile_name == "deep":
        return {"key_ideas": 8, "methods": 10, "practical": 10, "keep": 8, "examples": 6}
    if profile_name == "auto" and duration_minutes >= 240:
        return {"key_ideas": 8, "methods": 10, "practical": 10, "keep": 8, "examples": 6}
    return {"key_ideas": 5, "methods": 7, "practical": 7, "keep": 6, "examples": 4}


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOPWORDS]


def _sentence_score(sentences: list[str]) -> dict[str, float]:
    freq: dict[str, int] = {}
    for sentence in sentences:
        for token in set(_tokenize(sentence)):
            freq[token] = freq.get(token, 0) + 1

    scores: dict[str, float] = {}
    for sentence in sentences:
        tokens = _tokenize(sentence)
        if not tokens:
            scores[sentence] = 0.0
            continue
        scores[sentence] = sum(freq.get(token, 0) for token in tokens) / (len(tokens) ** 0.5)
    return scores


def _sentence_key(sentence: str) -> str:
    return re.sub(r"\s+", " ", NON_WORD_RE.sub(" ", sentence.lower())).strip()


def _dedupe(sentences: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for sentence in sentences:
        key = _sentence_key(sentence)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(sentence)
    return result


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _select_diverse(sentences: list[str], limit: int) -> list[str]:
    unique = _dedupe(sentences)
    scores = _sentence_score(unique)
    ranked = sorted(unique, key=lambda item: scores.get(item, 0.0), reverse=True)

    selected: list[str] = []
    token_sets: list[set[str]] = []
    for sentence in ranked:
        token_set = set(_tokenize(sentence))
        if token_sets and max(_jaccard(token_set, existing) for existing in token_sets) > 0.72:
            continue
        selected.append(sentence)
        token_sets.append(token_set)
        if len(selected) >= limit:
            break
    return selected


def _strip_leading_phrases(text: str) -> str:
    updated = text.strip()
    for pattern, replacement in LEADING_PHRASE_REPLACEMENTS:
        updated = re.sub(pattern, replacement, updated, flags=re.I)
    return updated.strip(" -,:;")


def _clean_sentence(sentence: str) -> str | None:
    text = re.sub(r"\s+", " ", sentence).strip()
    if len(text.split()) < 7:
        return None

    lower = text.lower()
    if any(re.search(pattern, lower) for pattern in FILLER_PATTERNS):
        return None

    text = _strip_leading_phrases(text)
    lower = text.lower()
    if any(phrase in lower for phrase in AUDIENCE_PHRASES):
        return None
    if lower.startswith(("hey,", "okay,", "so,", "well,", "now,", "um,", "uh,")):
        text = re.sub(r"^(hey|okay|so|well|now|um|uh)[,\s]+", "", text, flags=re.I)

    text = re.sub(r"\bguys\b", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" -,:;")
    if len(text.split()) < 7:
        return None
    if text.lower().startswith(("i'm going to", "i want to", "i'll show", "please", "thank you")):
        return None
    if not re.search(r"[.!?]$", text):
        text += "."
    return text[0].upper() + text[1:]


def _collect_note_worthy_sentences(transcript_data: dict[str, object]) -> list[str]:
    sentences: list[str] = []
    for entry in transcript_data["entries"]:
        for sentence in split_sentences(entry.text):
            cleaned = _clean_sentence(sentence)
            if cleaned:
                sentences.append(cleaned)
    return _dedupe(sentences)


def _theme_matches(sentence: str, keywords: tuple[str, ...]) -> bool:
    lower = sentence.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def _collect_theme_sentences(sentences: list[str]) -> dict[str, list[str]]:
    themed: dict[str, list[str]] = {rule["id"]: [] for rule in THEME_RULES}
    for sentence in sentences:
        for rule in THEME_RULES:
            if _theme_matches(sentence, rule["keywords"]):
                themed[rule["id"]].append(sentence)
    return {key: _dedupe(value) for key, value in themed.items() if value}


def _top_theme_ids(theme_map: dict[str, list[str]], section: str, limit: int) -> list[str]:
    candidates: list[tuple[int, int, str]] = []
    for index, rule in enumerate(THEME_RULES):
        if rule["section"] != section:
            continue
        size = len(theme_map.get(rule["id"], []))
        if size:
            candidates.append((size, -index, rule["id"]))
    candidates.sort(reverse=True)
    return [theme_id for _, _, theme_id in candidates[:limit]]


def _theme_rule(theme_id: str) -> dict[str, object]:
    for rule in THEME_RULES:
        if rule["id"] == theme_id:
            return rule
    raise KeyError(theme_id)


def _detect_tools(text: str) -> list[str]:
    tools: list[str] = []
    for tool in TOOL_HINTS:
        if re.search(re.escape(tool), text, flags=re.I) and tool not in tools:
            tools.append(tool)
    return tools


def _detect_examples(text: str) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    for rule in EXAMPLE_RULES:
        if any(keyword.lower() in lower for keyword in rule["keywords"]):
            found.append(rule["text"])
    return found


def _format_bullets(sentences: list[str]) -> str:
    return "\n".join(f"- {sentence}" for sentence in sentences)


def _build_key_ideas(theme_map: dict[str, list[str]], fallback_sentences: list[str], limit: int) -> str:
    bullets: list[str] = []
    used_theme_ids: set[str] = set()
    for theme_id in _top_theme_ids(theme_map, "key_ideas", limit):
        rule = _theme_rule(theme_id)
        bullets.append(f"- **{rule['title']}:** {rule['summary']}")
        used_theme_ids.add(theme_id)

    for section in ("methods", "practical"):
        if len(bullets) >= limit:
            break
        for theme_id in _top_theme_ids(theme_map, section, limit):
            if theme_id in used_theme_ids:
                continue
            rule = _theme_rule(theme_id)
            bullets.append(f"- **{rule['title']}:** {rule['summary']}")
            used_theme_ids.add(theme_id)
            if len(bullets) >= limit:
                break

    if len(bullets) < limit:
        leftovers = [sentence for sentence in fallback_sentences if _sentence_key(sentence) not in {_sentence_key(b) for b in bullets}]
        for sentence in _select_diverse(leftovers, limit - len(bullets)):
            bullets.append(f"- {sentence}")

    return "\n".join(bullets)


def _build_methods(theme_map: dict[str, list[str]], limit: int) -> str:
    sections: list[str] = []
    for theme_id in _top_theme_ids(theme_map, "methods", limit):
        rule = _theme_rule(theme_id)
        picked = list(rule.get("details", ()))
        if not picked:
            picked = _select_diverse(theme_map[theme_id], limit=4)
        if not picked:
            continue
        sections.append(f"### {rule['title']}\n{_format_bullets(picked)}")
    return "\n\n".join(sections)


def _build_practical_notes(theme_map: dict[str, list[str]], segments, limit: int) -> str:
    candidates: list[str] = []
    for theme_id in _top_theme_ids(theme_map, "practical", limit):
        rule = _theme_rule(theme_id)
        candidates.extend(list(rule.get("details", ())))

    if not candidates:
        for segment in segments:
            for sentence in segment.procedural_points + segment.decision_points:
                cleaned = _clean_sentence(sentence)
                if cleaned:
                    candidates.append(cleaned)

    picked = _select_diverse(candidates, limit=limit)
    return _format_bullets(picked)


def _build_tools_section(full_text: str) -> str:
    tools = _detect_tools(full_text)
    if not tools:
        return "- W tym materiale narzędzia nie są celem samym w sobie; liczy się to, jak składają się w działający workflow."
    return "\n".join(f"- **{tool}**" for tool in tools[:14])


def _build_keep_in_mind(sentences: list[str], used_sentences: list[str], limit: int) -> str:
    cross_cutting = [
        "Główne wąskie gardła to zwykle słabe planowanie, brudny kontekst albo źle dobrane narzędzia, a nie sam brak mocy modelu.",
        "Frameworki są ważne dlatego, że obniżają error rate i sprawiają, że system łatwiej zrozumieć oraz debugować.",
        "Progressive disclosure i czyste context window poprawiają jakość bardziej niż dokładanie kolejnych bloków promptu.",
        "Im więcej autonomii ma workflow, tym ważniejsze stają się review loop i zasada least privilege.",
        "Parallelizacja jest wygraną tylko wtedy, gdy skraca realny wall-clock time zamiast dokładać organizacyjnego narzutu.",
        "Workflow staje się trwały dopiero wtedy, gdy poprawki aktualizują zarówno kod, jak i warstwę instrukcji.",
    ]
    picked = _select_diverse(cross_cutting, limit=limit)
    return _format_bullets(picked)


def _build_examples_section(full_text: str, limit: int) -> str:
    examples = _detect_examples(full_text)
    picked = _select_diverse(examples, limit=limit)
    return _format_bullets(picked)


def _build_intro(transcript_data: dict[str, object], theme_map: dict[str, list[str]]) -> str:
    theme_titles = []
    for theme_id in _top_theme_ids(theme_map, "key_ideas", 3):
        theme_titles.append(_theme_rule(theme_id)["title"].lower())
    for theme_id in _top_theme_ids(theme_map, "methods", 3):
        title = _theme_rule(theme_id)["title"].lower()
        if title not in theme_titles:
            theme_titles.append(title)
    lead = ", ".join(theme_titles[:4]) if theme_titles else "budowy i wdrażania workflowów AI"
    return (
        f"Ten materiał to długi, praktyczny przegląd {lead}. "
        f"Najmocniejszy wątek filmu nie polega na samym zachwycie nad modelami, tylko na tym, jak zamienić ich elastyczność w systemy, "
        f"które da się uruchamiać wielokrotnie, testować, poprawiać i podłączać do realnych procesów biznesowych. "
        f"Przy czasie trwania około {transcript_data['duration_minutes']} minut najwięcej wartości daje patrzenie na kurs jak na mapę architektury: "
        f"od mentalnych modeli i ekonomicznego sensu agentic workflows, przez warstwy frameworku, aż po konkretne wzorce implementacyjne typu skills, MCP, subagenci, review i webhooki."
    )


def _build_implementation_section() -> str:
    steps = [
        "Zacznij od prostego problemu o wysokiej częstotliwości: coś, co dzieje się regularnie i ma powtarzalny schemat wejścia/wyjścia.",
        "Najpierw rozpisz directive, czyli jak ma wyglądać dobry rezultat, jakie są wejścia i co uznajesz za błąd albo sukces.",
        "Potem dopiero buduj orchestration: kolejność kroków, momenty review, punkty decyzyjne i miejsca, w których agent ma się zatrzymać albo eskalować.",
        "Elementy powtarzalne i wrażliwe przenoś do execution scripts, żeby nie zależały od humoru modelu w danej sesji.",
        "Uruchom mały test na próbce zamiast od razu odpalać pełen proces na produkcyjnym zakresie danych albo na prawdziwych systemach.",
        "Po pierwszym przejściu dodaj reviewer loop albo inne świeże spojrzenie, żeby wychwycić ślepe punkty zanim workflow zostanie utrwalony.",
        "Dopiero po lokalnej stabilizacji przechodź do webhooków, schedulowania i cloud deploymentu.",
        "Na końcu dopnij self-annealing: jeśli coś się psuje, aktualizacja ma objąć i kod, i dyrektywy, a nie tylko jeden z tych elementów.",
    ]
    return _format_bullets(steps)


def _build_risks_section() -> str:
    risks = [
        "Najczęstszy błąd to traktowanie modeli jak szybszego Google Docs zamiast jak warstwy wykonawczej podpiętej do narzędzi i procesów.",
        "Brak planu na wejściu zwykle mści się później wieloma małymi odchyleniami, które razem rozwalają końcowy rezultat.",
        "Za dużo kontekstu w jednej nitce i brak progressive disclosure pogarszają jakość pracy bardziej, niż większość osób się spodziewa.",
        "Słabe MCP albo niestabilne integracje potrafią zabić cały workflow nawet wtedy, gdy sam model działa bardzo dobrze.",
        "Subagenci używani wszędzie zaczynają generować narzut, opóźnienie i chaos zamiast realnej dźwigni.",
        "Rozjazd między directive a execution script tworzy fałszywe poczucie, że system jest udokumentowany, choć operacyjnie działa już inaczej.",
        "Wdrożenie do chmury zbyt wcześnie, zanim lokalna wersja przejdzie kilka sensownych iteracji, tylko przenosi bałagan w inne miejsce.",
        "Myślenie w kategoriach pełnej automatyzacji jednej roli może zasłonić dużo bardziej wartościowe, szerokie odciążenie wielu ról jednocześnie.",
    ]
    return _format_bullets(risks)


def compose_notes(transcript_data: dict[str, object], profile_name: str) -> str:
    note_sentences = _collect_note_worthy_sentences(transcript_data)
    theme_map = _collect_theme_sentences(note_sentences)
    full_text = " ".join(entry.text for entry in transcript_data["entries"])
    segments = build_segments(transcript_data["entries"])
    limits = _detail_limits(profile_name, transcript_data["duration_minutes"])

    intro = _build_intro(transcript_data, theme_map)
    key_ideas = _build_key_ideas(theme_map, note_sentences, limits["key_ideas"])
    methods = _build_methods(theme_map, limits["methods"])
    practical_notes = _build_practical_notes(theme_map, segments, limits["practical"])
    examples = _build_examples_section(full_text, limits["examples"])
    implementation = _build_implementation_section()
    risks = _build_risks_section()

    used_sentences: list[str] = []
    for block in (key_ideas, methods, practical_notes):
        used_sentences.extend([line[2:] for line in block.splitlines() if line.startswith("- ")])
    keep_in_mind = _build_keep_in_mind(note_sentences, used_sentences, limits["keep"])
    tools_section = _build_tools_section(full_text)

    sections = [
        f"# Notes: {transcript_data['video_title']}",
        f"**Źródło:** {transcript_data['video_url']}",
        "",
        intro,
        "",
        "## Najważniejsze idee",
        key_ideas or "- Nie wykryto wystarczająco mocnych tematów przewodnich.",
    ]

    if methods:
        sections.extend(["", "## Metody i workflow", methods])

    if examples:
        sections.extend(["", "## Przykłady z materiału", examples])

    sections.extend(["", "## Narzędzia i elementy systemu", tools_section])

    if implementation:
        sections.extend(["", "## Jak układać własny workflow", implementation])

    if practical_notes:
        sections.extend(["", "## Praktyczne uwagi", practical_notes])

    if risks:
        sections.extend(["", "## Typowe błędy i ryzyka", risks])

    if keep_in_mind:
        sections.extend(["", "## Do zapamiętania", keep_in_mind])

    return "\n".join(sections).strip() + "\n"


def main() -> int:
    args = parse_args()
    transcript_data = parse_transcript_markdown(args.transcript_path)
    if not transcript_data["entries"]:
        raise SystemExit("No transcript entries found. Cannot generate notes.")

    notes_text = compose_notes(transcript_data=transcript_data, profile_name=args.notes_profile)
    output_path = notes_output_path(args.transcript_path, args.output)
    output_path.write_text(notes_text, encoding="utf-8")

    print(f"Notes saved to: {output_path}")
    print(f"Estimated duration minutes: {transcript_data['duration_minutes']}")
    print(f"Source paragraphs: {len(transcript_data['entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
