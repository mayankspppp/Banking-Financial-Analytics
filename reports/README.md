# Banking & Financial Analytics

A data analytics project focused on exploring banking customers, financial transactions, loan performance, and credit risk using Python, SQL, and Excel.

## 1. Project Overview

This project analyzes synthetic banking and financial datasets to identify business insights, understand customer behavior, monitor transaction trends, and evaluate loan performance.

Python is used for data cleaning and exploratory data analysis (EDA), SQLite is used for SQL-based analysis, and Excel is used to create a dashboard-style financial report.

## 2. Project Objectives

- Analyze customer demographics and account balances.
- Understand transaction patterns and trends.
- Evaluate loan distribution and loan status.
- Identify potential loan default risks.
- Compare financial performance across cities.
- Present key business insights through an Excel dashboard.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data analysis and processing |
| Pandas | Data manipulation and cleaning |
| NumPy | Numerical operations |
| SQLite | Database management |
| SQL | Data querying and analysis |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Excel | Dashboard and reporting |
| OpenPyXL | Excel automation and formatting |

## 4. Dataset Description

The project uses three synthetic datasets:

| Dataset | Records | Description |
|---|---:|---|
| Customers | 500 | Customer and account information |
| Transactions | 5,000 | Banking transaction records |
| Loans | 800 | Loan information and status |

The datasets are connected using the common `customer_id` field.

**Note:** All datasets are synthetic and created for educational and portfolio purposes.

## 5. Python Analysis

Python and Pandas were used for:

- Loading and inspecting datasets.
- Checking missing values.
- Identifying duplicate records.
- Converting date columns.
- Generating statistical summaries.
- Performing exploratory data analysis (EDA).
- Creating data visualizations.

## 6. SQL Analysis

SQLite and SQL were used to perform:

- Customer and transaction analysis.
- City-wise transaction analysis.
- Account type analysis.
- Top customers by account balance.
- Credit score categorization.
- Loan status analysis.
- Credit score versus loan default analysis.
- City-wise loan risk analysis.
- Window functions and customer ranking.
- Running totals and transaction comparisons.

## 7. Excel Dashboard

The Excel workbook contains the following analysis sheets:

- Dashboard
- Customers
- Transactions
- Loans
- Transaction Summary
- Loan Summary
- City Analysis
- Credit Risk

The dashboard presents key performance indicators (KPIs) and charts for transaction activity, loan status, and city-wise transaction performance.

## 8. Key Business Insights

Based on the project analysis:

- **500 customers** were analyzed.
- **5,000 transactions** were examined.
- **800 loans** were analyzed.
- Deposit transactions have the highest transaction count.
- Delhi has the highest transaction volume among the analyzed cities.
- Active loans represent the largest loan-status category.
- The overall loan default rate is approximately **8.88%**.
- Customers in the low credit score category have a higher loan default percentage than customers in higher credit score categories.

## 9. Project Structure

```text
Banking_Financial_Analytics/
│
├── dataset/
│   ├── customers.csv
│   ├── transactions.csv
│   ├── loans.csv
│   └── README.txt
│
├── python/
│   ├── main.py
│   ├── data_cleaning.py
│   ├── eda.py
│   ├── export_data.py
│   ├── format_dashboard.py
│   └── format_charts.py
│
├── sql/
│   ├── banking.db
│   ├── banking_analysis.sql
│   └── banking_analysis_queries.sql
│
├── reports/
│   ├── Banking_Financial_Analytics.xlsx
│   ├── Banking_Financial_Analytics_formatted.xlsx
│   └── Banking_Financial_Analytics_final.xlsx
│
├── dashboard/
│
├── requirements.txt
└── README.md
```

## 10. How to Run the Project

### Step 1: Clone the repository

```bash
git clone <your-github-repository-url>
cd Banking_Financial_Analytics
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Python scripts

Run the scripts from the project root:

```bash
python python/main.py
python python/data_cleaning.py
python python/eda.py
python python/export_data.py
```

### Step 5: Generate the formatted Excel report

```bash
python python/format_dashboard.py
python python/format_charts.py
```

### Step 6: Open the final report

Open:

```text
reports/Banking_Financial_Analytics_final.xlsx
```

## 11. Conclusion

This project demonstrates practical skills in Python-based data analysis, SQL querying, financial data exploration, data visualization, and Excel reporting.

It provides a structured analysis of customer accounts, banking transactions, loan performance, and credit risk.

---

**Disclaimer:** This project uses synthetic data and is intended for educational and portfolio demonstration purposes only.