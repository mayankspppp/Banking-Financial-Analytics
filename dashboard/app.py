from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_string = str(PROJECT_ROOT)
if project_root_string not in sys.path:
    sys.path.insert(0, project_root_string)

import pandas as pd
import streamlit as st

from dashboard.analytics import (
    calculate_kpis,
    credit_risk_summary,
    filter_banking_data,
    loan_status_summary,
    transaction_type_summary,
)
from dashboard.charts import (
    credit_risk_chart,
    customer_balance_chart,
    customer_city_chart,
    loan_city_risk_chart,
    loan_status_chart,
    loan_type_chart,
    transaction_channel_chart,
    transaction_trend_chart,
    transaction_type_chart,
)
from dashboard.data import DATABASE_PATH, BankingData, load_banking_data
from dashboard.exports import csv_bytes, excel_report_bytes, pdf_report_bytes
from dashboard.styles import CUSTOM_CSS

st.set_page_config(
    page_title="Banking Financial Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner="Loading banking data from SQLite...")
def _load_data() -> BankingData:
    return load_banking_data(DATABASE_PATH)


@st.cache_data(show_spinner=False)
def _cached_excel_report(
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
    loans: pd.DataFrame,
    filters: dict[str, str],
    customer_reference: pd.DataFrame,
) -> bytes:
    return excel_report_bytes(
        BankingData(customers, transactions, loans),
        filters,
        customer_reference=customer_reference,
    )


@st.cache_data(show_spinner=False)
def _cached_pdf_report(
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
    loans: pd.DataFrame,
    filters: dict[str, str],
    customer_reference: pd.DataFrame,
) -> bytes:
    return pdf_report_bytes(
        BankingData(customers, transactions, loans),
        filters,
        customer_reference=customer_reference,
    )


def _currency(value: float) -> str:
    return f"₹{value:,.2f}"


def _table_column_config(frame: pd.DataFrame) -> dict[str, object]:
    configuration: dict[str, object] = {}
    currency_columns = {"account_balance", "amount", "loan_amount"}
    date_columns = {"join_date", "transaction_date", "loan_date"}

    for column in frame.columns:
        label = column.replace("_", " ").title()
        if column in currency_columns:
            configuration[column] = st.column_config.NumberColumn(
                label,
                format="₹%.2f",
            )
        elif column == "interest_rate_pct":
            configuration[column] = st.column_config.NumberColumn(
                label,
                format="%.2f%%",
            )
        elif column in date_columns:
            configuration[column] = st.column_config.DateColumn(
                label,
                format="YYYY-MM-DD",
            )
        else:
            configuration[column] = st.column_config.Column(label)

    return configuration


def _render_table(frame: pd.DataFrame, label: str, key: str) -> None:
    search = st.text_input(f"Search {label.lower()}", key=f"{key}-search")
    visible = frame
    if search:
        searchable = frame.astype("string").fillna("").agg(" ".join, axis=1)
        visible = frame.loc[
            searchable.str.contains(search, case=False, regex=False, na=False)
        ]
    st.caption(
        f"{len(visible):,} of {len(frame):,} rows · Search above; select a column "
        "header to sort."
    )
    st.dataframe(
        visible,
        hide_index=True,
        width="stretch",
        height=360,
        column_config=_table_column_config(frame),
        key=f"{key}-table",
    )


def _filter_summary(
    start_date: date,
    end_date: date,
    cities: list[str],
    account_types: list[str],
    all_cities: list[str],
    all_account_types: list[str],
) -> dict[str, str]:
    return {
        "Reporting period": f"{start_date.isoformat()} to {end_date.isoformat()}",
        "Cities": ", ".join(cities) if cities else "None selected",
        "Account types": (
            ", ".join(account_types) if account_types else "None selected"
        ),
        "City selection": "All" if cities == all_cities else "Selected",
        "Account selection": (
            "All" if account_types == all_account_types else "Selected"
        ),
    }


def main() -> None:
    data = _load_data()
    all_cities = sorted(data.customers["city"].dropna().unique().tolist())
    all_account_types = sorted(
        data.customers["account_type"].dropna().unique().tolist()
    )
    date_values = pd.concat(
        [
            data.customers["join_date"],
            data.transactions["transaction_date"],
            data.loans["loan_date"],
        ],
        ignore_index=True,
    ).dropna()
    if date_values.empty:
        raise ValueError("No dates are available in the SQLite source tables.")
    min_date = date_values.min().date()
    max_date = date_values.max().date()

    st.sidebar.markdown("## Portfolio controls")
    st.sidebar.caption(
        "Filters apply to source records and related customer segments."
    )
    selected_period = st.sidebar.date_input(
        "Reporting period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help=(
            "The period applies to join_date for customers, transaction_date for "
            "transactions, and loan_date for loans."
        ),
    )
    if (
        not isinstance(selected_period, (tuple, list))
        or len(selected_period) != 2
        or selected_period[0] is None
        or selected_period[1] is None
    ):
        st.sidebar.info("Choose both a start and end date to view the dashboard.")
        st.stop()
    start_date, end_date = selected_period
    cities = st.sidebar.multiselect("Cities", all_cities, default=all_cities)
    account_types = st.sidebar.multiselect(
        "Account types", all_account_types, default=all_account_types
    )
    if st.sidebar.button("Refresh from database"):
        _load_data.clear()
        st.rerun()
    st.sidebar.caption(f"Read-only source: `{DATABASE_PATH.name}`")

    filtered = filter_banking_data(
        data,
        start_date=start_date,
        end_date=end_date,
        cities=cities,
        account_types=account_types,
    )
    kpis = calculate_kpis(filtered)
    filters = _filter_summary(
        start_date,
        end_date,
        cities,
        account_types,
        all_cities,
        all_account_types,
    )

    st.markdown(
        '<div class="section-eyebrow">Portfolio intelligence</div>',
        unsafe_allow_html=True,
    )
    st.title("Banking Financial Analytics")
    st.markdown(
        '<p class="dashboard-subtitle">A live view of customer activity, '
        "financial flows and lending risk from your existing SQLite data.</p>",
        unsafe_allow_html=True,
    )

    metrics = [
        (
            "Total Customers",
            f"{kpis.total_customers:,}",
            "Customers who joined within the selected period and segment.",
        ),
        (
            "Total Transactions",
            f"{kpis.total_transactions:,}",
            "All matching transaction records, including failed transactions.",
        ),
        (
            "Total Deposits",
            _currency(kpis.total_deposits),
            "Successful Deposit transactions only; amounts follow the existing INR convention.",
        ),
        (
            "Total Withdrawals",
            _currency(kpis.total_withdrawals),
            "Successful Withdrawal transactions only; amounts follow the existing INR convention.",
        ),
        (
            "Total Loans",
            _currency(kpis.total_loan_amount),
            f"Principal amount across {kpis.total_loans:,} matching loan records.",
        ),
        (
            "Loan Default Rate",
            (
                f"{kpis.loan_default_rate:.2f}%"
                if kpis.loan_default_rate is not None
                else "N/A"
            ),
            "Defaulted loan records divided by all matching loan records.",
        ),
    ]
    for row_start in range(0, len(metrics), 3):
        metric_columns = st.columns(3, gap="medium")
        for column, (label, value, help_text) in zip(
            metric_columns, metrics[row_start : row_start + 3]
        ):
            column.metric(label, value, help=help_text)

    overview, customers_tab, transactions_tab, risk_tab, data_tab = st.tabs(
        [
            "Overview",
            "Customer Analytics",
            "Transaction Analytics",
            "Loans & Credit Risk",
            "Data & Exports",
        ]
    )

    with overview:
        st.subheader("At a glance")
        first_row = st.columns((1.45, 1))
        with first_row[0]:
            st.plotly_chart(
                transaction_trend_chart(filtered.transactions),
                width="stretch",
                key="overview-transaction-trend",
            )
        with first_row[1]:
            st.plotly_chart(
                loan_status_chart(filtered.loans),
                width="stretch",
                key="overview-loan-status",
            )
        second_row = st.columns(2)
        with second_row[0]:
            st.plotly_chart(
                customer_city_chart(filtered.customers),
                width="stretch",
                key="overview-customer-city",
            )
        with second_row[1]:
            st.plotly_chart(
                transaction_type_chart(filtered.transactions),
                width="stretch",
                key="overview-transaction-type",
            )
        st.caption(
            f"Reporting {filters['Reporting period']} · "
            f"{len(filtered.customers):,} customer cohort records, "
            f"{len(filtered.transactions):,} transactions and "
            f"{len(filtered.loans):,} loans after filtering."
        )

    with customers_tab:
        st.subheader("Customer analytics")
        first_row = st.columns(2)
        with first_row[0]:
            st.plotly_chart(
                customer_city_chart(filtered.customers),
                width="stretch",
                key="customer-city",
            )
        with first_row[1]:
            st.plotly_chart(
                customer_balance_chart(filtered.customers),
                width="stretch",
                key="customer-balance",
            )
        st.markdown("#### Customer records")
        _render_table(filtered.customers, "customer records", "customers")

    with transactions_tab:
        st.subheader("Transaction analytics")
        first_row = st.columns((1.4, 1))
        with first_row[0]:
            st.plotly_chart(
                transaction_trend_chart(filtered.transactions),
                width="stretch",
                key="transactions-trend",
            )
        with first_row[1]:
            st.plotly_chart(
                transaction_channel_chart(filtered.transactions),
                width="stretch",
                key="transactions-channel",
            )
        second_row = st.columns(2)
        with second_row[0]:
            st.plotly_chart(
                transaction_type_chart(filtered.transactions),
                width="stretch",
                key="transactions-type",
            )
        with second_row[1]:
            st.dataframe(
                transaction_type_summary(filtered.transactions),
                hide_index=True,
                width="stretch",
                key="transaction-type-summary",
            )
        st.markdown("#### Transaction records")
        _render_table(
            filtered.transactions, "transaction records", "transactions"
        )

    with risk_tab:
        st.subheader("Loan and credit risk")
        first_row = st.columns(2)
        with first_row[0]:
            st.plotly_chart(
                loan_status_chart(filtered.loans),
                width="stretch",
                key="risk-loan-status",
            )
        with first_row[1]:
            st.plotly_chart(
                credit_risk_chart(data.customers, filtered.loans),
                width="stretch",
                key="risk-credit-score",
            )
        second_row = st.columns(2)
        with second_row[0]:
            st.plotly_chart(
                loan_type_chart(filtered.loans),
                width="stretch",
                key="risk-loan-type",
            )
        with second_row[1]:
            st.plotly_chart(
                loan_city_risk_chart(data.customers, filtered.loans),
                width="stretch",
                key="risk-city-default",
            )
        st.markdown("#### Loan status summary")
        st.dataframe(
            loan_status_summary(filtered.loans),
            hide_index=True,
            width="stretch",
            key="loan-status-summary",
        )
        st.markdown("#### Credit risk by score band")
        st.dataframe(
            credit_risk_summary(data.customers, filtered.loans),
            hide_index=True,
            width="stretch",
            key="credit-risk-summary",
        )
        st.markdown("#### Loan records")
        _render_table(filtered.loans, "loan records", "loans")

    with data_tab:
        st.subheader("Filtered data")
        st.caption(
            "Use the search field to find rows and click column headings to sort."
        )
        with st.expander("Customer records", expanded=False):
            _render_table(
                filtered.customers, "customer records", "export-customers"
            )
        with st.expander("Transaction records", expanded=False):
            _render_table(
                filtered.transactions, "transaction records", "export-transactions"
            )
        with st.expander("Loan records", expanded=False):
            _render_table(filtered.loans, "loan records", "export-loans")

        st.markdown("#### Download filtered report")
        excel_bytes = _cached_excel_report(
            filtered.customers,
            filtered.transactions,
            filtered.loans,
            filters,
            data.customers,
        )
        pdf_bytes = _cached_pdf_report(
            filtered.customers,
            filtered.transactions,
            filtered.loans,
            filters,
            data.customers,
        )
        download_columns = st.columns(5)
        download_columns[0].download_button(
            "Excel report",
            data=excel_bytes,
            file_name="banking_financial_analytics.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
        download_columns[1].download_button(
            "Customers CSV",
            data=csv_bytes(filtered.customers),
            file_name="banking_customers.csv",
            mime="text/csv",
            width="stretch",
        )
        download_columns[2].download_button(
            "Transactions CSV",
            data=csv_bytes(filtered.transactions),
            file_name="banking_transactions.csv",
            mime="text/csv",
            width="stretch",
        )
        download_columns[3].download_button(
            "Loans CSV",
            data=csv_bytes(filtered.loans),
            file_name="banking_loans.csv",
            mime="text/csv",
            width="stretch",
        )
        download_columns[4].download_button(
            "PDF report",
            data=pdf_bytes,
            file_name="banking_financial_analytics.pdf",
            mime="application/pdf",
            width="stretch",
        )
        st.caption(
            "Exports use the active filters. The SQLite database is opened read-only."
        )


if __name__ == "__main__":
    main()
