"""
Compiles the session's query history (question, SQL, chart, data, insights) into a
single downloadable PDF report.
"""
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
)


def build_pdf_report(entries: list, output_path: str, report_title: str = "InsightGPT Analytics Report") -> str:
    """
    entries: list of dicts, each with keys:
        question (str), sql (str), dataframe (pd.DataFrame), chart_fig (plotly Figure or None),
        insights (str)
    """
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=12, textColor=colors.HexColor("#1f2d3d"))
    body_style = styles["BodyText"]
    mono_style = ParagraphStyle("Mono", parent=styles["Code"], fontSize=8, leading=10, backColor=colors.HexColor("#f5f6fa"))

    story = [
        Paragraph(report_title, title_style),
        Paragraph(datetime.now().strftime("Generated on %B %d, %Y at %H:%M"), body_style),
        Spacer(1, 0.6 * cm),
    ]

    for i, entry in enumerate(entries, start=1):
        story.append(Paragraph(f"{i}. {entry['question']}", h2_style))

        story.append(Paragraph("SQL Query", styles["Heading4"]))
        story.append(Paragraph(entry["sql"].replace("\n", "<br/>"), mono_style))
        story.append(Spacer(1, 0.3 * cm))

        fig = entry.get("chart_fig")
        if fig is not None:
            try:
                img_bytes = fig.to_image(format="png", width=900, height=500, scale=2)
                story.append(Image(io.BytesIO(img_bytes), width=16 * cm, height=8.9 * cm))
                story.append(Spacer(1, 0.3 * cm))
            except Exception:
                pass

        df = entry.get("dataframe")
        if df is not None and not df.empty:
            story.append(Paragraph("Data (first 10 rows)", styles["Heading4"]))
            preview = df.head(10)
            table_data = [list(preview.columns)] + preview.astype(str).values.tolist()
            t = Table(table_data, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f6fa")]),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3 * cm))

        if entry.get("insights"):
            story.append(Paragraph("Business Insights", styles["Heading4"]))
            for line in entry["insights"].split("\n"):
                line = line.strip()
                if line:
                    story.append(Paragraph(line, body_style))

        if i < len(entries):
            story.append(PageBreak())

    doc.build(story)
    return output_path
