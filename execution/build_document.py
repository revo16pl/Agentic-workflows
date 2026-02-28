#!/usr/bin/env python3
"""
STEP 3 of 3: Build final PDF from prepared intermediates.

Input:  .tmp/{stem}/  containing:
          slides/slide_01.png ...   (from Step 1)
          extracted.json            (from Step 1)
          descriptions.json         (from Step 2, written by Claude)

Output: file_converter/output/{stem}.pdf

Usage:
    python3 execution/build_document.py ".tmp/WS-06 Milestones"
    python3 execution/build_document.py ".tmp/WS-06 Milestones" "custom/output/dir"
"""

import sys
import json
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Image, Paragraph, Spacer, PageBreak, HRFlowable
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("ERROR: pip3 install reportlab")
    sys.exit(1)

# Register Unicode-capable font for Polish characters
_ARIAL_UNICODE = "/Library/Fonts/Arial Unicode.ttf"
if Path(_ARIAL_UNICODE).exists():
    pdfmetrics.registerFont(TTFont("MainFont", _ARIAL_UNICODE))
    pdfmetrics.registerFont(TTFont("MainFont-Bold", _ARIAL_UNICODE))
    FONT_REGULAR = "MainFont"
    FONT_BOLD = "MainFont-Bold"
else:
    # Fallback — may not render Polish chars
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

BASE = Path(__file__).parent.parent


# ─── Styles ───────────────────────────────────────────────────────────────────

def make_styles():
    custom = {}

    custom["slide_heading"] = ParagraphStyle(
        "slide_heading",
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        spaceAfter=6,
        textColor=HexColor("#1a1a2e"),
    )
    custom["section_label"] = ParagraphStyle(
        "section_label",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=14,
        spaceBefore=12,
        spaceAfter=4,
        textColor=HexColor("#444466"),
    )
    custom["body"] = ParagraphStyle(
        "body",
        fontName=FONT_REGULAR,
        fontSize=10,
        leading=14,
        spaceAfter=2,
    )
    custom["phase_header"] = ParagraphStyle(
        "phase_header",
        fontName=FONT_BOLD,
        fontSize=10.5,
        leading=14,
        spaceBefore=12,
        spaceAfter=3,
        textColor=HexColor("#1a1a2e"),
    )
    custom["bullet"] = ParagraphStyle(
        "bullet",
        fontName=FONT_REGULAR,
        fontSize=9.5,
        leading=13,
        leftIndent=14,
        spaceAfter=2,
    )
    custom["milestone"] = ParagraphStyle(
        "milestone",
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=13,
        leftIndent=14,
        spaceBefore=5,
        spaceAfter=2,
        textColor=HexColor("#8B0000"),
    )
    return custom


# ─── Structured text renderer ─────────────────────────────────────────────────

def render_structured_text(story, text, styles):
    """
    Render structured text into reportlab story elements.

    Line prefixes:
      ## <text>  → phase/section header (bold, dark)
      •  <text>  → bullet point (indented)
      →  <text>  → milestone (bold, dark red, indented)
      <text>     → body paragraph
    """
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 3))
            continue

        # Escape XML special characters
        safe = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if stripped.startswith("## "):
            story.append(Paragraph(safe[3:], styles["phase_header"]))
        elif stripped.startswith("• "):
            story.append(Paragraph(safe[2:], styles["bullet"]))
        elif stripped.startswith("→ "):
            story.append(Paragraph(safe[2:], styles["milestone"]))
        else:
            story.append(Paragraph(safe, styles["body"]))


# ─── PDF builder ──────────────────────────────────────────────────────────────

