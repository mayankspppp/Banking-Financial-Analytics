from __future__ import annotations

import sqlite3
from datetime import date
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd
from openpyxl import load_workbook

from dashboard.analytics import calculate_kpis, filter_banking_data
from dashboard.data import BankingData, load_banking_data
from dashboard.exports import csv_bytes, excel_report_bytes, pdf_report_bytes
from python.generate_synthetic_data import (
    generate_synthetic_data,
    write_synthetic_outputs,
)


def sample_data() -> BankingData:
    customers = pd.DataFrame(
        [
            {
                "customer_id": "C1",
                "age": 31,
                "gender": "F",
                "city": "Delhi",
                "account_type": "Current",
                "account_balance": 1500.0,
                "credit_score": 710,
                "join_date": pd.Timestamp("2024-01-01"),
            },
            {
                "customer_id": "C2",
                "age": 42,
                "gender": "M",
                "city": "Pune",
                "account_type": "Savings",
                "account_balance": 2000.0,
                "credit_score": 760,
                "join_date": pd.Timestamp("2022-01-01"),
            },
        ]
    )
    transactions = pd.DataFrame(
        [
            {
                "transaction_id": "T1",
                "customer_id": "C1",
                "transaction_date": pd.Timestamp("2024-02-01"),
                "transaction_type": "Deposit",
                "amount": 100.0,
                "channel": "Online",
                "transaction_status": "Success",
            },
            {
                "transaction_id": "T2",
                "customer_id": "C1",
                "transaction_date": pd.Timestamp("2024-02-02"),
                "transaction_type": "Deposit",
                "amount": 40.0,
                "channel": "Branch",
                "transaction_status": "Failed",
            },
            {
                "transaction_id": "T3",
                "customer_id": "C2",
                "transaction_date": pd.Timestamp("2024-02-03"),
                "transaction_type": "Withdrawal",
                "amount": 20.0,
                "channel": "Online",
                "transaction_status": "Success",
            },
        ]
    )
    loans = pd.DataFrame(
        [
            {
                "loan_id": "L1",
                "customer_id": "C1",
                "loan_type": "Home Loan",
                "loan_amount": 1000.0,
                "interest_rate_pct": 5.0,
                "tenure_months": 24,
                "loan_date": pd.Timestamp("2024-02-01"),
                "loan_status": "Default",
            },
            {
                "loan_id": "L2",
                "customer_id": "C2",
                "loan_type": "Car Loan",
                "loan_amount": 500.0,
                "interest_rate_pct": 6.0,
                "tenure_months": 12,
                "loan_date": pd.Timestamp("2024-02-01"),
                "loan_status": "Closed",
            },
        ]
    )
    return BankingData(customers, transactions, loans)


