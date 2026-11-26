from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from dashboard.analytics import (
    credit_risk_summary,
    customer_city_summary,
    loan_city_risk_summary,
    transaction_type_summary,
)

PANEL = "#111B27"
TEXT = "#E8EEF6"
MUTED = "#93A4B8"
GRID = "rgba(147, 164, 184, 0.16)"
PALETTE = ["#56D6BE", "#8FA8FF", "#F5B85B", "#F1788B", "#B59AF7"]


def _style(figure: go.Figure, title: str, height: int = 340) -> go.Figure:
    figure.update_layout(
        title={
            "text": title,
            "x": 0.02,
            "xanchor": "left",
            "font": {"size": 16, "color": TEXT},
        },
        template="plotly_dark",
        height=height,
        margin={"l": 18, "r": 18, "t": 58, "b": 30},
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font={"family": "Inter, sans-serif", "color": TEXT},
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": MUTED, "size": 11},
            "orientation": "h",
            "y": -0.2,
        },
        hoverlabel={
            "bgcolor": "#172433",
            "bordercolor": "rgba(86, 214, 190, 0.45)",
            "font": {"color": TEXT, "family": "Inter, sans-serif", "size": 12},
            "align": "left",
            "namelength": -1,
        },
        hovermode="closest",
    )
    figure.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID)
    figure.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        automargin=True,
        tickfont={"color": MUTED, "size": 10},
    )
    return figure


def _empty_figure(title: str) -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text="No records match the selected filters.",
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"color": MUTED, "size": 13},
    )
    return _style(figure, title)


def customer_city_chart(customers: pd.DataFrame) -> go.Figure:
    summary = customer_city_summary(customers)
    if summary.empty:
        return _empty_figure("Customers by city and account type")
    figure = px.bar(
        summary,
        x="city",
        y="customer_count",
        color="account_type",
        barmode="group",
        color_discrete_sequence=PALETTE,
        labels={
            "city": "City",
            "customer_count": "Customers",
            "account_type": "Account type",
        },
    )
    figure.update_traces(
        hovertemplate="%{x}<br>%{fullData.name}: %{y:,} customers<extra></extra>"
    )
    return _style(figure, "Customers by city and account type")


def customer_balance_chart(customers: pd.DataFrame) -> go.Figure:
    if customers.empty:
        return _empty_figure("Account balances and credit scores")
    figure = px.scatter(
        customers,
        x="credit_score",
        y="account_balance",
        color="account_type",
        hover_data=["city", "customer_id"],
        color_discrete_sequence=PALETTE,
        labels={
            "credit_score": "Credit score",
            "account_balance": "Account balance",
            "account_type": "Account type",
        },
    )
    figure.update_traces(
        hovertemplate=(
            "Credit score: %{x}<br>Balance: ₹%{y:,.2f}<br>"
            "Account: %{fullData.name}<br>City: %{customdata[0]}<br>"
            "Customer: %{customdata[1]}<extra></extra>"
        )
    )
    return _style(figure, "Account balances and credit scores")


def transaction_trend_chart(transactions: pd.DataFrame) -> go.Figure:
    if transactions.empty:
        return _empty_figure("Monthly transaction activity")
    monthly = (
        transactions.assign(
            month=transactions["transaction_date"].dt.to_period("M").dt.to_timestamp()
        )
        .groupby(["month", "transaction_status"], as_index=False, observed=True)
        .agg(transaction_count=("transaction_id", "count"))
    )
    figure = px.line(
        monthly,
        x="month",
        y="transaction_count",
        color="transaction_status",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={
            "month": "Month",
            "transaction_count": "Transactions",
            "transaction_status": "Status",
        },
    )
    figure.update_traces(
        hovertemplate="%{x|%b %Y}<br>%{fullData.name}: %{y:,} transactions<extra></extra>"
    )
    return _style(figure, "Monthly transaction activity")


def transaction_type_chart(transactions: pd.DataFrame) -> go.Figure:
    summary = transaction_type_summary(transactions)
    if summary.empty:
        return _empty_figure("Successful transaction value by type")
    figure = px.bar(
        summary,
        x="transaction_type",
        y="successful_amount",
        color="transaction_type",
        color_discrete_sequence=PALETTE,
        labels={
            "transaction_type": "Transaction type",
            "successful_amount": "Successful amount",
        },
    )
    figure.update_traces(
        hovertemplate="%{x}<br>Successful value: ₹%{y:,.2f}<extra></extra>"
    )
    figure.update_layout(showlegend=False)
    return _style(figure, "Successful transaction value by type")