def build_pdf(tmp_dir: Path, output_path: Path, slides_data: list, descriptions: dict):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    page_width = A4[0] - 4 * cm  # usable width
    page_height = A4[1] - 4 * cm

    styles = make_styles()
    story = []

    slides_dir = tmp_dir / "slides"

    for slide_info in slides_data:
        num = slide_info["slide"]
        title = slide_info.get("title", "")
        texts = slide_info.get("texts", [])
        notes = slide_info.get("notes", "")

        desc_data = descriptions.get(num, {})
        if isinstance(desc_data, dict):
            description = desc_data.get("description", "")
            structured_text = desc_data.get("structured_text", "")
        else:
            description = str(desc_data)
            structured_text = ""

        # Skip truly empty slides (no title, no text, no description)
        if not title and not texts and not description:
            continue

        # ── Slide heading ──
        heading_text = f"Slide {num}"
        if title:
            heading_text += f": {title}"
        story.append(Paragraph(heading_text, styles["slide_heading"]))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#ccccdd"), spaceAfter=8))

        # ── Screenshot ──
        png_path = slides_dir / f"slide_{num:02d}.png"
        if png_path.exists():
            from PIL import Image as PILImage
            with PILImage.open(str(png_path)) as img:
                img_w, img_h = img.size
            aspect = img_h / img_w
            img_width = page_width
            img_height = img_width * aspect
            max_img_height = page_height * 0.55
            if img_height > max_img_height:
                img_height = max_img_height
                img_width = img_height / aspect
            story.append(Image(str(png_path), width=img_width, height=img_height))
            story.append(Spacer(1, 10))

        # ── AI Description ──
        if description:
            story.append(Paragraph("Opis wizualny", styles["section_label"]))
            for line in description.split("\n"):
                line = line.strip()
                if line:
                    story.append(Paragraph(line.replace("&", "&amp;").replace("<", "&lt;"), styles["body"]))
            story.append(Spacer(1, 6))

        # ── Structured text (preferred) or raw text fallback ──
        if structured_text:
            story.append(Paragraph("Treść slajdu", styles["section_label"]))
            render_structured_text(story, structured_text, styles)
            story.append(Spacer(1, 6))
        elif texts:
            story.append(Paragraph("Treść slajdu", styles["section_label"]))
            for t in texts:
                for line in t.split("\n"):
                    line = line.strip()
                    if line:
                        story.append(Paragraph(
                            line.replace("&", "&amp;").replace("<", "&lt;"),
                            styles["body"]
                        ))
            story.append(Spacer(1, 6))

        # ── Speaker notes ──
        if notes:
            story.append(Paragraph("Notatki prelegenta", styles["section_label"]))
            story.append(Paragraph(
                notes.replace("&", "&amp;").replace("<", "&lt;"),
                styles["body"]
            ))

        story.append(PageBreak())

    doc.build(story)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 execution/build_document.py <tmp_dir> [output_dir]")
        sys.exit(1)

    tmp_dir = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else (BASE / "file_converter" / "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = tmp_dir.name

    # Load extracted text
    extracted_path = tmp_dir / "extracted.json"
    if not extracted_path.exists():
        print(f"ERROR: extracted.json not found in {tmp_dir}")
        print("Run Step 1 first: python3 execution/convert_for_ai.py")
        sys.exit(1)
    slides_data = json.loads(extracted_path.read_text(encoding="utf-8"))

    # Load descriptions (written by Claude in Step 2)
    descriptions_path = tmp_dir / "descriptions.json"
    descriptions = {}
    if descriptions_path.exists():
        raw = json.loads(descriptions_path.read_text(encoding="utf-8"))
        descriptions = {
            item["slide"]: {
                "description": item.get("description", ""),
                "structured_text": item.get("structured_text", ""),
            }
            for item in raw
        }
        print(f"  Loaded {len(descriptions)} AI descriptions")
    else:
        print("  [!] descriptions.json not found — building without AI descriptions")
        print("      (Run Step 2: ask Claude to analyse slide PNGs in .tmp/{stem}/)")

    # Build PDF
    pdf_path = output_dir / f"{stem}.pdf"
    print(f"\nBuilding PDF → {pdf_path.name}")
    build_pdf(tmp_dir, pdf_path, slides_data, descriptions)
    print(f"  Done: {pdf_path}")

    print(f"\nOutput in: {output_dir}")


if __name__ == "__main__":
    main()
