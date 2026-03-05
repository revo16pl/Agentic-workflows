#!/usr/bin/env python3
"""Bootstrap service_page workflow from URL analysis."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from company_profile_resolver import CompanyProfileResolutionError, resolve_company_profile
from extract_service_page_context import extract_service_page_context


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare service_page workspace from URL.")
    parser.add_argument("--url", required=True, help="Service page URL to analyze.")
    parser.add_argument("--company", required=True, help='Company name, e.g. "studio balans".')
    parser.add_argument("--topic", default="", help="Optional explicit topic override.")
    parser.add_argument("--date", default="", help="Workspace date prefix (YYYY-MM-DD).")
    parser.add_argument("--section-policy", choices=["inherited", "fixed"], default="inherited")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--docs-root", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def extract_workspace(stdout: str) -> Path:
    match = re.search(r"Workspace ready:\s*(.+)", stdout)
    if not match:
        raise RuntimeError("Cannot parse workspace path from article_workflow_init output.")
    return Path(match.group(1).strip()).resolve()


def fallback_topic_from_url(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1].strip()
    if not slug:
        return "Service page"
    text = slug.replace("-", " ").replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else "Service page"


def update_run_context(workspace: Path, updates: dict[str, str]) -> None:
    path = workspace / "run_context.md"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else ["# run_context.md", ""]

    existing: dict[str, int] = {}
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if line.startswith("- ") and ":" in line:
            key = line[2:].split(":", 1)[0].strip()
            existing[key] = idx

    for key, value in updates.items():
        formatted = f"- {key}: {value}"
        if key in existing:
            lines[existing[key]] = formatted
        else:
            lines.append(formatted)

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def prefill_brief(
    brief_path: Path,
    topic: str,
    company: str,
    source_url: str,
    tab_labels: list[str],
    company_profile_id: str,
    section_policy: str,
) -> None:
    if not brief_path.exists():
        return
    text = brief_path.read_text(encoding="utf-8")
    yaml_match = re.search(r"```yaml\s*(.*?)```", text, flags=re.S)
    if yaml_match:
        yaml_text = yaml_match.group(1)
        replacements = {
            "topic": topic,
            "company": company,
            "source_url": source_url,
            "section_policy": section_policy,
            "subheading_length_target": "similar",
        }
        for key, value in replacements.items():
            pattern = rf"^{re.escape(key)}:\s*.*$"
            replacement = f'{key}: "{value}"'
            if re.search(pattern, yaml_text, flags=re.M):
                yaml_text = re.sub(pattern, replacement, yaml_text, flags=re.M)
            else:
                yaml_text += f"\n{replacement}"
        text = text[: yaml_match.start(1)] + yaml_text + text[yaml_match.end(1) :]

    labels_block = (
        "\n".join([f"- {label}" for label in tab_labels])
        if tab_labels
        else "- Wskazania\n- Przeciwwskazania i bezpieczeństwo\n- Zalecenia przed i po\n- FAQ"
    )
    auto_section = (
        "\n\n## Auto context from source URL\n"
        f"- URL: {source_url}\n"
        f"- Topic seed: {topic}\n"
        f"- Company profile id: {company_profile_id}\n"
        "- Dziedziczone zakładki:\n"
        f"{labels_block}\n"
    )
    if "## Auto context from source URL" not in text:
        text = text.rstrip() + auto_section
    brief_path.write_text(text.rstrip() + "\n", encoding="utf-8")


def prefill_service_draft(workspace: Path, tab_labels: list[str], source_subheading_chars: int) -> None:
    draft_path = workspace / "article_draft_v2.md"
    labels = [str(x).strip() for x in tab_labels if str(x).strip()]
    if not labels:
        labels = ["Wskazania", "Przeciwwskazania i bezpieczeństwo", "Zalecenia przed i po", "FAQ"]

    lines = [
        "# article_draft_v2.md",
        "",
        "## Subheading",
        f"_Wpisz nowy subheading (1-2 zdania, ok. {source_subheading_chars} znaków; podobna długość do źródła, ale nowa treść)._",
        "",
        "## Opis",
        "### Akapit 1",
        "",
        "### Akapit 2",
        "",
        "### Akapit 3",
        "",
        "## Najważniejsze informacje",
    ]

    for label in labels:
        lines.append(f"### {label}")
        lines.append("- ")

    draft_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_service_writer_packet(
    workspace: Path,
    *,
    topic: str,
    source_url: str,
    service_context: dict[str, object],
    company_snapshot: dict[str, object],
) -> Path:
    packet_path = workspace / "service_page_writer_packet.md"

    tab_labels = service_context.get("tab_labels", [])
    labels = [str(item).strip() for item in tab_labels if str(item).strip()] if isinstance(tab_labels, list) else []
    if not labels:
        labels = ["Wskazania", "Przeciwwskazania i bezpieczeństwo", "Zalecenia przed i po", "FAQ"]

    subheading = service_context.get("subheading", {})
    subheading_text = ""
    subheading_chars = 0
    if isinstance(subheading, dict):
        subheading_text = str(subheading.get("text", "")).strip()
        try:
            subheading_chars = int(subheading.get("chars", 0) or 0)
        except (TypeError, ValueError):
            subheading_chars = 0

    description = service_context.get("description", {})
    paragraph_count = 0
    if isinstance(description, dict):
        try:
            paragraph_count = int(description.get("paragraph_count", 0) or 0)
        except (TypeError, ValueError):
            paragraph_count = 0

    brand_voice = company_snapshot.get("brand_voice", {}) if isinstance(company_snapshot.get("brand_voice"), dict) else {}
    tone_rules = brand_voice.get("tone_rules", []) if isinstance(brand_voice.get("tone_rules"), list) else []
    avoid_rules = brand_voice.get("avoid_rules", []) if isinstance(brand_voice.get("avoid_rules"), list) else []
    excluded_claims = company_snapshot.get("excluded_claims", []) if isinstance(company_snapshot.get("excluded_claims"), list) else []
    legal_notes = company_snapshot.get("legal_notes", []) if isinstance(company_snapshot.get("legal_notes"), list) else []

    lines: list[str] = [
        "# service_page_writer_packet.md",
        "",
        "## Topic and intent summary",
        f"- Topic: {topic}",
        f"- URL source: {source_url}",
        "- Draft mode: manual (agent writes content from research + brief)",
        "- Dominująca intencja: commercial_local (service page)",
        "",
        "## Source page baseline (for structure, not for copy)",
        f"- Aktualny subheading: {subheading_chars} znaków",
        f"- Aktualny opis: {paragraph_count} akapity",
        "- Dziedziczone zakładki:",
    ]
    lines.extend([f"  - {label}" for label in labels])

    lines.extend(
        [
            "",
            "## Top research insights (uzupełnij po research_fetch)",
            "1. ",
            "2. ",
            "3. ",
            "",
            "## Content gaps to cover (uzupełnij po research_fetch)",
            "1. ",
            "2. ",
            "3. ",
            "",
            "## Brand voice rules",
            f"- Company profile id: {company_snapshot.get('company_profile_id', '')}",
            f"- Narrator: {brand_voice.get('narrator', '')}",
            "- Tone rules:",
        ]
    )
    lines.extend([f"  - {str(rule).strip()}" for rule in tone_rules if str(rule).strip()] or ["  - (uzupełnij)"])
    lines.append("- Avoid rules:")
    lines.extend([f"  - {str(rule).strip()}" for rule in avoid_rules if str(rule).strip()] or ["  - (uzupełnij)"])

    lines.extend(["", "## Banned claims / compliance"]) 
    lines.append("- Excluded claims:")
    lines.extend([f"  - {str(item).strip()}" for item in excluded_claims if str(item).strip()] or ["  - (brak)"])
    lines.append("- Legal notes:")
    lines.extend([f"  - {str(item).strip()}" for item in legal_notes if str(item).strip()] or ["  - (brak)"])

    lines.extend(
        [
            "",
            "## CMS sections and quality checklist",
            "### Subheading",
            f"- Target length: similar to source (~{subheading_chars} chars)",
            "- New copy only (nie kopiuj existing tekstu)",
            "",
            "### Opis",
            "- 3 krótkie akapity",
            "- Edukacyjny, logiczny flow, konkret",
            "- Zero fillerów i pustych ogólników",
            "",
            "### Najważniejsze informacje",
            "- Każda zakładka musi mieć realny content",
            "- FAQ: min 2 pytania z krótkimi odpowiedziami",
            "- Bez pustych bulletów i placeholderów",
            "",
            "## Editorial QA protocol (obowiązkowe przed exportem)",
            "1. Przeczytaj draft na głos i usuń każde zdanie, które brzmi sztucznie albo nielogicznie.",
            "2. Zrób minimum 2 iteracje redakcyjne; nie poprawiaj samych słów, tylko całe fragmenty 2-3 zdań.",
            "3. Użyj kolejno perspektyw: content-strategy -> copywriting -> copy-editing.",
            "4. Po machine QA wróć jeszcze raz do draftu i wdroż poprawki, jeśli którykolwiek checker coś złapie.",
            "5. Zapisz decyzje i poprawki w editorial_review.md.",
            "6. Nie oznaczaj draftu jako gotowego, dopóki logic_pass != PASS i post_machine_qa_revision_completed != yes.",
            "",
            "## CTA and links",
            f"- CTA (MoFu): {company_snapshot.get('default_cta', {}).get('mofu', '') if isinstance(company_snapshot.get('default_cta'), dict) else ''}",
            "- Allowed service links:",
        ]
    )
    allowed_links = company_snapshot.get("allowed_service_links", [])
    if isinstance(allowed_links, list) and allowed_links:
        lines.extend([f"  - {str(link).strip()}" for link in allowed_links if str(link).strip()])
    else:
        lines.append("  - (brak)")

    if subheading_text:
        lines.extend(["", "## Source lead (reference only)", f"> {subheading_text}"])

    packet_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return packet_path


def main() -> int:
    args = parse_args()
    url = args.url.strip()
    company = args.company.strip()

    context = extract_service_page_context(url)
    topic = args.topic.strip() or str(context.get("h1", "")).strip() or fallback_topic_from_url(url)
    tab_labels = [str(x).strip() for x in (context.get("tab_labels", []) or []) if str(x).strip()]
    section_labels_csv = ", ".join(tab_labels)

    try:
        company_snapshot = resolve_company_profile(company_input=company)
    except CompanyProfileResolutionError as exc:
        print(f"ERROR: {exc}")
        return 1

    cmd = [
        "python3",
        str(PROJECT_ROOT / "execution" / "article_workflow_init.py"),
        "--topic",
        topic,
        "--company",
        company,
        "--content-profile",
        "service_page",
        "--source-url",
        url,
        "--section-policy",
        args.section_policy,
    ]
    if args.date.strip():
        cmd.extend(["--date", args.date.strip()])
    if args.workspace_root:
        cmd.extend(["--workspace-root", str(args.workspace_root.resolve())])
    if args.docs_root:
        cmd.extend(["--docs-root", str(args.docs_root.resolve())])
    if args.force:
        cmd.append("--force")

    run = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if run.returncode != 0:
        print(run.stdout)
        print(run.stderr)
        return run.returncode

    workspace = extract_workspace(run.stdout)
    context_path = workspace / "service_page_context.json"
    context_path.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    company_snapshot_path = workspace / "company_profile_snapshot.json"
    company_snapshot_path.write_text(json.dumps(company_snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    update_run_context(
        workspace,
        {
            "content_profile": "service_page",
            "source_url": url,
            "section_policy": args.section_policy,
            "section_labels": section_labels_csv,
            "subheading_length_target": "similar",
            "company_profile_id": str(company_snapshot.get("company_profile_id", "")).strip(),
            "brand_voice_loaded": "yes",
        },
    )
    prefill_brief(
        brief_path=workspace / "article_brief.md",
        topic=topic,
        company=company,
        source_url=url,
        tab_labels=tab_labels,
        company_profile_id=str(company_snapshot.get("company_profile_id", "")).strip(),
        section_policy=args.section_policy,
    )

    subheading_chars = 0
    subheading = context.get("subheading", {})
    if isinstance(subheading, dict):
        try:
            subheading_chars = int(subheading.get("chars", 0) or 0)
        except (TypeError, ValueError):
            subheading_chars = 0

    prefill_service_draft(workspace=workspace, tab_labels=tab_labels, source_subheading_chars=subheading_chars)
    packet_path = write_service_writer_packet(
        workspace,
        topic=topic,
        source_url=url,
        service_context=context,
        company_snapshot=company_snapshot,
    )

    print(f"Workspace ready: {workspace}")
    print(f"Service context: {context_path}")
    print(f"Company profile snapshot: {company_snapshot_path}")
    print(f"Writer packet: {packet_path}")
    print(f"Topic: {topic}")
    print(f"Tabs: {', '.join(tab_labels) if tab_labels else '(fallback labels)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
