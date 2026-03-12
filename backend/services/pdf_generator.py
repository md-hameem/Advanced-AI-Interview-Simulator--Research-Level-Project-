"""
Advanced AI Interview Simulator - PDF Report Generator
Generates professional PDF assessment reports using ReportLab.
"""
import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF

logger = logging.getLogger(__name__)

# ─── Brand Colors ───────────────────────────────────────────────────────
BRAND_PRIMARY = colors.HexColor("#6366f1")
BRAND_DARK = colors.HexColor("#1e1b4b")
BRAND_LIGHT = colors.HexColor("#e0e7ff")
COLOR_SUCCESS = colors.HexColor("#22c55e")
COLOR_WARNING = colors.HexColor("#eab308")
COLOR_DANGER = colors.HexColor("#ef4444")
COLOR_MUTED = colors.HexColor("#6b7280")
COLOR_BG = colors.HexColor("#f8fafc")
COLOR_WHITE = colors.white
COLOR_BLACK = colors.HexColor("#111827")


def _score_color(score: float, max_val: float = 10) -> colors.Color:
    pct = score / max_val
    if pct >= 0.8:
        return COLOR_SUCCESS
    if pct >= 0.6:
        return colors.HexColor("#3b82f6")
    if pct >= 0.4:
        return COLOR_WARNING
    return COLOR_DANGER


def _recommendation_color(rec: str) -> colors.Color:
    r = rec.lower()
    if "strong" in r and "hire" in r:
        return COLOR_SUCCESS
    if "hire" in r and "no" not in r:
        return colors.HexColor("#3b82f6")
    return COLOR_DANGER


