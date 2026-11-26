
from openpyxl import load_workbook

# Load Excel workbook
file_path = "reports/Banking_Financial_Analytics.xlsx"
wb = load_workbook(file_path)

ws = wb["Dashboard"]

# Format KPI numbers
for cell in ["B4", "D4", "F4"]:
    ws[cell].number_format = '#,##0'

# Default rate: value is already 8.88, so don't multiply by 100
ws["B7"].number_format = '0.00"%"'

# Currency formatting
for cell in ["D7", "F7"]:
    ws[cell].number_format = '"₹"#,##0.00'

# Save as a separate file
output_path = "reports/Banking_Financial_Analytics_formatted.xlsx"
wb.save(output_path)

print("Dashboard KPI formatting completed!")
print("Saved at:", output_path)
