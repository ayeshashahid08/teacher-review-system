import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

REPORT_DIR = "generated_reports"


def generate_monthly_report_pdf(report_data: dict) -> str:
    os.makedirs(REPORT_DIR, exist_ok=True)
    filename = f"{REPORT_DIR}/report_{report_data['report_id']}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    # Style for wrapped table cell text
    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
    )
    header_style = ParagraphStyle(
        "CellHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
    )

    elements = []

    elements.append(Paragraph(f"Monthly Performance Report", styles["Title"]))
    elements.append(Paragraph(
        f"{report_data['teacher_name']} — {report_data['month']}/{report_data['year']}",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    summary_table_data = [
        ["Total Observations", str(report_data["total_observations"])],
        ["Average Score", f"{report_data['average_score']:.2f}" if report_data["average_score"] is not None else "N/A"],
        ["Status", report_data["status"]],
    ]
    summary_table = Table(summary_table_data, colWidths=[6 * cm, 6 * cm])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.7 * cm))

    elements.append(Paragraph("MCQ Response Percentages", styles["Heading3"]))

    # Wrap each cell's text in a Paragraph so long question text
    # wraps inside the column instead of overflowing into the next one.
    mcq_table_data = [
        [Paragraph("Question", header_style), Paragraph("Score %", header_style)]
    ]
    for item in report_data["mcq_percentages"]:
        mcq_table_data.append([
            Paragraph(item["question_text"], cell_style),
            Paragraph(f"{item['response_percentage']}%", cell_style),
        ])

    # Slightly narrower question column + wider score column,
    # and let the table size itself to the page width.
    mcq_table = Table(mcq_table_data, colWidths=[13 * cm, 3 * cm])
    mcq_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(mcq_table)
    elements.append(Spacer(1, 0.7 * cm))

    elements.append(Paragraph("AI Feedback Summary", styles["Heading3"]))
    elements.append(Paragraph(report_data["ai_suggestions"] or "No AI feedback available.", styles["BodyText"]))
    elements.append(Spacer(1, 0.5 * cm))

    if report_data.get("human_suggestions"):
        elements.append(Paragraph("Principal's Notes", styles["Heading3"]))
        elements.append(Paragraph(report_data["human_suggestions"], styles["BodyText"]))
        elements.append(Spacer(1, 0.5 * cm))

    if report_data.get("approved_by_name"):
        elements.append(Paragraph(
            f"Approved by {report_data['approved_by_name']} on {report_data['approved_at']}",
            styles["Italic"]
        ))

    doc.build(elements)
    return filename
# import os
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet

# REPORT_DIR = "generated_reports"


# def generate_monthly_report_pdf(report_data: dict) -> str:
#     os.makedirs(REPORT_DIR, exist_ok=True)
#     filename = f"{REPORT_DIR}/report_{report_data['report_id']}.pdf"

#     doc = SimpleDocTemplate(filename, pagesize=A4)
#     styles = getSampleStyleSheet()
#     elements = []

#     elements.append(Paragraph(f"Monthly Performance Report", styles["Title"]))
#     elements.append(Paragraph(
#         f"{report_data['teacher_name']} — {report_data['month']}/{report_data['year']}",
#         styles["Heading2"]
#     ))
#     elements.append(Spacer(1, 0.5 * cm))

#     summary_table_data = [
#         ["Total Observations", str(report_data["total_observations"])],
#         ["Average Score", f"{report_data['average_score']:.2f}" if report_data["average_score"] is not None else "N/A"],
#         ["Status", report_data["status"]],
#     ]
#     summary_table = Table(summary_table_data, colWidths=[6 * cm, 6 * cm])
#     summary_table.setStyle(TableStyle([
#         ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
#     ]))
#     elements.append(summary_table)
#     elements.append(Spacer(1, 0.7 * cm))

#     elements.append(Paragraph("MCQ Response Percentages", styles["Heading3"]))
#     mcq_table_data = [["Question", "Score %"]]
#     for item in report_data["mcq_percentages"]:
#         mcq_table_data.append([item["question_text"], f"{item['response_percentage']}%"])
#     mcq_table = Table(mcq_table_data, colWidths=[10 * cm, 3 * cm])
#     mcq_table.setStyle(TableStyle([
#         ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
#         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#     ]))
#     elements.append(mcq_table)
#     elements.append(Spacer(1, 0.7 * cm))

#     elements.append(Paragraph("AI Feedback Summary", styles["Heading3"]))
#     elements.append(Paragraph(report_data["ai_suggestions"] or "No AI feedback available.", styles["BodyText"]))
#     elements.append(Spacer(1, 0.5 * cm))

#     if report_data.get("human_suggestions"):
#         elements.append(Paragraph("Principal's Notes", styles["Heading3"]))
#         elements.append(Paragraph(report_data["human_suggestions"], styles["BodyText"]))
#         elements.append(Spacer(1, 0.5 * cm))

#     if report_data.get("approved_by_name"):
#         elements.append(Paragraph(
#             f"Approved by {report_data['approved_by_name']} on {report_data['approved_at']}",
#             styles["Italic"]
#         ))

#     doc.build(elements)
#     return filename