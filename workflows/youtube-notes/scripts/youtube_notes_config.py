from __future__ import annotations

from dataclasses import dataclass


DEFAULT_LANGUAGE_POLICY = "pl_strict"
DEFAULT_EVIDENCE_MODE = "annex"


@dataclass(frozen=True)
class ProfileConfig:
    internal_name: str
    word_min: int
    word_max: int
    methods_min: int
    takeaways_min: int
    claims_min: int
    tldr_sentences: int


# v4: lekkie profile długości + miękkie minima treści
PROFILE_CONFIGS: dict[str, ProfileConfig] = {
    "short": ProfileConfig("short", 250, 600, 4, 4, 0, 0),
    "standard": ProfileConfig("standard", 600, 1400, 6, 6, 0, 0),
    "deep": ProfileConfig("deep", 1400, 2600, 9, 8, 0, 0),
    "deep_plus": ProfileConfig("deep+", 2600, 4200, 12, 10, 0, 0),
}

PROCEDURAL_PATTERNS = (
    r"\bzrób\b",
    r"\buruchom\b",
    r"\bustaw\b",
    r"\bskonfigur\w*\b",
    r"\bwdro\w*\b",
    r"\bprzetest\w*\b",
    r"\bbuild\b",
    r"\bdeploy\b",
    r"\bconfigure\b",
    r"\bimplement\w*\b",
    r"\bcreate\b",
)

DECISION_PATTERNS = (
    r"\bkiedy\b",
    r"\bpo co\b",
    r"\bjeśli\b",
    r"\bwtedy\b",
    r"\bwhen\b",
    r"\bwhy\b",
    r"\bif\b",
    r"\btrade-?off\b",
    r"\bris(k|k)o\b",
    r"\bdecyzj\w*\b",
)

TOOL_HINTS = (
    "Claude",
    "Claude Code",
    "Gemini",
    "OpenAI",
    "Antigravity",
    "Cursor",
    "VS Code",
    "GitHub",
    "Git",
    "Supabase",
    "Postgres",
    "PostgreSQL",
    "Next.js",
    "Tailwind",
    "Vercel",
    "Netlify",
    "n8n",
    "Make",
    "Zapier",
    "LangGraph",
    "LangChain",
    "Playwright",
    "MCP",
)