class DashboardAnalyticsTests(unittest.TestCase):
    def test_metrics_and_segment_filters_use_successful_flows(self) -> None:
        filtered = filter_banking_data(
            sample_data(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 28),
            cities=["Delhi"],
            account_types=["Current"],
        )

        metrics = calculate_kpis(filtered)
        self.assertEqual(metrics.total_customers, 1)
        self.assertEqual(metrics.total_transactions, 2)
        self.assertEqual(metrics.total_deposits, 100.0)
        self.assertEqual(metrics.total_withdrawals, 0.0)
        self.assertEqual(metrics.total_loan_amount, 1000.0)
        self.assertEqual(metrics.total_loans, 1)
        self.assertEqual(metrics.loan_default_rate, 100.0)

    def test_customer_join_date_does_not_hide_segment_activity(self) -> None:
        filtered = filter_banking_data(
            sample_data(),
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 28),
            cities=["Pune"],
            account_types=["Savings"],
        )

        self.assertEqual(len(filtered.customers), 0)
        self.assertEqual(len(filtered.transactions), 1)
        self.assertEqual(len(filtered.loans), 1)

    def test_default_rate_is_unavailable_without_loan_records(self) -> None:
        data = sample_data()
        no_loans = BankingData(data.customers, data.transactions, data.loans.iloc[0:0])
        self.assertIsNone(calculate_kpis(no_loans).loan_default_rate)

    def test_rejects_reversed_date_ranges(self) -> None:
        with self.assertRaises(ValueError):
            filter_banking_data(
                sample_data(),
                start_date=date(2024, 3, 1),
                end_date=date(2024, 2, 1),
            )

    def test_generated_database_loads_and_exports(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            outputs = write_synthetic_outputs(
                output_dir=root / "dataset",
                database_path=root / "banking.db",
                seed=7,
                customer_count=20,
                transaction_count=80,
                loan_count=30,
            )
            data = load_banking_data(outputs["database"])
            with sqlite3.connect(
                Path(outputs["database"]).resolve().as_uri() + "?mode=ro", uri=True
            ) as connection:
                metadata = connection.execute(
                    "SELECT dataset_label, seed FROM dataset_metadata"
                ).fetchone()

        self.assertEqual(len(data.customers), 20)
        self.assertEqual(len(data.transactions), 80)
        self.assertEqual(len(data.loans), 30)
        self.assertIn("FICTIONAL DEMONSTRATION DATA", metadata[0])
        self.assertEqual(metadata[1], 7)

        report_filters = {"Reporting period": "All available dates"}
        workbook_bytes = excel_report_bytes(data, report_filters)
        workbook = load_workbook(BytesIO(workbook_bytes), read_only=True)
        self.assertIn("Overview", workbook.sheetnames)
        self.assertIn("Credit Risk", workbook.sheetnames)
        self.assertTrue(csv_bytes(data.transactions).startswith(b"\xef\xbb\xbf"))
        self.assertTrue(pdf_report_bytes(data, report_filters).startswith(b"%PDF-"))

    def test_faker_generation_is_repeatable_for_the_same_seed(self) -> None:
        first = generate_synthetic_data(
            seed=123, customer_count=5, transaction_count=10, loan_count=4
        )
        second = generate_synthetic_data(
            seed=123, customer_count=5, transaction_count=10, loan_count=4
        )
        for table_name in first:
            pd.testing.assert_frame_equal(first[table_name], second[table_name])

    def test_default_generation_has_expected_counts_and_valid_customer_links(self) -> None:
        datasets = generate_synthetic_data()
        customers = datasets["customers"]
        customer_ids = set(customers["customer_id"])

        self.assertEqual(len(customers), 500)
        self.assertEqual(len(datasets["transactions"]), 5_000)
        self.assertEqual(len(datasets["loans"]), 800)
        self.assertTrue(customers["customer_id"].is_unique)
        self.assertTrue(customers["customer_name"].str.startswith("Demo ").all())
        self.assertTrue(
            set(datasets["transactions"]["customer_id"]).issubset(customer_ids)
        )
        self.assertTrue(set(datasets["loans"]["customer_id"]).issubset(customer_ids))

    def test_generator_refuses_to_overwrite_existing_files_by_default(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            outputs = write_synthetic_outputs(
                output_dir=root / "dataset",
                database_path=root / "banking.db",
                seed=9,
                customer_count=2,
                transaction_count=3,
                loan_count=1,
            )
            database_bytes_before = outputs["database"].read_bytes()
            customer_csv_before = outputs["customers"].read_bytes()

            with self.assertRaises(FileExistsError):
                write_synthetic_outputs(
                    output_dir=root / "dataset",
                    database_path=root / "banking.db",
                    seed=10,
                    customer_count=2,
                    transaction_count=3,
                    loan_count=1,
                )

            self.assertEqual(outputs["database"].read_bytes(), database_bytes_before)
            self.assertEqual(outputs["customers"].read_bytes(), customer_csv_before)


if __name__ == "__main__":
    unittest.main()
