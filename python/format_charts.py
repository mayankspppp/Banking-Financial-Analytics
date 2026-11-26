
from openpyxl import load_workbook
from openpyxl.chart.label import DataLabelList

# Load formatted Excel workbook
file_path = "reports/Banking_Financial_Analytics_formatted.xlsx"
wb = load_workbook(file_path)

ws = wb["Dashboard"]

# Format all dashboard charts
for index, chart in enumerate(ws._charts, start=1):

    # Chart size
    chart.width = 15
    chart.height = 8

    # Professional chart style
    chart.style = 10

    # Remove overlapping data labels
    chart.dLbls = DataLabelList()
    chart.dLbls.showVal = False
    chart.dLbls.showCatName = False
    chart.dLbls.showSerName = False
    chart.dLbls.showLegendKey = False

    # Display legend on right
    if chart.legend:
        chart.legend.position = "r"

    print(f"Chart {index} formatted successfully")

# Save final workbook
output_path = "reports/Banking_Financial_Analytics_final.xlsx"
wb.save(output_path)

print("\nAll charts formatted successfully!")
print("Saved at:", output_path)
