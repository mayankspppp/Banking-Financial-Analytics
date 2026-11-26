from __future__ import annotations

import argparse
import sqlite3
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from faker import VERSION as FAKER_VERSION
from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
DATABASE_PATH = PROJECT_ROOT / "banking.db"
DEFAULT_SEED = 20261126
START_DATE = date(2021, 1, 1)
END_DATE = date(2025, 12, 31)

CITIES = tuple(f"City {letter}" for letter in "ABCDEFGH")
GENDERS = ("Female", "Male", "Non-binary", "Prefer not to say")
ACCOUNT_TYPES = ("Savings", "Current")
TRANSACTION_TYPES = ("Deposit", "Withdrawal", "Transfer", "Payment")
CHANNELS = ("Online", "Mobile", "Branch", "ATM")
TRANSACTION_STATUSES = ("Success", "Failed")
LOAN_TYPES = ("Home", "Personal", "Auto", "Education", "Business")
LOAN_STATUSES = ("Active", "Closed", "Default")
TENURES = (12, 24, 36, 60, 120, 240, 360)


def generate_synthetic_data(
    seed: int = DEFAULT_SEED,
    customer_count: int = 500,
    transaction_count: int = 5_000,
    loan_count: int = 800,
) -> dict[str, pd.DataFrame]:
    """Create reproducible fictional demonstration tables."""
    if customer_count < 1:
        raise ValueError("customer_count must be at least 1.")
    if transaction_count < 0 or loan_count < 0:
        raise ValueError("transaction_count and loan_count cannot be negative.")

    fake = Faker("en_US")
    fake.seed_instance(seed)
    random = np.random.default_rng(seed)
    customer_ids = [
        fake.unique.bothify(text="CUST-#####") for _ in range(customer_count)
    ]

    customers = pd.DataFrame(
        [
            {
                "customer_id": customer_id,
                "customer_name": f"Demo {fake.name()}",
                "age": int(random.integers(21, 76)),
                "gender": str(random.choice(GENDERS)),
                "city": str(random.choice(CITIES)),
                "account_type": str(random.choice(ACCOUNT_TYPES)),
                "account_balance": int(random.integers(10_000, 30_000_001)) / 100,
                "credit_score": int(random.integers(500, 851)),
                "join_date": fake.date_between_dates(
                    date_start=START_DATE, date_end=END_DATE
                ).isoformat(),
            }
            for customer_id in customer_ids
        ],
        columns=[
            "customer_id",
            "customer_name",
            "age",
            "gender",
            "city",
            "account_type",
            "account_balance",
            "credit_score",
            "join_date",
        ],
    )

    transaction_customer_ids = random.choice(
        customer_ids, size=transaction_count, replace=True
    )
    transaction_types = random.choice(TRANSACTION_TYPES, size=transaction_count)
    transaction_channels = random.choice(CHANNELS, size=transaction_count)
    transaction_statuses = random.choice(
        TRANSACTION_STATUSES,
        size=transaction_count,
        p=(0.92, 0.08),
    )
    transaction_amounts = random.integers(
        500, 1_000_001, size=transaction_count
    ) / 100

    transactions = pd.DataFrame(
        [
            {
                "transaction_id": f"TXN-{index:07d}",
                "customer_id": str(transaction_customer_ids[index - 1]),
                "transaction_date": fake.date_between_dates(
                    date_start=START_DATE, date_end=END_DATE
                ).isoformat(),
                "transaction_type": str(transaction_types[index - 1]),
                "amount": float(transaction_amounts[index - 1]),
                "channel": str(transaction_channels[index - 1]),
                "transaction_status": str(transaction_statuses[index - 1]),
            }
            for index in range(1, transaction_count + 1)
        ],
        columns=[
            "transaction_id",
            "customer_id",
            "transaction_date",
            "transaction_type",
            "amount",
            "channel",
            "transaction_status",
        ],
    )

    loan_customer_ids = random.choice(customer_ids, size=loan_count, replace=True)
    loan_types = random.choice(LOAN_TYPES, size=loan_count)
    loan_amounts = random.integers(100_000, 80_000_001, size=loan_count) / 100
    interest_rates = random.integers(700, 1_801, size=loan_count) / 100
    tenures = random.choice(TENURES, size=loan_count)
    loan_statuses = random.choice(
        LOAN_STATUSES,
        size=loan_count,
        p=(0.65, 0.30, 0.05),
    )

    loans = pd.DataFrame(
        [
            {
                "loan_id": f"LOAN-{index:06d}",
                "customer_id": str(loan_customer_ids[index - 1]),
                "loan_type": str(loan_types[index - 1]),
                "loan_amount": float(loan_amounts[index - 1]),
                "interest_rate_pct": float(interest_rates[index - 1]),
                "tenure_months": int(tenures[index - 1]),
                "loan_date": fake.date_between_dates(
                    date_start=START_DATE, date_end=END_DATE
                ).isoformat(),
                "loan_status": str(loan_statuses[index - 1]),
            }
            for index in range(1, loan_count + 1)
        ],
        columns=[
            "loan_id",
            "customer_id",
            "loan_type",
            "loan_amount",
            "interest_rate_pct",
            "tenure_months",
            "loan_date",
            "loan_status",
        ],
    )

    return {
        "customers": customers,
        "transactions": transactions,
        "loans": loans,
    }