class PDFReportGenerator:
    """Generates a professional candidate assessment PDF."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_styles()

    def _register_styles(self):
        """Register custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            "BrandTitle",
            parent=self.styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=BRAND_DARK,
            spaceAfter=4 * mm,
        ))
        self.styles.add(ParagraphStyle(
            "BrandSubtitle",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            textColor=COLOR_MUTED,
            spaceAfter=6 * mm,
        ))
        self.styles.add(ParagraphStyle(
            "SectionHeader",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=BRAND_DARK,
            spaceBefore=8 * mm,
            spaceAfter=4 * mm,
            borderWidth=0,
            borderPadding=0,
        ))
        self.styles.add(ParagraphStyle(
            "ScoreLabel",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=COLOR_MUTED,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "ScoreValue",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "BodyText2",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=COLOR_BLACK,
            leading=14,
            spaceBefore=2 * mm,
            spaceAfter=2 * mm,
        ))
        self.styles.add(ParagraphStyle(
            "BulletItem",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=COLOR_BLACK,
            leading=14,
            leftIndent=12,
            bulletIndent=4,
        ))
        self.styles.add(ParagraphStyle(
            "FooterStyle",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=COLOR_MUTED,
            alignment=TA_CENTER,
        ))

    # ─── Public API ──────────────────────────────────────────────────

    def generate(self, report_data: dict) -> bytes:
        """Generate a PDF report and return the bytes."""
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            title=f"Interview Report - {report_data.get('candidate_name', 'Candidate')}",
            author="AI Interview Simulator",
        )

        story = []

        # Build content
        self._add_header(story, report_data)
        self._add_overall_score(story, report_data)
        self._add_score_breakdown(story, report_data)
        self._add_recommendation(story, report_data)
        self._add_strengths_weaknesses(story, report_data)
        self._add_question_breakdown(story, report_data)
        self._add_detailed_feedback(story, report_data)
        self._add_footer(story)

        doc.build(story)
        return buffer.getvalue()

    # ─── Section Builders ────────────────────────────────────────────

    def _add_header(self, story: list, data: dict):
        """Title block with candidate info."""
        # Decorative line
        story.append(HRFlowable(
            width="100%", thickness=3, color=BRAND_PRIMARY,
            spaceBefore=0, spaceAfter=4 * mm,
        ))

        story.append(Paragraph("Candidate Assessment Report", self.styles["BrandTitle"]))

        info_parts = []
        if data.get("candidate_name"):
            info_parts.append(f"<b>Candidate:</b> {data['candidate_name']}")
        if data.get("target_role"):
            info_parts.append(f"<b>Role:</b> {data['target_role']}")
        if data.get("interview_type"):
            info_parts.append(f"<b>Type:</b> {data['interview_type'].replace('_', ' ').title()}")
        info_parts.append(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}")

        story.append(Paragraph(" &nbsp;|&nbsp; ".join(info_parts), self.styles["BrandSubtitle"]))

        story.append(HRFlowable(
            width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"),
            spaceAfter=6 * mm,
        ))

    def _add_overall_score(self, story: list, data: dict):
        """Big overall score display."""
        score = data.get("overall_score", 0)
        color = _score_color(score, 10)

        # Build a colored score box
        score_table = Table(
            [[
                Paragraph(f"<font size='32' color='{color.hexval()}'><b>{score:.1f}</b></font>"
                          f"<font size='14' color='#9ca3af'>/10</font>",
                          ParagraphStyle("s", alignment=TA_CENTER, parent=self.styles["Normal"])),
            ]],
            colWidths=[120],
            rowHeights=[60],
        )
        score_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG),
            ("ROUNDEDCORNERS", [8, 8, 8, 8]),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ]))

        # Center it using a wrapper table
        wrapper = Table([[score_table]], colWidths=[doc_width()])
        wrapper.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        story.append(wrapper)
        story.append(Spacer(1, 4 * mm))

    def _add_score_breakdown(self, story: list, data: dict):
        """Category scores in a row."""
        story.append(Paragraph("Score Breakdown", self.styles["SectionHeader"]))

        categories = [
            ("Technical", data.get("technical_score", 0), 5),
            ("Communication", data.get("communication_score", 0), 5),
            ("Problem Solving", data.get("problem_solving_score", 0), 5),
        ]

        header_row = []
        score_row = []
        bar_row = []

        for label, score, max_val in categories:
            color = _score_color(score, max_val)
            header_row.append(Paragraph(label, self.styles["ScoreLabel"]))
            score_row.append(Paragraph(
                f"<font color='{color.hexval()}'><b>{score:.1f}</b></font>"
                f"<font size='9' color='#9ca3af'>/{max_val}</font>",
                ParagraphStyle("sv", alignment=TA_CENTER, fontSize=16,
                               fontName="Helvetica-Bold", parent=self.styles["Normal"]),
            ))

            # Visual bar
            pct = min(score / max_val, 1.0)
            d = Drawing(100, 8)
            d.add(Rect(0, 0, 100, 8, fillColor=colors.HexColor("#e5e7eb"), strokeColor=None))
            d.add(Rect(0, 0, 100 * pct, 8, fillColor=color, strokeColor=None))
            bar_row.append(d)

        col_w = doc_width() / 3
        t = Table([header_row, score_row, bar_row], colWidths=[col_w] * 3)
        t.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("LINEABOVE", (0, 1), (-1, 1), 0.5, colors.HexColor("#e5e7eb")),
            ("LINEABOVE", (0, 2), (-1, 2), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    def _add_recommendation(self, story: list, data: dict):
        """Hiring recommendation badge."""
        rec = data.get("recommendation", "N/A")
        color = _recommendation_color(rec)
        display = rec.replace("_", " ").upper()

        t = Table(
            [[Paragraph(
                f"<font color='{COLOR_WHITE.hexval()}'><b>{display}</b></font>",
                ParagraphStyle("rec", alignment=TA_CENTER, fontSize=12,
                               fontName="Helvetica-Bold", parent=self.styles["Normal"]),
            )]],
            colWidths=[180],
            rowHeights=[32],
        )
        t.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), color),
            ("ROUNDEDCORNERS", [16, 16, 16, 16]),
        ]))
        wrapper = Table([[t]], colWidths=[doc_width()])
        wrapper.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        story.append(wrapper)
        story.append(Spacer(1, 6 * mm))

    def _add_strengths_weaknesses(self, story: list, data: dict):
        """Two-column strengths & weaknesses."""
        strengths = data.get("strengths", [])
        weaknesses = data.get("weaknesses", [])

        if not strengths and not weaknesses:
            return

        story.append(Paragraph("Strengths &amp; Areas for Improvement", self.styles["SectionHeader"]))

        left_items = []
        for s in strengths[:6]:
            left_items.append(Paragraph(f"<font color='#16a34a'>✓</font> {s}", self.styles["BulletItem"]))

        right_items = []
        for w in weaknesses[:6]:
            right_items.append(Paragraph(f"<font color='#dc2626'>△</font> {w}", self.styles["BulletItem"]))

        # Pad to same length
        max_len = max(len(left_items), len(right_items), 1)
        while len(left_items) < max_len:
            left_items.append(Spacer(1, 0))
        while len(right_items) < max_len:
            right_items.append(Spacer(1, 0))

        col_w = doc_width() / 2 - 4
        rows = []
        rows.append([
            Paragraph("<b>Strengths</b>", ParagraphStyle("sh", fontSize=10, textColor=COLOR_SUCCESS, fontName="Helvetica-Bold", parent=self.styles["Normal"])),
            Paragraph("<b>Areas for Improvement</b>", ParagraphStyle("wh", fontSize=10, textColor=COLOR_DANGER, fontName="Helvetica-Bold", parent=self.styles["Normal"])),
        ])
        for i in range(max_len):
            rows.append([left_items[i], right_items[i]])

        t = Table(rows, colWidths=[col_w, col_w])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#e5e7eb")),
            ("LINEAFTER", (0, 0), (0, -1), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    def _add_question_breakdown(self, story: list, data: dict):
        """Table of per-question scores."""
        q_scores = data.get("question_scores", [])
        if not q_scores:
            return

        story.append(Paragraph("Question-by-Question Breakdown", self.styles["SectionHeader"]))

        header = ["#", "Type", "Score", "Correct.", "Depth", "Clarity", "Reason."]
        rows = [header]

        for i, qs in enumerate(q_scores):
            question_text = qs.get("question", "")
            q_type = qs.get("type", "N/A")
            score = qs.get("score", 0)
            rows.append([
                str(i + 1),
                q_type[:15],
                f"{score:.1f}/10",
                f"{qs.get('correctness', 0):.1f}",
                f"{qs.get('depth', 0):.1f}",
                f"{qs.get('clarity', 0):.1f}",
                f"{qs.get('reasoning', 0):.1f}",
            ])

        col_widths = [20, 65, 50, 48, 42, 42, 48]
        t = Table(rows, colWidths=col_widths)
        t.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # Body
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_WHITE, COLOR_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ]))
        story.append(t)
        story.append(Spacer(1, 4 * mm))

    def _add_detailed_feedback(self, story: list, data: dict):
        """Detailed text feedback section."""
        feedback = data.get("detailed_feedback", "")
        if not feedback:
            return

        story.append(Paragraph("Detailed Feedback", self.styles["SectionHeader"]))

        # Split by line breaks and render each paragraph
        for para in feedback.split("\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, self.styles["BodyText2"]))

        study_recs = data.get("study_recommendations", [])
        if study_recs:
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph("<b>Study Recommendations</b>", self.styles["BodyText2"]))
            for rec in study_recs:
                story.append(Paragraph(f"• {rec}", self.styles["BulletItem"]))

    def _add_footer(self, story: list):
        """Footer with branding."""
        story.append(Spacer(1, 10 * mm))
        story.append(HRFlowable(
            width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"),
            spaceAfter=3 * mm,
        ))
        story.append(Paragraph(
            f"Generated by <b>AI Interview Simulator</b> on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            " &nbsp;|&nbsp; This is an AI-generated assessment.",
            self.styles["FooterStyle"],
        ))


def doc_width():
    """Usable width of an A4 page with our margins."""
    return A4[0] - 36 * mm


# Singleton
pdf_generator = PDFReportGenerator()
