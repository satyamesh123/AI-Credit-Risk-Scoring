from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.constants import RISK_COLORS, STANDARD_TO_DISPLAY, format_inr


def build_export_record(user_input: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    display_input = {
        key: value
        for key, value in user_input.items()
        if key in STANDARD_TO_DISPLAY
    }
    if "credit_amount" in display_input:
        display_input["credit_amount"] = format_inr(display_input["credit_amount"])
    record = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds"),
        **{STANDARD_TO_DISPLAY.get(key, key): value for key, value in display_input.items()},
        "Probability": round(prediction["probability"], 4),
        "Confidence %": round(prediction["confidence_percent"], 2),
        "Risk label": prediction["risk_label"],
        "Explanation": prediction["plain_english_explanation"],
        "Top contributors": " | ".join(prediction["top_contributors"]),
        "Random Forest probability": round(prediction["model_breakdown"]["random_forest"]["probability"], 4),
        "XGBoost probability": round(prediction["model_breakdown"]["xgboost"]["probability"], 4),
    }
    return record


def record_to_csv_bytes(record: dict[str, Any]) -> bytes:
    return pd.DataFrame([record]).to_csv(index=False).encode("utf-8")


def create_prediction_pdf(
    user_input: dict[str, Any],
    prediction: dict[str, Any],
    metrics: dict[str, Any],
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=colors.HexColor("#0f2942"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#23384d"),
    )
    label_style = ParagraphStyle(
        "Label",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0a6b76"),
    )

    risk_color = colors.HexColor(RISK_COLORS[prediction["risk_label"]])
    elements = [
        Paragraph("AI Credit Risk Scoring Report", title_style),
        Paragraph(
            "This report summarizes an applicant profile against the synthetic underwriting policy "
            "learned from the German credit dataset.",
            body_style,
        ),
        Spacer(1, 12),
        Table(
            [[
                Paragraph("<b>Risk Tier</b>", label_style),
                Paragraph(f"<b>{prediction['risk_label']}</b>", ParagraphStyle("risk", parent=body_style, textColor=risk_color)),
                Paragraph("<b>Confidence</b>", label_style),
                Paragraph(f"{prediction['confidence_percent']:.1f}%", body_style),
            ]],
            colWidths=[1.1 * inch, 1.2 * inch, 1.1 * inch, 1.2 * inch],
        ),
        Spacer(1, 12),
    ]

    profile_rows = [["Field", "Value"]]
    for key, value in user_input.items():
        if key not in STANDARD_TO_DISPLAY:
            continue
        if key == "credit_amount":
            value = format_inr(value)
        profile_rows.append([STANDARD_TO_DISPLAY.get(key, key), str(value)])
    profile_table = Table(profile_rows, colWidths=[2.1 * inch, 3.8 * inch])
    profile_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2942")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5fbff")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7d3de")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fbff"), colors.white]),
            ]
        )
    )
    elements.extend(
        [
            Paragraph("Applicant Profile", label_style),
            Spacer(1, 6),
            profile_table,
            Spacer(1, 14),
            Paragraph("Narrative", label_style),
            Paragraph(prediction["plain_english_explanation"], body_style),
            Spacer(1, 8),
            Paragraph("Primary Contributors", label_style),
            Paragraph("<br/>".join(f"- {item}" for item in prediction["top_contributors"]), body_style),
            Spacer(1, 12),
        ]
    )

    comparison_rows = [["Model", "AUC", "F1", "Accuracy"]]
    for model_name, values in metrics.items():
        comparison_rows.append(
            [
                model_name.replace("_", " ").title(),
                f"{values['roc_auc']:.3f}",
                f"{values['f1']:.3f}",
                f"{values['accuracy']:.3f}",
            ]
        )
    comparison_table = Table(comparison_rows, colWidths=[2.0 * inch, 1.0 * inch, 1.0 * inch, 1.1 * inch])
    comparison_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a6b76")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7d3de")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ecf9fb"), colors.white]),
            ]
        )
    )
    elements.extend([Paragraph("Model Snapshot", label_style), Spacer(1, 6), comparison_table])

    doc.build(elements)
    return buffer.getvalue()