def write_synthetic_outputs(
    output_dir: Path | str = DATASET_DIR,
    database_path: Path | str = DATABASE_PATH,
    seed: int = DEFAULT_SEED,
    customer_count: int = 500,
    transaction_count: int = 5_000,
    loan_count: int = 800,
    overwrite: bool = False,
) -> dict[str, Path]:
    """Write generated CSVs and SQLite tables, refusing accidental replacement."""
    output_directory = Path(output_dir).expanduser().resolve()
    database = Path(database_path).expanduser().resolve()
    csv_paths = {
        name: output_directory / f"{name}.csv"
        for name in ("customers", "transactions", "loans")
    }
    targets = [*csv_paths.values(), database]
    existing = [path for path in targets if path.exists()]
    if existing and not overwrite:
        paths = ", ".join(str(path) for path in existing)
        raise FileExistsError(
            f"Refusing to overwrite existing generated output: {paths}. "
            "Pass overwrite=True or use --overwrite to replace it."
        )

    tables = generate_synthetic_data(
        seed=seed,
        customer_count=customer_count,
        transaction_count=transaction_count,
        loan_count=loan_count,
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    database.parent.mkdir(parents=True, exist_ok=True)

    for name, frame in tables.items():
        frame.to_csv(csv_paths[name], index=False)

    if database.exists():
        database.unlink()
    with sqlite3.connect(database) as connection:
        for name, frame in tables.items():
            frame.to_sql(name, connection, if_exists="fail", index=False)
        connection.execute(
            """
            CREATE TABLE dataset_metadata (
                dataset_label TEXT NOT NULL,
                seed INTEGER NOT NULL,
                faker_version TEXT NOT NULL,
                numpy_version TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO dataset_metadata
                (dataset_label, seed, faker_version, numpy_version)
            VALUES (?, ?, ?, ?)
            """,
            (
                "FICTIONAL DEMONSTRATION DATA — generated with Faker and NumPy",
                seed,
                FAKER_VERSION,
                np.__version__,
            ),
        )

    return {**csv_paths, "database": database}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic local banking demo data with Faker."
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--customers", type=int, default=500)
    parser.add_argument("--transactions", type=int, default=5_000)
    parser.add_argument("--loans", type=int, default=800)
    parser.add_argument("--output-dir", type=Path, default=DATASET_DIR)
    parser.add_argument("--database-path", type=Path, default=DATABASE_PATH)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace generated CSVs and database if they already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    outputs = write_synthetic_outputs(
        output_dir=args.output_dir,
        database_path=args.database_path,
        seed=args.seed,
        customer_count=args.customers,
        transaction_count=args.transactions,
        loan_count=args.loans,
        overwrite=args.overwrite,
    )
    print(f"Generated fictional demonstration data with seed {args.seed}:")
    for name, path in outputs.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
