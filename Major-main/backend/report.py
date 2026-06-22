"""
Report Generator
────────────────
Produces a structured decision report as JSON or PDF.
PDF uses reportlab for a clean, professional layout.
"""

from __future__ import annotations
import json
import io
from datetime import datetime
from typing import Any

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


STATUS_COLOR = {
    "pass": "✅", "fail": "❌", "warn": "⚠️",
    "move": "✅", "stay": "🔴", "investigate": "🟡",
    "justified": "✅", "not_justified": "🔴", "marginal": "🟡",
    "approved": "✅", "provisioned": "🚀", "rejected": "🔴", "pending": "⏳",
}


def build_json_report(
    decision: dict,
    company: dict,
    asset: dict,
    cost_model: dict | None,
    compliance_summary: dict,
    audit_logs: list[dict],
) -> dict[str, Any]:
    return {
        "report_type": "Cloud Agility Broker — Decision Report",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "decision": decision,
        "company": company,
        "data_asset": asset,
        "compliance": compliance_summary,
        "cost_analysis": cost_model,
        "audit_trail": audit_logs,
    }


def build_pdf_report(
    decision: dict,
    company: dict,
    asset: dict,
    cost_model: dict | None,
    compliance_summary: dict,
    audit_logs: list[dict],
) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab is not installed")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # ── Title ─────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1a1a2e")
    )
    subtitle_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.grey, spaceAfter=12
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#16213e"), spaceBefore=14, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, leading=14
    )

    story.append(Paragraph("Cloud Agility Broker", title_style))
    story.append(Paragraph("Automated Cloud Migration Decision Report", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')} &nbsp;|&nbsp; "
        f"Decision ID: {decision.get('id', 'N/A')}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")))
    story.append(Spacer(1, 0.4 * cm))

    # ── Summary Box ───────────────────────────────────────────────────────────
    rec = decision.get("recommendation", "N/A").upper()
    comp = decision.get("compliance_status", "N/A").upper()
    cost_st = decision.get("cost_status", "N/A").upper()

    summary_data = [
        ["Field", "Value"],
        ["Company", company.get("name", "N/A")],
        ["Data Asset", asset.get("name", "N/A")],
        ["Data Class", asset.get("data_class", "N/A")],
        ["Source Cloud", decision.get("source_cloud", "N/A").upper()],
        ["Target Cloud", decision.get("target_cloud", "N/A").upper()],
        ["Recommendation", rec],
        ["Compliance Status", comp],
        ["Cost Justification", cost_st],
        ["Decision Status", decision.get("status", "N/A").upper()],
    ]

    summary_table = Table(summary_data, colWidths=[5 * cm, 12 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Rationale ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Decision Rationale", h2_style))
    story.append(Paragraph(decision.get("rationale", "No rationale provided."), body_style))
    story.append(Spacer(1, 0.3 * cm))

    # ── Compliance ────────────────────────────────────────────────────────────
    story.append(Paragraph("Compliance Evaluation", h2_style))
    checks = compliance_summary.get("checks", [])
    if checks:
        comp_data = [["Rule ID", "Rule Name", "Severity", "Status", "Explanation"]]
        for c in checks:
            comp_data.append([
                c.get("rule_id", ""),
                c.get("rule_name", "")[:30],
                c.get("severity", "").upper(),
                c.get("status", "").upper(),
                c.get("explanation", "")[:60],
            ])
        comp_table = Table(comp_data, colWidths=[2 * cm, 4 * cm, 2 * cm, 1.8 * cm, 7.2 * cm])
        comp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 5),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(comp_table)
    story.append(Spacer(1, 0.3 * cm))

    # ── Cost Analysis ─────────────────────────────────────────────────────────
    if cost_model:
        story.append(Paragraph("Cost Analysis", h2_style))
        cost_rows = [
            ["Current Monthly Cost", f"${cost_model.get('current_monthly_cost', 0):,.2f}"],
            ["Target Monthly Cost",  f"${cost_model.get('target_monthly_cost', 0):,.2f}"],
            ["Monthly Savings",      f"${cost_model.get('monthly_savings', 0):,.2f}"],
            ["Data Egress Cost",     f"${cost_model.get('egress_cost', 0):,.2f}"],
            ["Exit Penalty",         f"${cost_model.get('exit_penalty', 0):,.2f}"],
            ["Engineering Labour",   f"${cost_model.get('engineering_effort_cost', 0):,.2f}"],
            ["Downtime Risk",        f"${cost_model.get('downtime_risk_cost', 0):,.2f}"],
            ["Total Migration Cost", f"${cost_model.get('total_migration_cost', 0):,.2f}"],
            ["Breakeven",            f"{cost_model.get('breakeven_months', 'N/A')} months"],
            ["3-Year Net Benefit",   f"${cost_model.get('three_year_net', 0):,.2f}"],
        ]
        cost_table = Table(cost_rows, colWidths=[7 * cm, 5 * cm])
        cost_table.setStyle(TableStyle([
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Audit Trail ───────────────────────────────────────────────────────────
    story.append(Paragraph("Audit Trail", h2_style))
    if audit_logs:
        audit_data = [["Timestamp", "Event", "Actor"]]
        for log in audit_logs[:20]:
            ts = log.get("timestamp", "")
            if hasattr(ts, "strftime"):
                ts = ts.strftime("%Y-%m-%d %H:%M:%S")
            audit_data.append([
                str(ts)[:19],
                log.get("event_type", "").replace("_", " ").title(),
                log.get("actor", "system"),
            ])
        audit_table = Table(audit_data, colWidths=[5 * cm, 9 * cm, 3 * cm])
        audit_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(audit_table)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Paragraph(
        "This report was generated automatically by Cloud Agility Broker. "
        "It is intended for audit, legal, and engineering review purposes.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7, textColor=colors.grey)
    ))

    doc.build(story)
    return buffer.getvalue()
