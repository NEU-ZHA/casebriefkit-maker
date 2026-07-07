#!/usr/bin/env python3
"""Build a public preview PDF for the possible CaseBriefKit template pack."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "downloads"
PDF_PATH = DOWNLOADS / "casebriefkit-template-pack-preview.pdf"

PACK_ITEMS = [
    (
        "Case brief template",
        "Fillable DOCX and printable PDF for facts, issue, rule, analysis, holding, reasoning, and class notes.",
    ),
    (
        "Class notes and outline template",
        "Connect assigned cases with doctrine, professor questions, and later outline material.",
    ),
    (
        "Completed fictional example",
        "A worked sample so students can compare a blank form with a finished brief.",
    ),
    (
        "Cold-call prep sheet",
        "A compact page for facts, posture, holding, reasoning, and likely follow-up questions.",
    ),
    (
        "IRAC / FIRAC / CREAC quick templates",
        "Short structures for different class habits and professor preferences.",
    ),
    (
        "Issue spotting checklist",
        "A bridge from daily case reading to exam-style issue recognition.",
    ),
    (
        "Professor preference adapter",
        "A simple sheet for recording what a professor rewards or dislikes in briefs.",
    ),
    (
        "Google Docs copy helper",
        "A quick-copy structure for students who prefer cloud documents over local Word files.",
    ),
]


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


def build_pdf() -> None:
    DOWNLOADS.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=0.68 * inch,
        leftMargin=0.68 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="CaseBriefKit Template Pack Preview",
        author="CaseBriefKit",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "PreviewTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#17211F"),
        alignment=1,
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "PreviewSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#34413D"),
        alignment=1,
        spaceAfter=14,
    )
    heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1F6F5B"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#34413D"),
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#5D6864"),
    )
    card_title = ParagraphStyle(
        "CardTitle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=11,
        textColor=colors.HexColor("#17211F"),
        spaceAfter=2,
    )
    card_body = ParagraphStyle(
        "CardBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=10.5,
        textColor=colors.HexColor("#34413D"),
    )

    story = [
        paragraph("CaseBriefKit Template Pack Preview", title),
        paragraph(
            "A public preview of possible editable DOCX and printable PDF study files for law school case briefs.",
            subtitle,
        ),
        paragraph("What this preview is", heading),
        paragraph(
            "This is not the full pack and it is not a purchase receipt. It shows the file types being tested so students can decide whether the expanded set would save enough time to request.",
            body,
        ),
        Spacer(1, 10),
        paragraph("Possible pack contents", heading),
    ]

    rows = []
    for index in range(0, len(PACK_ITEMS), 2):
        row = []
        for title_text, description in PACK_ITEMS[index : index + 2]:
            row.append(
                [
                    paragraph(title_text, card_title),
                    paragraph(description, card_body),
                ]
            )
        rows.append(row)

    table = Table(rows, colWidths=[3.35 * inch, 3.35 * inch], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAF8")),
                ("BOX", (0, 0), (-1, -1), 0.65, colors.HexColor("#D6DDD9")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6DDD9")),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([table, Spacer(1, 12)])

    story.extend(
        [
            paragraph("Free sample vs. expanded pack", heading),
            paragraph(
                "The free sample is a single one-page case brief form. The expanded pack would add multiple study templates, examples, and class workflow sheets if real students request it.",
                body,
            ),
            Spacer(1, 10),
            paragraph("How to signal interest", heading),
            paragraph(
                "Try the free DOCX or PDF first, then use the template pack interest form on the website if these files would be useful enough to buy later.",
                body,
            ),
            Spacer(1, 12),
            paragraph(
                "CaseBriefKit is an educational writing aid for law students. It is not legal advice. Do not send private study records, school IDs, or sensitive personal information through public feedback links.",
                small,
            ),
        ]
    )

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(PDF_PATH)
