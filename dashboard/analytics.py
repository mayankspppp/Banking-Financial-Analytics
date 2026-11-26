from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from dashboard.data import BankingData

SUCCESS_STATUS = "Success"
DEPOSIT_TYPE = "Deposit"
WITHDRAWAL_TYPE = "Withdrawal"
DEFAULT_STATUS = "Default"


@dataclass(frozen=True)
class KPIValues:
    total_customers: int
    total_transactions: int
    total_deposits: float
    total_withdrawals: float
    total_loan_amount: float
    total_loans: int
    loan_default_rate: float | None


def filter_banking_data(
    data: BankingData,
    start_date: date,
    end_date: date,
    cities: list[str] | None = None,
    account_types: list[str] | None = None,
) -> BankingData:
    """Filter each fact table by its own date and customer segment."""
    if start_date > end_date:
        raise ValueError("The reporting period start must not be after its end.")

    segment_customers = data.customers
    if cities is not None:
        segment_customers = segment_customers[
            segment_customers["city"].isin(cities)
        ]
    if account_types is not None:
        segment_customers = segment_customers[
            segment_customers["account_type"].isin(account_types)
        ]

    customer_cohort = segment_customers[
        _date_mask(segment_customers["join_date"], start_date, end_date)
    ].copy()
    segment_customer_ids = segment_customers["customer_id"]

    transactions = data.transactions[
        _date_mask(data.transactions["transaction_date"], start_date, end_date)
        & data.transactions["customer_id"].isin(segment_customer_ids)
    ].copy()
    loans = data.loans[
        _date_mask(data.loans["loan_date"], start_date, end_date)
        & data.loans["customer_id"].isin(segment_customer_ids)
    ].copy()

    return BankingData(
        customers=customer_cohort,
        transactions=transactions,
        loans=loans,
    )


def _date_mask(values: pd.Series, start_date: date, end_date: date) -> pd.Series:
    start = pd.Timestamp(start_date)
    end_exclusive = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    return values.ge(start) & values.lt(end_exclusive)


def calculate_kpis(data: BankingData) -> KPIValues:
    successful = data.transactions[
        data.transactions["transaction_status"].eq(SUCCESS_STATUS)
    ]
    loan_count = len(data.loans)
    default_count = int(data.loans["loan_status"].eq(DEFAULT_STATUS).sum())

    return KPIValues(
        total_customers=len(data.customers),
        total_transactions=len(data.transactions),
        total_deposits=float(
            successful.loc[
                successful["transaction_type"].eq(DEPOSIT_TYPE), "amount"
            ].sum()
        ),
        total_withdrawals=float(
            successful.loc[
                successful["transaction_type"].eq(WITHDRAWAL_TYPE), "amount"
            ].sum()
        ),
        total_loan_amount=float(data.loans["loan_amount"].sum()),
        total_loans=loan_count,
        loan_default_rate=(
            default_count / loan_count * 100 if loan_count else None
        ),
    )


def customer_city_summary(customers: pd.DataFrame) -> pd.DataFrame:
    return (
        customers.groupby(["city", "account_type"], as_index=False, observed=True)
        .agg(
            customer_count=("customer_id", "nunique"),
            total_balance=("account_balance", "sum"),
            average_balance=("account_balance", "mean"),
        )
        .sort_values(["city", "account_type"])
    )


def transaction_type_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    if transactions.empty:
        return pd.DataFrame(
            columns=[
                "transaction_type",
                "total_transactions",
                "successful_transactions",
                "successful_amount",
            ]
        )

    summary = (
        transactions.groupby("transaction_type", as_index=False, observed=True)
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=(
                "transaction_status",
                lambda values: values.eq(SUCCESS_STATUS).sum(),
            ),
        )
    )
    successful_amounts = (
        transactions.loc[transactions["transaction_status"].eq(SUCCESS_STATUS)]
        .groupby("transaction_type", observed=True)["amount"]
        .sum()
        .rename("successful_amount")
    )
    return (
        summary.join(successful_amounts, on="transaction_type")
        .fillna({"successful_amount": 0.0})
        .sort_values("transaction_type")
        .reset_index(drop=True)
    )


def transaction_status_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    return (
        transactions.groupby(
            ["transaction_date", "transaction_status"], as_index=False, observed=True
        )
        .agg(transaction_count=("transaction_id", "count"))
        .sort_values(["transaction_date", "transaction_status"])
    )


def loan_status_summary(loans: pd.DataFrame) -> pd.DataFrame:
    return (
        loans.groupby("loan_status", as_index=False, observed=True)
        .agg(
            loan_count=("loan_id", "count"),
            total_loan_amount=("loan_amount", "sum"),
            average_interest_rate=("interest_rate_pct", "mean"),
        )
        .sort_values("loan_status")
    )


def credit_risk_summary(
    customers: pd.DataFrame, loans: pd.DataFrame
) -> pd.DataFrame:
    if loans.empty:
        return pd.DataFrame(
            columns=[
                "credit_category",
                "loan_count",
                "default_count",
                "default_rate",
                "total_loan_amount",
            ]
        )

    loan_customers = loans.merge(
        customers[["customer_id", "credit_score"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    loan_customers["credit_category"] = pd.cut(
        loan_customers["credit_score"],
        bins=[float("-inf"), 650, 700, 750, float("inf")],
        labels=["Low", "Average", "Good", "Excellent"],
        right=False,
    )
    summary = (
        loan_customers.groupby("credit_category", as_index=False, observed=True)
        .agg(
            loan_count=("loan_id", "count"),
            default_count=("loan_status", lambda values: values.eq(DEFAULT_STATUS).sum()),
            total_loan_amount=("loan_amount", "sum"),
        )
    )
    summary["default_rate"] = summary["default_count"] / summary["loan_count"] * 100
    return summary


def loan_city_risk_summary(
    customers: pd.DataFrame, loans: pd.DataFrame
) -> pd.DataFrame:
    if loans.empty:
        return pd.DataFrame(
            columns=["city", "loan_count", "default_count", "default_rate"]
        )

    loan_customers = loans.merge(
        customers[["customer_id", "city"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    summary = (
        loan_customers.groupby("city", as_index=False, observed=True)
        .agg(
            loan_count=("loan_id", "count"),
            default_count=("loan_status", lambda values: values.eq(DEFAULT_STATUS).sum()),
        )
        .sort_values("city")
    )
    summary["default_rate"] = summary["default_count"] / summary["loan_count"] * 100
    return summary
