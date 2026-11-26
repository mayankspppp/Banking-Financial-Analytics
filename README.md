# Banking & Financial Analytics

A portfolio-ready Streamlit dashboard for exploring banking operations, customer segments, transactions, and credit risk. The project creates its own reproducible synthetic dataset locally; it does not ship customer CSV files, a database, or generated reports.

## Features

- Overview KPIs and interactive Plotly visualizations
- Customer, transaction, loan, and credit-risk analytics
- Date, city, and account-type filters
- Searchable, sortable data tables
- Filtered CSV, Excel, and PDF exports
- SQLite database access is read-only in the dashboard
- Seeded Faker data generation with a configurable record count

## Technology

Python 3.12+, Streamlit, Pandas, NumPy, Plotly, Faker, SQLite, OpenPyXL, and ReportLab.

## Setup

From the project root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Generate the local CSV files and SQLite database:

```bash
python -m python.generate_synthetic_data --seed 20261126
```

Generation stops if its output files already exist. To deliberately regenerate them:

```bash
python -m python.generate_synthetic_data --seed 20261126 --overwrite
```

### Fictional data contract

The source project has customers, transactions, and loans tables. This generator keeps their existing fields and adds `customer_name` to customers. Every name is prefixed with `Demo`, customer/transaction/loan IDs are generated, city values are labels such as `City A`, and all amounts, scores, statuses, and dates are newly generated. No original database, workbook, or CSV records are read or copied. Contact details and account numbers are not generated.

The default output contains exactly 500 customers, 5,000 transactions, and 800 loans. Faker and NumPy are both seeded from `--seed`; repeating a seed with the pinned Faker dependency reproduces the same records. Every transaction and loan customer ID is selected from the generated customer IDs. The SQLite database includes a `dataset_metadata` row explicitly labeled **FICTIONAL DEMONSTRATION DATA** with the seed and generator library versions.

Generated CSVs and the SQLite database are local-only and ignored by Git. Their fictional status is also documented in [`dataset/README.md`](dataset/README.md).

## Run the dashboard

Run from the project root:

```bash
PYTHONPATH="$PWD" .venv/bin/python -m streamlit run dashboard/app.py
```

Then open [http://localhost:8501](http://localhost:8501). Keep the terminal open while using the dashboard.

PowerShell:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

## Hosted deployment

No hosted deployment target is configured or tested. A clean checkout intentionally has no database or CSV data, so a host must run the synthetic-data generator with a chosen seed before starting Streamlit. Do not commit generated data to make deployment work. Use a host with a supported pre-start/build step and persistent-enough local storage for the generated database; provider-specific setup remains to be added and verified.

## Analysis scripts

After generating the data, the existing Python scripts can inspect it and create local Excel reports:

```bash
python python/main.py
python python/eda.py
python python/export_data.py
python python/format_dashboard.py
python python/format_charts.py
```

These report scripts use only the generated local CSV files. Their outputs are excluded from Git.

## SQL

The read-only analysis queries are in [`sql/banking_analysis_queries.sql`](sql/banking_analysis_queries.sql). Run them against the locally generated `banking.db` using a SQLite client.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests generate isolated synthetic data in temporary directories and do not require the local database.

## Screenshots

Add genuine dashboard screenshots under `docs/screenshots/` before publishing. No screenshots are included yet.

## Data and privacy

The generator creates fictional demonstration records from Faker and NumPy using a reproducible seed. Do not put real customer or financial information in this repository. Generated databases, CSVs, exports, virtual environments, caches, and local Streamlit configuration are ignored.
