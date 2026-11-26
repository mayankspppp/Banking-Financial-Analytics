from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "banking.db"

REQUIRED_COLUMNS = {
    "customers": {
        "customer_id",
        "age",
        "gender",
        "city",
        "account_type",
        "account_balance",
        "credit_score",
        "join_date",
    },
    "transactions": {
        "transaction_id",
        "customer_id",
        "transaction_date",
        "transaction_type",
        "amount",
        "channel",
        "transaction_status",
    },
    "loans": {
        "loan_id",
        "customer_id",
        "loan_type",
        "loan_amount",
        "interest_rate_pct",
        "tenure_months",
        "loan_date",
        "loan_status",
    },
}

DATE_COLUMNS = {
    "customers": "join_date",
    "transactions": "transaction_date",
    "loans": "loan_date",
}


@dataclass(frozen=True)
class BankingData:
    customers: pd.DataFrame
    transactions: pd.DataFrame
    loans: pd.DataFrame


def load_banking_data(database_path: Path | str = DATABASE_PATH) -> BankingData:
    """Load and validate the existing SQLite tables using a read-only connection."""
    path = Path(database_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Banking database was not found: {path}")

    database_uri = f"file:{quote(path.as_posix(), safe='/')}?mode=ro"
    with closing(sqlite3.connect(database_uri, uri=True)) as connection:
        connection.execute("PRAGMA query_only = ON")
        existing_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        missing_tables = set(REQUIRED_COLUMNS) - existing_tables
        if missing_tables:
            raise ValueError(
                "Banking database is missing required tables: "
                + ", ".join(sorted(missing_tables))
            )

        tables: dict[str, pd.DataFrame] = {}
        for table_name, required_columns in REQUIRED_COLUMNS.items():
            columns = {
                row[1]
                for row in connection.execute(f'PRAGMA table_info("{table_name}")')
            }
            missing_columns = required_columns - columns
            if missing_columns:
                raise ValueError(
                    f"Table '{table_name}' is missing required columns: "
                    + ", ".join(sorted(missing_columns))
                )
            tables[table_name] = pd.read_sql_query(
                f'SELECT * FROM "{table_name}"', connection
            )

    for table_name, date_column in DATE_COLUMNS.items():
        tables[table_name][date_column] = pd.to_datetime(
            tables[table_name][date_column], errors="raise"
        )
        if tables[table_name][date_column].isna().any():
            raise ValueError(
                f"Table '{table_name}' contains empty values in '{date_column}'."
            )

    for table_name, amount_column in (
        ("customers", "account_balance"),
        ("transactions", "amount"),
        ("loans", "loan_amount"),
    ):
        tables[table_name][amount_column] = pd.to_numeric(
            tables[table_name][amount_column], errors="raise"
        )

    return BankingData(
        customers=tables["customers"],
        transactions=tables["transactions"],
        loans=tables["loans"],
    )
