from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
DATABASE_PATH = PROJECT_ROOT / "banking.db"

DATE_COLUMNS = {
    "customers": "join_date",
    "transactions": "transaction_date",
    "loans": "loan_date",
}


def load_datasets() -> dict[str, pd.DataFrame]:
    datasets = {
        "customers": pd.read_csv(DATASET_DIR / "customers.csv"),
        "transactions": pd.read_csv(DATASET_DIR / "transactions.csv"),
        "loans": pd.read_csv(DATASET_DIR / "loans.csv"),
    }

    for table_name, frame in datasets.items():
        date_column = DATE_COLUMNS[table_name]
        frame[date_column] = pd.to_datetime(frame[date_column], errors="raise")

    return datasets


def print_data_checks(datasets: dict[str, pd.DataFrame]) -> None:
    print("=" * 50)
    print("BANKING & FINANCIAL ANALYTICS PROJECT")
    print("=" * 50)

    for table_name, frame in datasets.items():
        print(f"\n{table_name.upper()} DATA")
        print(frame.head())
        print(f"\n{table_name.upper()} SHAPE")
        print(frame.shape)
        print(f"\n{table_name.upper()} MISSING VALUES")
        print(frame.isnull().sum())
        print(f"\n{table_name.upper()} DUPLICATE RECORDS")
        print(frame.duplicated().sum())
        print(f"\n{table_name.upper()} DATA TYPES")
        print(frame.dtypes)


def initialize_missing_database_tables(
    database_path: Path = DATABASE_PATH,
) -> list[str]:
    """Create missing tables without replacing or modifying existing tables."""
    datasets = load_datasets()
    created_tables: list[str] = []

    with sqlite3.connect(database_path) as connection:
        existing_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        for table_name, frame in datasets.items():
            if table_name in existing_tables:
                continue
            frame.to_sql(table_name, connection, if_exists="fail", index=False)
            created_tables.append(table_name)

        table_names = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        ]
        print("Database tables:", table_names)

    return created_tables


def main() -> None:
    datasets = load_datasets()
    print_data_checks(datasets)

    created_tables = initialize_missing_database_tables()
    if created_tables:
        print("Created missing tables:", ", ".join(created_tables))
    else:
        print("Existing database tables were preserved; no tables were replaced.")


if __name__ == "__main__":
    main()
