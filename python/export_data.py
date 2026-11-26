
import pandas as pd
import os
from openpyxl.chart import BarChart, Reference

# Dataset files load karna
customers = pd.read_csv("dataset/customers.csv")
transactions = pd.read_csv("dataset/transactions.csv")
loans = pd.read_csv("dataset/loans.csv")

# Date columns convert karna
customers["join_date"] = pd.to_datetime(customers["join_date"])
transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
loans["loan_date"] = pd.to_datetime(loans["loan_date"])

# Reports folder
os.makedirs("reports", exist_ok=True)

# Excel workbook create karna
output_file = "reports/Banking_Financial_Analytics.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

    # Raw data sheets
    customers.to_excel(writer, sheet_name="Customers", index=False)
    transactions.to_excel(writer, sheet_name="Transactions", index=False)
    loans.to_excel(writer, sheet_name="Loans", index=False)

    # Transaction summary
    transaction_summary = transactions.groupby("transaction_type").agg(
        total_transactions=("transaction_id", "count"),
        total_amount=("amount", "sum"),
        average_amount=("amount", "mean")
    ).reset_index()

    transaction_summary.to_excel(
        writer, sheet_name="Transaction Summary", index=False
    )

    # Loan summary
    loan_summary = loans.groupby("loan_status").agg(
        total_loans=("loan_id", "count"),
        total_loan_amount=("loan_amount", "sum"),
        average_interest_rate=("interest_rate_pct", "mean")
    ).reset_index()

    loan_summary.to_excel(
        writer, sheet_name="Loan Summary", index=False
    )

    # City analysis
    city_analysis = customers.merge(
        transactions, on="customer_id"
    ).groupby("city").agg(
        total_transactions=("transaction_id", "count"),
        total_transaction_amount=("amount", "sum"),
        average_transaction_amount=("amount", "mean")
    ).reset_index()

    city_analysis.to_excel(
        writer, sheet_name="City Analysis", index=False
    )

    # Credit risk analysis
    credit_risk = customers.merge(
        loans, on="customer_id"
    )

    credit_risk["credit_category"] = pd.cut(
        credit_risk["credit_score"],
        bins=[0, 650, 700, 750, 850],
        labels=["Low", "Average", "Good", "Excellent"]
    )

    risk_summary = credit_risk.groupby(
        "credit_category", observed=False
    ).agg(
        total_loans=("loan_id", "count"),
        default_loans=("loan_status", lambda x: (x == "Default").sum())
    ).reset_index()

    risk_summary["default_percentage"] = (
        risk_summary["default_loans"] /
        risk_summary["total_loans"] * 100
    ).round(2)

    risk_summary.to_excel(
        writer, sheet_name="Credit Risk", index=False
    )

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Generated Excel workbook open karna
wb = load_workbook(output_file)

for ws in wb.worksheets:

    # Header formatting
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="1F4E78",
            end_color="1F4E78",
            fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center")

    # Freeze first row and enable filters
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

        for cell in column:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[column_letter].width = min(max_length + 3, 30)

# Transaction Count Chart
ws = wb["Transaction Summary"]

chart = BarChart()
chart.type = "col"
chart.style = 10
chart.title = "Transaction Count by Type"
chart.x_axis.title = "Transaction Type"
chart.y_axis.title = "Number of Transactions"

data = Reference(
    ws,
    min_col=2,
    min_row=1,
    max_row=5
)

categories = Reference(
    ws,
    min_col=1,
    min_row=2,
    max_row=5
)

chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)

chart.height = 10
chart.width = 18

ws.add_chart(chart, "F2")


# Loan Status Chart
ws = wb["Loan Summary"]

loan_chart = BarChart()
loan_chart.type = "col"
loan_chart.style = 10
loan_chart.title = "Loan Status Analysis"
loan_chart.x_axis.title = "Loan Status"
loan_chart.y_axis.title = "Number of Loans"

loan_data = Reference(
    ws,
    min_col=2,
    min_row=1,
    max_row=4
)

loan_categories = Reference(
    ws,
    min_col=1,
    min_row=2,
    max_row=4
)

loan_chart.add_data(loan_data, titles_from_data=True)
loan_chart.set_categories(loan_categories)

loan_chart.height = 10
loan_chart.width = 18

ws.add_chart(loan_chart, "F2")


# City-wise Transaction Chart
ws = wb["City Analysis"]

city_chart = BarChart()
city_chart.type = "col"
city_chart.style = 10
city_chart.title = "City-wise Transaction Analysis"
city_chart.x_axis.title = "City"
city_chart.y_axis.title = "Total Transactions"

