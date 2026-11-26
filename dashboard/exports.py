from __future__ import annotations

from copy import copy
from io import BytesIO
from typing import Mapping

import pandas as pd
from openpyxl.styles import PatternFill
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from dashboard.analytics import (
    calculate_kpis,
    credit_risk_summary,
    customer_city_summary,
    loan_status_summary,
    transaction_type_summary,
)
from dashboard.data import BankingData

REPORT_NAVY = colors.HexColor("#101A27")
REPORT_PALE = colors.HexColor("#EAF3F2")
REPORT_TEXT = colors.HexColor("#263446")


def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8-sig")


def excel_report_bytes(
    data: BankingData,
    filter_summary: Mapping[str, str],
    customer_reference: pd.DataFrame | None = None,
) -> bytes:
    output = BytesIO()
    kpis = calculate_kpis(data)
    customer_reference = customer_reference if customer_reference is not None else data.customers
    kpi_rows = [
        ("Total customers", kpis.total_customers),
        ("Total transactions", kpis.total_transactions),
        ("Total deposits (successful)", kpis.total_deposits),
        ("Total withdrawals (successful)", kpis.total_withdrawals),
        ("Total loan amount", kpis.total_loan_amount),
        ("Loan count", kpis.total_loans),
        (
            "Loan default rate (%)",
            kpis.loan_default_rate if kpis.loan_default_rate is not None else "N/A",
        ),
    ]

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(kpi_rows, columns=["Metric", "Value"]).to_excel(
            writer, sheet_name="Overview", index=False
        )
        pd.DataFrame(
            list(filter_summary.items()), columns=["Filter", "Selection"]
        ).to_excel(writer, sheet_name="Filters", index=False)
        data.customers.to_excel(writer, sheet_name="Customers", index=False)
        data.transactions.to_excel(writer, sheet_name="Transactions", index=False)
        data.loans.to_excel(writer, sheet_name="Loans", index=False)
        customer_city_summary(data.customers).to_excel(
            writer, sheet_name="Customer Analytics", index=False
        )
        transaction_type_summary(data.transactions).to_excel(
            writer, sheet_name="Transaction Analytics", index=False
        )
        loan_status_summary(data.loans).to_excel(
            writer, sheet_name="Loan Analytics", index=False
        )
        credit_risk_summary(customer_reference, data.loans).to_excel(
            writer, sheet_name="Credit Risk", index=False
        )

        for worksheet in writer.sheets.values():
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                max_length = max(
                    (
                        len(str(cell.value))
                        for cell in column_cells
                        if cell.value is not None
                    ),
                    default=0,
                )
                worksheet.column_dimensions[
                    column_cells[0].column_letter
                ].width = min(max_length + 3, 36)
            for cell in worksheet[1]:
                font = copy(cell.font)
                font.bold = True
                font.color = "FFFFFF"
                cell.font = font
                cell.fill = PatternFill(fill_type="solid", fgColor="17283A")

    return output.getvalue()


def pdf_report_bytes(
    data: BankingData,
    filter_summary: Mapping[str, str],
    customer_reference: pd.DataFrame | None = None,
) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Banking Financial Analytics Report",
        author="Banking Financial Analytics Dashboard",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BankingReportTitle",
            parent=styles["Title"],
            textColor=REPORT_NAVY,
            alignment=TA_LEFT,
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BankingReportSection",
            parent=styles["Heading2"],
            textColor=REPORT_NAVY,
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=12,
            spaceAfter=6,
        )
    )

    kpis = calculate_kpis(data)
    customer_reference = customer_reference if customer_reference is not None else data.customers
    default_rate = (
        f"{kpis.loan_default_rate:.2f}%"
        if kpis.loan_default_rate is not None
        else "N/A"
    )
    story = [
        Paragraph("Banking Financial Analytics", styles["BankingReportTitle"]),
        Paragraph("Portfolio performance and risk summary", styles["Normal"]),
        Spacer(1, 8),
        Paragraph("Applied filters", styles["BankingReportSection"]),
        _pdf_table(
            [["Filter", "Selection"], *filter_summary.items()],
            widths=[45 * mm, 125 * mm],
        ),
        Paragraph("Key performance indicators", styles["BankingReportSection"]),
        _pdf_table(
            [
                ["Metric", "Value"],
                ["Total customers", f"{kpis.total_customers:,}"],
                ["Total transactions", f"{kpis.total_transactions:,}"],
                ["Total deposits (successful)", _inr(kpis.total_deposits)],
                ["Total withdrawals (successful)", _inr(kpis.total_withdrawals)],
                ["Total loan amount", _inr(kpis.total_loan_amount)],
                ["Loan count", f"{kpis.total_loans:,}"],
                ["Loan default rate", default_rate],
            ],
            widths=[95 * mm, 75 * mm],
        ),
        Paragraph("Transaction activity", styles["BankingReportSection"]),
        _summary_table(
            transaction_type_summary(data.transactions),
            [
                "transaction_type",
                "total_transactions",
                "successful_transactions",
                "successful_amount",
            ],
            ["Type", "Transactions", "Successful", "Successful amount (INR)"],
            ["successful_amount"],
        ),
        Paragraph("Loan portfolio", styles["BankingReportSection"]),
        _summary_table(
            loan_status_summary(data.loans),
            [
                "loan_status",
                "loan_count",
                "total_loan_amount",
                "average_interest_rate",
            ],
            ["Status", "Loans", "Loan amount (INR)", "Average rate (%)"],
            ["total_loan_amount"],
        ),
        Paragraph("Credit risk by credit score band", styles["BankingReportSection"]),
        _summary_table(
            credit_risk_summary(customer_reference, data.loans),
            ["credit_category", "loan_count", "default_count", "default_rate"],
            ["Credit score band", "Loans", "Defaults", "Default rate (%)"],
            [],
        ),
        Spacer(1, 8),
        Paragraph(
            "Amounts follow the existing project INR reporting convention. "
            "Deposit and withdrawal values include successful transactions only.",
            styles["BodyText"],
        ),
    ]
    document.build(story)
    return output.getvalue()


def _pdf_table(rows: list[list[object]], widths: list[float]) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), REPORT_NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 1), (-1, -1), REPORT_TEXT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, REPORT_PALE]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E0E7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _summary_table(
    frame: pd.DataFrame,
    columns: list[str],
    labels: list[str],
    amount_columns: list[str],
) -> Table:
    rows: list[list[object]] = [labels]
    for row in frame[columns].itertuples(index=False, name=None):
        rendered: list[object] = []
        for column, value in zip(columns, row):
            if pd.isna(value):
                rendered.append("N/A")
            elif column in amount_columns:
                rendered.append(f"{float(value):,.2f}")
            elif column in {"default_rate", "average_interest_rate"}:
                rendered.append(f"{float(value):.2f}")
            elif isinstance(value, float):
                rendered.append(f"{value:,.2f}")
            else:
                rendered.append(str(value))
        rows.append(rendered)
    if len(rows) == 1:
        rows.append(["No matching records"] + [""] * (len(labels) - 1))

    available_width = 176 * mm
    widths = [available_width / len(labels)] * len(labels)
    return _pdf_table(rows, widths)


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"
