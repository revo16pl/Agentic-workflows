#!/usr/bin/env python3
"""Export final article markdown to Google Docs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from article_workflow_state import recompute_hard_block_gate, set_hard_gate_set
from article_workflow_validate import validate_workspace

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export article draft to Google Docs.")
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace directory path.")
    parser.add_argument("--input", default="article_draft_v2.md", help="Source markdown in workspace.")
    parser.add_argument("--title", default=None, help="Google Doc title (optional).")
    parser.add_argument("--folder-id", default=None, help="Google Drive folder id (optional).")
    parser.add_argument("--owner", default=None, help="Owner name for metadata (optional).")
    parser.add_argument("--company", default=None, help="Override company metadata (optional).")
    parser.add_argument("--topic", default=None, help="Override topic metadata (optional).")
    parser.add_argument("--dry-run", action="store_true", help="Resolve metadata without API call.")
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip pre-export QA validation (not recommended).",
    )
    parser.add_argument(
        "--skip-language-fix",
        action="store_true",
        help="Skip automatic Polish language correction/check before validation.",
    )
    parser.add_argument(
        "--skip-humanization-check",
        action="store_true",
        help="Skip humanization gate check before validation.",
    )
    parser.add_argument(
        "--skip-naturalness-check",
        action="store_true",
        help="Skip rule-based Polish naturalness check before validation.",
    )
    parser.add_argument(
        "--skip-fluency-ml-check",
        action="store_true",
        help="Skip Polish fluency ML check before validation.",
    )
    parser.add_argument(
        "--skip-context-check",
        action="store_true",
        help="Skip workflow context check (skills/evidence) before validation.",
    )
    parser.add_argument(
        "--skip-research-check",
        action="store_true",
        help="Skip research quality gate check before validation.",
    )
    return parser.parse_args()


def load_env(project_root: Path) -> None:
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def parse_brief_metadata(brief_path: Path) -> dict[str, str]:
    if not brief_path.exists():
        return {}
    text = brief_path.read_text(encoding="utf-8")
    yaml_block = re.search(r"```yaml\s*(.*?)```", text, flags=re.S)
    if not yaml_block:
        return {}
    metadata: dict[str, str] = {}
    for raw_line in yaml_block.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        clean_value = value.strip()
        if " #" in clean_value:
            clean_value = clean_value.split(" #", 1)[0].strip()
        metadata[key.strip()] = clean_value.strip('"').strip("'")
    return metadata


def parse_run_context(run_context_path: Path) -> dict[str, str]:
    if not run_context_path.exists():
        return {}
    payload: dict[str, str] = {}
    for raw_line in run_context_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        payload[key.strip()] = value.strip()
    return payload


def load_google_clients(credentials_path: Path, token_path: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:  # pragma: no cover
        print(
            "ERROR: Missing Google API dependencies. Run: "
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    creds = None
    if token_path.exists() and token_path.stat().st_size > 0:
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except (json.JSONDecodeError, ValueError):
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return docs_service, drive_service


def generate_title(topic: str, company: str, date_stamp: str) -> str:
    return f"{company or 'Unknown company'} | {topic or 'Untitled article'} | {date_stamp}"


INLINE_MARKUP_PATTERN = re.compile(
    r"\[([^\]]+)\]\((https?://[^)\s]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`",
)


def parse_inline_markup(text: str) -> tuple[str, list[dict[str, object]]]:
    plain_parts: list[str] = []
    styles: list[dict[str, object]] = []
    cursor = 0
    output_len = 0

    for match in INLINE_MARKUP_PATTERN.finditer(text):
        prefix = text[cursor : match.start()]
        plain_parts.append(prefix)
        output_len += len(prefix)

        link_text = match.group(1)
        link_url = match.group(2)
        bold_text = match.group(3)
        italic_text = match.group(4)
        code_text = match.group(5)

        if link_text is not None and link_url is not None:
            plain_parts.append(link_text)
            styles.append(
                {
                    "start": output_len,
                    "end": output_len + len(link_text),
                    "type": "link",
                    "url": link_url,
                }
            )
            output_len += len(link_text)
        elif bold_text is not None:
            plain_parts.append(bold_text)
            styles.append(
                {
                    "start": output_len,
                    "end": output_len + len(bold_text),
                    "type": "bold",
                }
            )
            output_len += len(bold_text)
        elif italic_text is not None:
            plain_parts.append(italic_text)
            styles.append(
                {
                    "start": output_len,
                    "end": output_len + len(italic_text),
                    "type": "italic",
                }
            )
            output_len += len(italic_text)
        elif code_text is not None:
            plain_parts.append(code_text)
            styles.append(
                {
                    "start": output_len,
                    "end": output_len + len(code_text),
                    "type": "code",
                }
            )
            output_len += len(code_text)

        cursor = match.end()

    tail = text[cursor:]
    plain_parts.append(tail)
    return "".join(plain_parts), styles


def parse_markdown_line(line: str) -> tuple[str, str, int]:
    stripped = line.rstrip()
    if not stripped:
        return ("blank", "", 0)

    heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
    if heading_match:
        level = min(len(heading_match.group(1)), 4)
        return ("heading", heading_match.group(2).strip(), level)

    ordered_match = re.match(r"^\s*\d+\.\s+(.*)$", stripped)
    if ordered_match:
        return ("ordered_list", ordered_match.group(1).strip(), 0)

    unordered_match = re.match(r"^\s*[-*]\s+(.*)$", stripped)
    if unordered_match:
        return ("unordered_list", unordered_match.group(1).strip(), 0)

    quote_match = re.match(r"^\s*>\s?(.*)$", stripped)
    if quote_match:
        return ("paragraph", quote_match.group(1).strip(), 0)

    if stripped in {"---", "***"}:
        return ("blank", "", 0)

    return ("paragraph", stripped, 0)


def heading_named_style(level: int) -> str:
    if level <= 1:
        return "HEADING_1"
    if level == 2:
        return "HEADING_2"
    if level == 3:
        return "HEADING_3"
    return "HEADING_4"


def markdown_to_gdocs_payload(markdown_body: str) -> tuple[str, list[dict[str, object]]]:
    lines = markdown_body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    full_text_parts: list[str] = []
    requests: list[dict[str, object]] = []
    bullet_ranges: list[tuple[int, int, str]] = []
    cursor = 1  # Google Docs index starts at 1 for inserted text.

    for line in lines:
        line_type, content, level = parse_markdown_line(line)
        plain_content, inline_styles = parse_inline_markup(content)

        line_start = cursor
        full_text_parts.append(plain_content)
        cursor += len(plain_content)
        line_end = cursor
        full_text_parts.append("\n")
        cursor += 1

        paragraph_end = line_end + 1
        if line_type == "heading" and plain_content:
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": line_start, "endIndex": paragraph_end},
                        "paragraphStyle": {"namedStyleType": heading_named_style(level)},
                        "fields": "namedStyleType",
                    }
                }
            )
        elif line_type == "unordered_list" and plain_content:
            bullet_ranges.append((line_start, paragraph_end, "BULLET_DISC_CIRCLE_SQUARE"))
        elif line_type == "ordered_list" and plain_content:
            bullet_ranges.append((line_start, paragraph_end, "NUMBERED_DECIMAL_ALPHA_ROMAN"))

        for style in inline_styles:
            start = line_start + int(style["start"])
            end = line_start + int(style["end"])
            if start >= end:
                continue
            style_type = str(style.get("type", ""))
            if style_type == "bold":
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": start, "endIndex": end},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    }
                )
            elif style_type == "italic":
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": start, "endIndex": end},
                            "textStyle": {"italic": True},
                            "fields": "italic",
                        }
                    }
                )
            elif style_type == "code":
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": start, "endIndex": end},
                            "textStyle": {
                                "weightedFontFamily": {"fontFamily": "Roboto Mono"},
                                "backgroundColor": {
                                    "color": {"rgbColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}
                                },
                            },
                            "fields": "weightedFontFamily,backgroundColor",
                        }
                    }
                )
            elif style_type == "link":
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": start, "endIndex": end},
                            "textStyle": {"link": {"url": str(style.get("url", ""))}},
                            "fields": "link",
                        }
                    }
                )

    for start, end, preset in bullet_ranges:
        requests.append(
            {
                "createParagraphBullets": {
                    "range": {"startIndex": start, "endIndex": end},
                    "bulletPreset": preset,
                }
            }
        )

    full_text = "".join(full_text_parts).strip() + "\n"
    return full_text, requests


def move_doc_to_folder(drive_service, file_id: str, folder_id: str) -> None:
    file_meta = drive_service.files().get(fileId=file_id, fields="parents").execute()
    previous_parents = ",".join(file_meta.get("parents", []))
    drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields="id, parents",
    ).execute()


def write_iteration_feedback(workspace: Path, errors: list[str]) -> Path:
    suggestions = []
    error_map = {
        "qa final_decision must be approved": "Ustaw `final_decision: approved` dopiero po poprawkach i ponownym QA.",
        "publish_ready.md must be ready_for_manual_review or approved": "Ustaw w `publish_ready.md` status `Ready_for_manual_review` po przejsciu gate'ow.",
        "word count": "Dopasuj dlugosc `article_draft_v2.md` do zakresu `word_count_min`/`word_count_max` w briefie.",
        "human_quality_pass": "Uzupelnij i ustaw `human_quality_pass: PASS` po redakcji anty-slop.",
        "keyword_coverage_pass": "Uzupelnij i ustaw `keyword_coverage_pass: PASS` po sprawdzeniu pokrycia klastra.",
        "internal_linking_pass": "Uzupelnij i ustaw `internal_linking_pass: PASS` po weryfikacji linkowania.",
        "length_strategy_pass": "Uzupelnij i ustaw `length_strategy_pass: PASS` po sprawdzeniu strategii dlugosci.",
        "seo_on_page_pass": "Uzupelnij i ustaw `seo_on_page_pass: PASS` po finalnej kontroli SEO on-page.",
        "polish_diacritics_pass": "Uzupelnij i ustaw `polish_diacritics_pass: PASS` po poprawie polskich znakow diakrytycznych.",
        "polish_grammar_pass": "Uzupelnij i ustaw `polish_grammar_pass: PASS` po poprawie gramatyki i pisowni.",
        "forbidden_phrase_pass": "Usun zakazane frazy AI-slop i ustaw `forbidden_phrase_pass: PASS`.",
        "specificity_pass": "Dodaj konkrety (liczby, przyklady, lokalne osadzenie, naturalne linki) i ustaw `specificity_pass: PASS`.",
        "voice_authenticity_pass": "Popraw zgodnosc z brand voice i ustaw `voice_authenticity_pass: PASS`.",
        "detector_ensemble_pass": "Popraw styl i przejdz open-source detector ensemble (`detector_ensemble_pass: PASS`).",
        "rewrite_loop_pass": "Wykonaj kolejna iteracje redakcyjna (przepisanie fragmentow), uruchom ponownie QA i ustaw `rewrite_loop_pass: PASS` dopiero po przejsciu wszystkich gate'ow.",
        "missing polish diacritics": "Dopracuj tekst w jezyku polskim z poprawnymi znakami diakrytycznymi (ą, ć, ę, ł, ń, ó, ś, ż, ź).",
        "polish grammar quality below gate": "Popraw wykryte bledy jezykowe i gramatyczne; uruchom walidacje ponownie.",
        "grammar validation unavailable": "Sprawdz dostep do LanguageTool API i uruchom walidacje ponownie.",
        "polish language auto-fix/check failed": "Uruchom `execution/check_polish_language.py --apply` i popraw wskazane problemy przed eksportem.",
        "humanization check failed": "Uruchom `execution/check_humanization.py`, popraw tekst i doprowadz wszystkie humanization gates do PASS.",
        "polish naturalness check failed": "Uruchom `execution/check_polish_naturalness.py`, popraw tytuł/kolokacje/rytm i powtórz walidację.",
        "polish fluency ml check failed": "Uruchom `execution/check_polish_fluency_ml.py` i popraw fragmenty o niskiej płynności językowej.",
        "workflow context check failed": "Uzupełnij `run_context.md` (skills_loaded/skills_applied) oraz `research_evidence_manifest.json` i ponów walidację.",
        "research quality check failed": "Uruchom `execution/check_research_quality.py`, popraw dane research i doprowadź wszystkie research gates do PASS.",
        "skills_policy_pass": "Uzupełnij `skills_loaded` i `skills_applied` o wymagane skills: content-strategy, copywriting, copy-editing, seo-audit, schema-markup, ai-seo.",
        "evidence_provenance_pass": "Uzupełnij `research_evidence_manifest.json` zgodnie z Evidence Contract (źródło, query, URL, date_range, pulled_at).",
        "polish_title_naturalness_pass": "Popraw tytuł na naturalny polski (bez konstrukcji typu „komu ... się sprawdza”).",
        "polish_collocation_pass": "Usuń nienaturalne kolokacje i sztuczne frazy (AI-slop).",
        "polish_punctuation_pass": "Popraw interpunkcję i skróty; usuń podejrzane skróty/skrótowce.",
        "polish_fluency_ml_pass": "Popraw zdania o niskiej płynności; uprość składnię i dopasuj idiomy do naturalnego PL.",
        "structure_variance_pass_v2": "Zwiększ zróżnicowanie długości zdań i akapitów.",
        "semantic_rewrite_pass_v2": "Wykonaj rewrite blokowy 2-4 zdań (nie tylko podmiana pojedynczych słów).",
        "keyword_metrics_coverage_pass": "Uruchom `execution/research_fetch.py` i upewnij się, że manifest ma min. 40 rekordów `keyword_metrics` oraz >=80% z `avg_monthly_searches`.",
        "serp_dataset_quality_pass": "Uzupełnij dane SERP (min. 30 rekordów i min. 8 unikalnych domen) przez `execution/research_fetch.py`.",
        "trends_dataset_quality_pass": "Uzupełnij dane trends (min. 5 zapytań i min. 12 punktów na zapytanie) przez `execution/research_fetch.py`.",
        "competitor_matrix_pass": "Uzupełnij `competitor_matrix` (min. 10 URL) i `content_gaps` (min. 5).",
        "research_data_freshness_pass": "Odśwież research (`execution/research_fetch.py`), aby `pulled_at` było aktualne.",
        "research_hard_block_pass": "Uruchom `execution/check_research_quality.py` i doprowadź wszystkie research gate'y do PASS.",
    }

    for error in errors:
        normalized = error.lower()
        if normalized.startswith("humanization gates failed:"):
            tail = normalized.split(":", 1)[1]
            for gate_name in [x.strip() for x in tail.split(",") if x.strip()]:
                action = error_map.get(gate_name)
                if action:
                    suggestions.append(action)
            continue
        for key, action in error_map.items():
            if key in normalized:
                suggestions.append(action)
                break

    unique_suggestions = list(dict.fromkeys(suggestions))
    max_iterations = int(os.getenv("ARTICLE_MAX_REWRITE_ITERATIONS", "5"))
    previous_iteration = 0
    feedback_path = workspace / "qa_iteration_feedback.md"
    if feedback_path.exists():
        prior = feedback_path.read_text(encoding="utf-8")
        match = re.search(r"iteration_count\s*:\s*(\d+)", prior, flags=re.IGNORECASE)
        if match:
            previous_iteration = int(match.group(1))
    iteration_count = previous_iteration + 1
    blocked_for_limit = iteration_count >= max_iterations

    now = dt.datetime.now().isoformat(timespec="seconds")
    lines = [
        "# qa_iteration_feedback.md",
        "",
        f"generated_at: {now}",
        f"status: {'Revise_required' if blocked_for_limit else 'revise_required'}",
        f"iteration_count: {iteration_count}",
        f"max_iterations: {max_iterations}",
        "",
        "## Validation errors",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- (no errors captured)"])
    lines.extend(["", "## Suggested actions"])
    lines.extend([f"- {item}" for item in unique_suggestions] or ["- Przejrzyj qa_report.md i popraw wskazane obszary."])

    if blocked_for_limit:
        lines.extend(
            [
                "",
                "## Iteration limit",
                "- Osiagnieto limit iteracji bez pelnego PASS.",
                "- Eksport do Google Docs pozostaje zablokowany do czasu recznej korekty strategii/artykulu.",
            ]
        )

    feedback_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return feedback_path


def run_polish_language_pass(workspace: Path, source_filename: str) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().parent / "check_polish_language.py"
    if not script_path.exists():
        return False, f"Language checker script not found: {script_path}"

    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(workspace),
        "--input",
        source_filename,
        "--output",
        source_filename,
        "--report",
        "language_quality_report.md",
        "--apply",
        "--json",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True, process.stdout.strip()

    stderr = process.stderr.strip()
    stdout = process.stdout.strip()
    details = stderr or stdout or "Unknown language check error."
    return False, details


def run_humanization_pass(workspace: Path, source_filename: str) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().parent / "check_humanization.py"
    if not script_path.exists():
        return False, f"Humanization checker script not found: {script_path}"

    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(workspace),
        "--input",
        source_filename,
        "--report",
        "humanization_report.md",
        "--json",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True, process.stdout.strip()

    stderr = process.stderr.strip()
    stdout = process.stdout.strip()
    failed_gates: list[str] = []
    if stdout:
        try:
            payload = json.loads(stdout)
            gates = payload.get("gates", {}) if isinstance(payload, dict) else {}
            if isinstance(gates, dict):
                failed_gates = [str(k) for k, v in gates.items() if not bool(v)]
        except json.JSONDecodeError:
            failed_gates = []

    if failed_gates:
        gate_text = ", ".join(failed_gates)
        details = f"Humanization gates failed: {gate_text}"
    else:
        details = stdout or "Unknown humanization check error."

    noise_markers = ["unauthenticated requests to the hf hub"]
    if stderr and not any(marker in stderr.lower() for marker in noise_markers):
        details = f"{details}\n{stderr}" if details else stderr
    return False, details


def run_polish_naturalness_pass(workspace: Path, source_filename: str) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().parent / "check_polish_naturalness.py"
    if not script_path.exists():
        return False, f"Naturalness checker script not found: {script_path}"

    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(workspace),
        "--input",
        source_filename,
        "--report",
        "polish_naturalness_report.md",
        "--json",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True, process.stdout.strip()
    details = process.stderr.strip() or process.stdout.strip() or "Unknown naturalness check error."
    return False, details


def run_polish_fluency_ml_pass(workspace: Path, source_filename: str) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().parent / "check_polish_fluency_ml.py"
    if not script_path.exists():
        return False, f"Polish fluency ML checker script not found: {script_path}"

    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(workspace),
        "--input",
        source_filename,
        "--report",
        "polish_fluency_ml_report.md",
        "--json",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True, process.stdout.strip()
    details = process.stderr.strip() or process.stdout.strip() or "Unknown fluency ML check error."
    return False, details


def run_workflow_context_pass(workspace: Path) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().parent / "check_workflow_context.py"
    if not script_path.exists():
        return False, f"Workflow context checker script not found: {script_path}"

    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(workspace),
        "--report",
        "workflow_context_report.md",
        "--json",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True, process.stdout.strip()
    details = process.stderr.strip() or process.stdout.strip() or "Unknown context check error."
    return False, details


def run_research_quality_pass(workspace: Path) -> tuple[bool, str]:
    script_path = Path(__file__).resolve().parent / "check_research_quality.py"
    if not script_path.exists():
        return False, f"Research quality checker script not found: {script_path}"

    cmd = [
        sys.executable,
        str(script_path),
        "--workspace",
        str(workspace),
        "--report",
        "research_quality_report.md",
        "--json",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True, process.stdout.strip()
    details = process.stderr.strip() or process.stdout.strip() or "Unknown research quality check error."
    return False, details


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    if not workspace.exists():
        print(f"ERROR: Workspace not found: {workspace}", file=sys.stderr)
        return 1

    project_root = Path(__file__).resolve().parent.parent
    load_env(project_root)

    source_path = workspace / args.input
    if not source_path.exists():
        print(f"ERROR: Source file not found: {source_path}", file=sys.stderr)
        return 1

    if not args.skip_language_fix:
        language_ok, language_details = run_polish_language_pass(
            workspace=workspace,
            source_filename=args.input,
        )
        if not language_ok:
            print("ERROR: Polish language correction/check failed.", file=sys.stderr)
            print(language_details, file=sys.stderr)
            feedback_path = write_iteration_feedback(
                workspace=workspace,
                errors=[
                    "polish language auto-fix/check failed",
                    language_details,
                ],
            )
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    if not args.skip_naturalness_check:
        natural_ok, natural_details = run_polish_naturalness_pass(
            workspace=workspace,
            source_filename=args.input,
        )
        if not natural_ok:
            print("ERROR: Polish naturalness check failed.", file=sys.stderr)
            print(natural_details, file=sys.stderr)
            feedback_path = write_iteration_feedback(
                workspace=workspace,
                errors=[
                    "polish naturalness check failed",
                    natural_details,
                ],
            )
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    if not args.skip_fluency_ml_check:
        fluency_ok, fluency_details = run_polish_fluency_ml_pass(
            workspace=workspace,
            source_filename=args.input,
        )
        if not fluency_ok:
            print("ERROR: Polish fluency ML check failed.", file=sys.stderr)
            print(fluency_details, file=sys.stderr)
            feedback_path = write_iteration_feedback(
                workspace=workspace,
                errors=[
                    "polish fluency ML check failed",
                    fluency_details,
                ],
            )
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    if not args.skip_humanization_check:
        human_ok, human_details = run_humanization_pass(
            workspace=workspace,
            source_filename=args.input,
        )
        if not human_ok:
            print("ERROR: Humanization check failed.", file=sys.stderr)
            print(human_details, file=sys.stderr)
            feedback_path = write_iteration_feedback(
                workspace=workspace,
                errors=[
                    "humanization check failed",
                    human_details,
                ],
            )
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    if not args.skip_context_check:
        context_ok, context_details = run_workflow_context_pass(workspace=workspace)
        if not context_ok:
            print("ERROR: Workflow context check failed.", file=sys.stderr)
            print(context_details, file=sys.stderr)
            feedback_path = write_iteration_feedback(
                workspace=workspace,
                errors=[
                    "workflow context check failed",
                    context_details,
                ],
            )
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    if not args.skip_research_check:
        research_ok, research_details = run_research_quality_pass(workspace=workspace)
        if not research_ok:
            print("ERROR: Research quality check failed.", file=sys.stderr)
            print(research_details, file=sys.stderr)
            feedback_path = write_iteration_feedback(
                workspace=workspace,
                errors=[
                    "research quality check failed",
                    research_details,
                ],
            )
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    hard_gate_order = [
        "polish_title_naturalness_pass",
        "polish_collocation_pass",
        "polish_grammar_pass",
        "polish_diacritics_pass",
        "polish_punctuation_pass",
        "polish_fluency_ml_pass",
        "structure_variance_pass_v2",
        "semantic_rewrite_pass_v2",
        "forbidden_phrase_pass",
        "specificity_pass",
        "voice_authenticity_pass",
        "rewrite_loop_pass",
        "evidence_provenance_pass",
        "skills_policy_pass",
        "keyword_metrics_coverage_pass",
        "serp_dataset_quality_pass",
        "trends_dataset_quality_pass",
        "competitor_matrix_pass",
        "research_data_freshness_pass",
        "research_hard_block_pass",
        "hard_block_export_pass",
    ]
    set_hard_gate_set(workspace=workspace, hard_gate_names=hard_gate_order)
    recompute_hard_block_gate(workspace=workspace)

    if not args.skip_validation:
        recompute_hard_block_gate(workspace=workspace)
        precheck = validate_workspace(workspace=workspace, mode="pre_export")
        if not precheck.ok:
            print("ERROR: Pre-export validation failed. Fix issues before Google Docs export.", file=sys.stderr)
            for error in precheck.errors:
                print(f"- {error}", file=sys.stderr)
            feedback_path = write_iteration_feedback(workspace=workspace, errors=precheck.errors)
            print(f"Feedback file created: {feedback_path}", file=sys.stderr)
            return 1

    brief_meta = parse_brief_metadata(workspace / "article_brief.md")
    context_meta = parse_run_context(workspace / "run_context.md")
    company = args.company or brief_meta.get("company") or context_meta.get("company") or "unknown-company"
    topic = args.topic or brief_meta.get("topic") or context_meta.get("topic") or source_path.stem
    owner = args.owner or brief_meta.get("owner") or os.getenv("USER", "unknown")
    folder_id = args.folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    title = args.title or generate_title(topic=topic, company=company, date_stamp=dt.date.today().isoformat())

    markdown_body = source_path.read_text(encoding="utf-8")
    doc_content, doc_style_requests = markdown_to_gdocs_payload(markdown_body)

    if args.dry_run:
        print("Dry run enabled. No API call made.")
        print(f"- title: {title}")
        print(f"- company: {company}")
        print(f"- topic: {topic}")
        print(f"- source: {source_path}")
        print(f"- folder_id: {folder_id or '(not set)'}")
        print(f"- rich_text_requests: {len(doc_style_requests)}")
        return 0

    credentials_path = Path(os.getenv("GOOGLE_OAUTH_CREDENTIALS", str(project_root / "credentials.json"))).resolve()
    token_path = Path(os.getenv("GOOGLE_OAUTH_TOKEN", str(project_root / "token.json"))).resolve()
    if not credentials_path.exists():
        print(
            f"ERROR: OAuth credentials not found: {credentials_path}. "
            "Set GOOGLE_OAUTH_CREDENTIALS or add credentials.json in project root.",
            file=sys.stderr,
        )
        return 1

    docs_service, drive_service = load_google_clients(credentials_path=credentials_path, token_path=token_path)
    created_doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = created_doc["documentId"]

    update_requests: list[dict[str, object]] = [{"insertText": {"location": {"index": 1}, "text": doc_content}}]
    update_requests.extend(doc_style_requests)
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": update_requests}).execute()

    if folder_id:
        move_doc_to_folder(drive_service=drive_service, file_id=doc_id, folder_id=folder_id)

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"ARTYKUL GOTOWY: {doc_url}")
    print("Status: gotowy do manual review w Google Docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