city_data = Reference(
    ws,
    min_col=2,
    min_row=1,
    max_row=9
)

city_categories = Reference(
    ws,
    min_col=1,
    min_row=2,
    max_row=9
)

city_chart.add_data(city_data, titles_from_data=True)
city_chart.set_categories(city_categories)

city_chart.height = 11
city_chart.width = 20

ws.add_chart(city_chart, "F2")


# ==================================
# FINAL BANKING ANALYTICS DASHBOARD
# ==================================

from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference

# Create Dashboard sheet
if "Dashboard" in wb.sheetnames:
    del wb["Dashboard"]

dash = wb.create_sheet("Dashboard", 0)

# Dashboard title
dash.merge_cells("A1:F2")
dash["A1"] = "BANKING & FINANCIAL ANALYTICS DASHBOARD"
dash["A1"].font = Font(
    bold=True, size=18, color="FFFFFF"
)
dash["A1"].fill = PatternFill(
    "solid", fgColor="17365D"
)
dash["A1"].alignment = Alignment(
    horizontal="center", vertical="center"
)

# KPI headings and values
kpis = [
    ("Total Customers", len(customers)),
    ("Total Transactions", len(transactions)),
    ("Total Loans", len(loans)),
    (
        "Default Rate (%)",
        round((loans["loan_status"].eq("Default").sum()
               / len(loans)) * 100, 2)
    ),
    ("Total Bank Balance (₹)", round(customers["account_balance"].sum(), 2)),
    ("Total Transaction Amount (₹)", round(transactions["amount"].sum(), 2))
]

positions = [
    ("A4", "B4"),
    ("C4", "D4"),
    ("E4", "F4"),
    ("A7", "B7"),
    ("C7", "D7"),
    ("E7", "F7")
]

for (label, value), (label_cell, value_cell) in zip(kpis, positions):
    dash[label_cell] = label
    dash[value_cell] = value

    dash[label_cell].font = Font(bold=True, color="FFFFFF")
    dash[label_cell].fill = PatternFill(
        "solid", fgColor="4472C4"
    )

    dash[value_cell].font = Font(
        bold=True, size=14, color="17365D"
    )
    dash[value_cell].fill = PatternFill(
        "solid", fgColor="D9EAF7"
    )

    dash[label_cell].alignment = Alignment(horizontal="center")
    dash[value_cell].alignment = Alignment(horizontal="center")

# Dashboard column widths
for col in ["A", "C", "E"]:
    dash.column_dimensions[col].width = 28

for col in ["B", "D", "F"]:
    dash.column_dimensions[col].width = 22

dash.freeze_panes = "A4"


# Add charts to Dashboard

# Transaction Chart
transaction_source = wb["Transaction Summary"]
transaction_chart = BarChart()
transaction_chart.type = "col"
transaction_chart.title = "Transaction Count by Type"
transaction_chart.y_axis.title = "Transactions"

data = Reference(transaction_source, min_col=2, min_row=1, max_row=5)
categories = Reference(transaction_source, min_col=1, min_row=2, max_row=5)

transaction_chart.add_data(data, titles_from_data=True)
transaction_chart.set_categories(categories)
transaction_chart.height = 8
transaction_chart.width = 14

dash.add_chart(transaction_chart, "A10")

# Loan Chart
loan_source = wb["Loan Summary"]
loan_chart = BarChart()
loan_chart.type = "col"
loan_chart.title = "Loan Status Analysis"
loan_chart.y_axis.title = "Number of Loans"

data = Reference(loan_source, min_col=2, min_row=1, max_row=4)
categories = Reference(loan_source, min_col=1, min_row=2, max_row=4)

loan_chart.add_data(data, titles_from_data=True)
loan_chart.set_categories(categories)
loan_chart.height = 8
loan_chart.width = 14

dash.add_chart(loan_chart, "H10")

# City Chart
city_source = wb["City Analysis"]
city_chart_dashboard = BarChart()
city_chart_dashboard.type = "col"
city_chart_dashboard.title = "City-wise Transactions"
city_chart_dashboard.y_axis.title = "Transactions"

data = Reference(city_source, min_col=2, min_row=1, max_row=9)
categories = Reference(city_source, min_col=1, min_row=2, max_row=9)

city_chart_dashboard.add_data(data, titles_from_data=True)
city_chart_dashboard.set_categories(categories)
city_chart_dashboard.height = 8
city_chart_dashboard.width = 20

dash.add_chart(city_chart_dashboard, "A27")


# Save workbook
wb.save(output_file)

# Save formatted workbook
wb.save(output_file)

print("Excel report generated successfully!")
print("File location:", output_file)



