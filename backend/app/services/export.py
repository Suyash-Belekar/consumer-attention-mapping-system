import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os


def export_excel(data, filename="report.xlsx"):
    """Export analytics data to Excel file"""

    # Sheet 1 - Product Scores
    scores_df = pd.DataFrame(data["scores"])

    # Sheet 2 - Shopper Segments
    segments_df = pd.DataFrame(data["segments"])

    # Sheet 3 - Recommendations
    recommendations_df = pd.DataFrame(data["recommendations"])

    # Sheet 4 - Alerts
    alerts_df = pd.DataFrame(data["alerts"])

    # Write to Excel with multiple sheets
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        scores_df.to_excel(writer, sheet_name="Product Scores", index=False)
        segments_df.to_excel(writer, sheet_name="Shopper Segments", index=False)
        recommendations_df.to_excel(writer, sheet_name="Recommendations", index=False)
        alerts_df.to_excel(writer, sheet_name="Alerts", index=False)

    print(f"Excel report saved to {filename}")
    return filename


def export_pdf(data, filename="report.pdf"):
    """Export analytics data to PDF file"""

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("Consumer Attention Mapping System - Analytics Report", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 20))

    # Product Scores Section
    story.append(Paragraph("Product Attractiveness Scores", styles["Heading1"]))
    story.append(Spacer(1, 10))

    score_table_data = [["Product", "Score", "Rating"]]
    for item in data["scores"]:
        score_table_data.append([item["product"], str(item["score"]), item["rating"]])

    score_table = Table(score_table_data, colWidths=[200, 100, 100])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f2f5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 20))

    # Recommendations Section
    story.append(Paragraph("Product Recommendations", styles["Heading1"]))
    story.append(Spacer(1, 10))

    rec_table_data = [["Product", "Issue", "Priority"]]
    for item in data["recommendations"]:
        rec_table_data.append([item["product"], item["issue"], item["priority"]])

    rec_table = Table(rec_table_data, colWidths=[150, 250, 100])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e94560")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f2f5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 20))

    # Alerts Section
    story.append(Paragraph("Product Alerts", styles["Heading1"]))
    story.append(Spacer(1, 10))

    alerts_table_data = [["Type", "Product", "Action"]]
    for item in data["alerts"]:
        alerts_table_data.append([item["type"], item["product"], item["action"]])

    alerts_table = Table(alerts_table_data, colWidths=[100, 150, 250])
    alerts_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f2f5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(alerts_table)

    doc.build(story)
    print(f"PDF report saved to {filename}")
    return filename


if __name__ == "__main__":
    test_data = {
        "scores": [
            {"product": "Coca Cola", "score": 100, "rating": "Excellent"},
            {"product": "Maggi Noodles", "score": 96, "rating": "Excellent"},
            {"product": "Lays Chips", "score": 93, "rating": "Excellent"},
            {"product": "Bread", "score": 53, "rating": "Average"},
            {"product": "Amul Butter", "score": 31, "rating": "Poor"},
        ],
        "segments": [
            {"shopper_id": 1, "segment": "Explorer", "dwell_time": 90},
            {"shopper_id": 2, "segment": "Quick Buyer", "dwell_time": 20},
            {"shopper_id": 3, "segment": "Comparison Shopper", "dwell_time": 60},
        ],
        "recommendations": [
            {"product": "Lays Chips", "issue": "High Attention but Low Sales", "priority": "High"},
            {"product": "Amul Butter", "issue": "Low Shelf Visibility", "priority": "High"},
            {"product": "Bread", "issue": "Low Customer Engagement", "priority": "Medium"},
        ],
        "alerts": [
            {"type": "CRITICAL", "product": "Amul Butter", "action": "Review shelf placement immediately"},
            {"type": "WARNING", "product": "Bread", "action": "Consider repositioning"},
            {"type": "SUCCESS", "product": "Coca Cola", "action": "Maintain current position"},
        ]
    }

    export_excel(test_data, "test_report.xlsx")
    export_pdf(test_data, "test_report.pdf")