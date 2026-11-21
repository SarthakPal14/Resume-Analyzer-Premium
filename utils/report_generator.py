"""Create a polished, downloadable PDF report."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Flowable
)

NAVY = colors.HexColor("#0E1A33")
BRAND = colors.HexColor("#2F5BEA")
INK = colors.HexColor("#16233B")
MUTED = colors.HexColor("#7A889E")
LINE = colors.HexColor("#E4EAF3")
GOOD, GOOD_BG = colors.HexColor("#0F8A5F"), colors.HexColor("#E6F6EF")
WARN, WARN_BG = colors.HexColor("#A5650A"), colors.HexColor("#FFF4DE")
BAD, BAD_BG = colors.HexColor("#B8404F"), colors.HexColor("#FDECEE")
PAGE_W = A4[0] - 36 * mm


class ScoreBar(Flowable):
    """Thin horizontal progress bar."""

    def __init__(self, score, width=PAGE_W, height=4 * mm):
        super().__init__()
        self.score, self.width, self.height = max(0, min(int(score), 100)), width, height

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#EDF1F8"))
        c.roundRect(0, 0.8 * mm, self.width, 2.4 * mm, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(GOOD if self.score >= 75 else (colors.HexColor("#E9A62F") if self.score >= 55 else BAD))
        w = self.width * self.score / 100
        if w > 0:
            c.roundRect(0, 0.8 * mm, max(w, 2.4 * mm), 2.4 * mm, 1.2 * mm, stroke=0, fill=1)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Resume Analyzer  ·  AI-generated coaching report, not an ATS score or hiring decision")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf_report(result: dict) -> bytes:
    analysis = result["analysis"]
    resume = result["resume_profile"]
    job = result["job_profile"]
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=20 * mm, title="Resume Analysis Report",
    )
    base = getSampleStyleSheet()
    S = {
        "kicker": ParagraphStyle("kicker", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=8,
                                 textColor=colors.HexColor("#9CC4FF"), leading=10),
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=21,
                                textColor=colors.white, alignment=0, leading=25, spaceAfter=0),
        "meta": ParagraphStyle("meta", parent=base["Normal"], fontSize=9.5, textColor=colors.HexColor("#C5D6F5"), leading=14),
        "h": ParagraphStyle("h", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, textColor=INK,
                            spaceBefore=16, spaceAfter=7, keepWithNext=1),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=9.3, leading=14, textColor=colors.HexColor("#44546F"), spaceAfter=3),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontSize=9.3, leading=14, textColor=colors.HexColor("#44546F"),
                                 leftIndent=12, bulletIndent=2, spaceAfter=3),
        "cell": ParagraphStyle("cell", parent=base["BodyText"], fontSize=8.5, leading=12, textColor=colors.HexColor("#44546F")),
        "cellb": ParagraphStyle("cellb", parent=base["BodyText"], fontSize=8.5, leading=12, textColor=INK, fontName="Helvetica-Bold"),
        "score": ParagraphStyle("score", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=30, textColor=INK,
                                alignment=1, leading=32),
        "scoresub": ParagraphStyle("scoresub", parent=base["Normal"], fontSize=8, textColor=MUTED, alignment=1),
        "small": ParagraphStyle("small", parent=base["Normal"], fontSize=8, leading=12, textColor=MUTED),
    }

    story = []

    # --- header band
    header = Table([[
        [Paragraph("RESUME ANALYZER  ·  MATCH REPORT", S["kicker"]), Spacer(1, 3),
         Paragraph("Resume &amp; Job Match Report", S["title"]), Spacer(1, 5),
         Paragraph(f"<b>Candidate:</b> {escape(resume.get('candidate_name', 'Unknown'))}"
                   f" &nbsp;&nbsp;|&nbsp;&nbsp; <b>Target role:</b> {escape(job.get('role_title', 'Not identified'))}", S["meta"])]
    ]], colWidths=[PAGE_W])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY), ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16), ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16), ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story += [header, Spacer(1, 10)]

    # --- score summary
    score = int(analysis.get("match_score", 0))
    tone, tone_bg, label = (GOOD, GOOD_BG, "Strong alignment") if score >= 80 else (
        (WARN, WARN_BG, "Promising match") if score >= 60 else (BAD, BAD_BG, "Needs improvement"))
    badge = ParagraphStyle("badge", parent=S["scoresub"], textColor=tone, fontName="Helvetica-Bold", fontSize=8.5)
    score_box = [Paragraph(f"{score}", S["score"]), Paragraph("out of 100", S["scoresub"]), Spacer(1, 4), Paragraph(label, badge)]
    summary = Table([[score_box, Paragraph(escape(analysis.get("match_summary", "")), S["body"])]],
                    colWidths=[40 * mm, PAGE_W - 40 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), tone_bg), ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F7F9FC")),
        ("BOX", (0, 0), (-1, -1), .6, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(summary)

    def add_bullets(title, items):
        block = [Paragraph(escape(title), S["h"])]
        for item in items or ["No items provided."]:
            block.append(Paragraph(escape(str(item)), S["bullet"], bulletText="•"))
        story.extend(block)

    # --- category scores
    story.append(Paragraph("Category breakdown", S["h"]))
    for item in analysis.get("category_scores", []):
        story.append(KeepTogether([
            Paragraph(f"<b>{escape(item.get('category', ''))}</b> &nbsp;<font color='#7A889E' size='8'>"
                      f"{item.get('weight_percent', 0)}% weight</font> &nbsp;&nbsp; <b>{item.get('score', 0)}/100</b>", S["body"]),
            ScoreBar(item.get("score", 0)),
            Paragraph(escape(item.get("rationale", "")), S["small"]),
            Spacer(1, 5),
        ]))

    add_bullets("Strengths", analysis.get("strengths", []))
    add_bullets("Areas to improve", analysis.get("improvement_areas", []))

    # --- skills table
    story.append(Paragraph("Skill assessment", S["h"]))
    rows = [[Paragraph(f"<font color='white'><b>{h}</b></font>", S["cell"]) for h in ("Skill", "Status", "Importance", "Evidence")]]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 1), (-1, -1), .35, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i, item in enumerate(analysis.get("skill_assessments", []), 1):
        status = item.get("status", "")
        fg, bg = (GOOD, GOOD_BG) if status == "Strong evidence" else ((WARN, WARN_BG) if status == "Partial evidence" else (BAD, BAD_BG))
        rows.append([
            Paragraph(escape(item.get("skill", "")), S["cellb"]),
            Paragraph(f"<font color='{fg.hexval().replace('0x', '#')}'><b>{escape(status)}</b></font>", S["cell"]),
            Paragraph(escape(item.get("importance", "")), S["cell"]),
            Paragraph(escape(item.get("evidence", "")), S["cell"]),
        ])
        style.append(("BACKGROUND", (1, i), (1, i), bg))
    table = Table(rows, colWidths=[34 * mm, 30 * mm, 22 * mm, PAGE_W - 86 * mm], repeatRows=1)
    table.setStyle(TableStyle(style))
    story.append(table)

    # --- rewrites
    story.append(Paragraph("Suggested bullet rewrites", S["h"]))
    for item in analysis.get("rewritten_bullets", []):
        parts = [
            Paragraph("<font color='#7A889E'><b>ORIGINAL</b></font><br/>" + escape(item.get("original", "")), S["cell"]),
            Paragraph("<font color='#0F8A5F'><b>SUGGESTED</b></font><br/>" + escape(item.get("improved", "")), S["cellb"]),
        ]
        t = Table([parts], colWidths=[PAGE_W / 2, PAGE_W / 2])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#FAFBFD")), ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F5FBF8")),
            ("BOX", (0, 0), (-1, -1), .5, LINE), ("LINEAFTER", (0, 0), (0, 0), .5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        block = [t]
        note = item.get("evidence_warning")
        if note:
            block.append(Paragraph("<b>Verify:</b> " + escape(note), S["small"]))
        block.append(Spacer(1, 7))
        story.append(KeepTogether(block))

    add_bullets("Recommended actions", analysis.get("recommended_actions", []))
    add_bullets("Interview preparation", analysis.get("interview_preparation", []))

    story.append(Paragraph("Important limitation", S["h"]))
    story.append(Paragraph(
        "This AI report is an informational coaching aid, not an official ATS score, hiring probability or "
        "employment decision. Verify every statement and suggested bullet. " + escape(analysis.get("fairness_note", "")),
        S["small"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