def transaction_channel_chart(transactions: pd.DataFrame) -> go.Figure:
    if transactions.empty:
        return _empty_figure("Transactions by channel")
    summary = (
        transactions.groupby("channel", as_index=False, observed=True)
        .agg(transaction_count=("transaction_id", "count"))
        .sort_values("channel")
    )
    figure = px.pie(
        summary,
        names="channel",
        values="transaction_count",
        hole=0.62,
        color_discrete_sequence=PALETTE,
        labels={"channel": "Channel", "transaction_count": "Transactions"},
    )
    figure.update_traces(
        hovertemplate="%{label}<br>Transactions: %{value:,}<br>Share: %{percent}<extra></extra>"
    )
    return _style(figure, "Transactions by channel")


def loan_status_chart(loans: pd.DataFrame) -> go.Figure:
    if loans.empty:
        return _empty_figure("Loan portfolio by status")
    summary = (
        loans.groupby("loan_status", as_index=False, observed=True)
        .agg(loan_count=("loan_id", "count"))
        .sort_values("loan_status")
    )
    figure = px.pie(
        summary,
        names="loan_status",
        values="loan_count",
        hole=0.62,
        color_discrete_sequence=PALETTE,
        labels={"loan_status": "Loan status", "loan_count": "Loans"},
    )
    figure.update_traces(
        hovertemplate="%{label}<br>Loans: %{value:,}<br>Share: %{percent}<extra></extra>"
    )
    return _style(figure, "Loan portfolio by status")


def credit_risk_chart(customers: pd.DataFrame, loans: pd.DataFrame) -> go.Figure:
    summary = credit_risk_summary(customers, loans)
    if summary.empty:
        return _empty_figure("Default rate by customer credit score")
    figure = px.bar(
        summary,
        x="credit_category",
        y="default_rate",
        custom_data=["loan_count", "default_count"],
        color="credit_category",
        color_discrete_sequence=PALETTE,
        labels={
            "credit_category": "Credit score band",
            "default_rate": "Default rate (%)",
        },
    )
    figure.update_traces(
        hovertemplate=(
            "%{x}<br>Default rate: %{y:.2f}%<br>"
            "Defaults: %{customdata[1]:,} / %{customdata[0]:,} loans"
            "<extra></extra>"
        )
    )
    figure.update_layout(showlegend=False)
    return _style(figure, "Default rate by customer credit score")


def loan_type_chart(loans: pd.DataFrame) -> go.Figure:
    if loans.empty:
        return _empty_figure("Loan value by type and status")
    summary = (
        loans.groupby(["loan_type", "loan_status"], as_index=False, observed=True)
        .agg(total_loan_amount=("loan_amount", "sum"))
        .sort_values(["loan_type", "loan_status"])
    )
    figure = px.bar(
        summary,
        x="loan_type",
        y="total_loan_amount",
        color="loan_status",
        barmode="stack",
        color_discrete_sequence=PALETTE,
        labels={
            "loan_type": "Loan type",
            "total_loan_amount": "Loan amount",
            "loan_status": "Status",
        },
    )
    figure.update_traces(
        hovertemplate=(
            "%{x}<br>Status: %{fullData.name}<br>"
            "Loan value: ₹%{y:,.2f}<extra></extra>"
        )
    )
    return _style(figure, "Loan value by type and status")


def loan_city_risk_chart(customers: pd.DataFrame, loans: pd.DataFrame) -> go.Figure:
    summary = loan_city_risk_summary(customers, loans)
    if summary.empty:
        return _empty_figure("Loan default rate by city")
    figure = px.bar(
        summary,
        x="city",
        y="default_rate",
        custom_data=["loan_count", "default_count"],
        color="default_rate",
        color_continuous_scale=["#56D6BE", "#F5B85B", "#F1788B"],
        labels={"city": "City", "default_rate": "Default rate (%)"},
    )
    figure.update_traces(
        hovertemplate=(
            "%{x}<br>Default rate: %{y:.2f}%<br>"
            "Defaults: %{customdata[1]:,} / %{customdata[0]:,} loans"
            "<extra></extra>"
        )
    )
    figure.update_layout(coloraxis_showscale=False)
    return _style(figure, "Loan default rate by city")