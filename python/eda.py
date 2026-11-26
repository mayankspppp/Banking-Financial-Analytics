
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset

customers = pd.read_csv("dataset/customers.csv")
transactions = pd.read_csv("dataset/transactions.csv")
loans = pd.read_csv("dataset/loans.csv")


# =================================
# 1. BASIC STATISTICAL ANALYSIS
# =================================

print("\nCUSTOMER STATISTICS")

print(customers.describe())


print("\nTRANSACTION STATISTICS")

print(transactions.describe())


print("\nLOAN STATISTICS")

print(loans.describe())

# =====================================
# TRANSACTION TYPE ANALYSIS
# =====================================

print("\n===== TRANSACTION TYPE ANALYSIS =====")

transaction_analysis = transactions.groupby(
    "transaction_type"
)["amount"].agg(
    ["count", "sum", "mean"]
)

print(transaction_analysis)

# =====================================
# DATA VISUALIZATION
# =====================================

# Transaction count by type

transaction_count = transactions["transaction_type"].value_counts()

plt.figure(figsize=(10, 5))

plt.bar(
    transaction_count.index,
    transaction_count.values
)

plt.title("Banking Transaction Count by Type")

plt.xlabel("Transaction Type")

plt.ylabel("Number of Transactions")

plt.xticks(rotation=15)

plt.tight_layout()

plt.show()

# =====================================
# MONTHLY TRANSACTION ANALYSIS
# =====================================

# Convert transaction date into datetime

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

# Extract month

transactions["month"] = transactions[
    "transaction_date"
].dt.month_name()

# Monthly transaction count

monthly_transactions = transactions.groupby(
    "month"
).size()


# =====================================
# MONTHLY TRANSACTION ANALYSIS
# =====================================

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

# Extract month number
transactions["month_number"] = (
    transactions["transaction_date"].dt.month
)

# Group by month number
monthly_transactions = (
    transactions.groupby("month_number")
    .size()
    .sort_index()
)

# Convert month numbers into names
month_names = [
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September",
    "October", "November", "December"
]

monthly_transactions.index = [
    month_names[i - 1]
    for i in monthly_transactions.index
]

print("\nMONTHLY TRANSACTION ANALYSIS")
print(monthly_transactions)

# Visualization
plt.figure(figsize=(10, 5))

plt.bar(
    monthly_transactions.index,
    monthly_transactions.values
)

plt.title("Monthly Banking Transactions")
plt.xlabel("Month")
plt.ylabel("Number of Transactions")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# =====================================
# LOAN ANALYTICS
# =====================================

print("\n===== LOAN ANALYTICS =====")

# 1. Total number of loans

print("\nTotal Loans:", len(loans))


# 2. Loan status analysis

print("\nLOAN STATUS ANALYSIS")

loan_status = loans["loan_status"].value_counts()

print(loan_status)


# 3. Loan type analysis

print("\nLOAN TYPE ANALYSIS")

loan_type = loans.groupby(
    "loan_type"
)["loan_amount"].agg(
    ["count", "sum", "mean"]
)

print(loan_type)


# 4. Average loan amount

print("\nAverage Loan Amount:")

print(loans["loan_amount"].mean())


# 5. Total loan amount

print("\nTotal Loan Amount:")

print(loans["loan_amount"].sum())


# =====================================
# LOAN STATUS VISUALIZATION
# =====================================

loan_status = loans["loan_status"].value_counts()

plt.figure(figsize=(9, 5))

plt.bar(
    loan_status.index,
    loan_status.values
)

plt.title("Bank Loan Status Analysis")

plt.xlabel("Loan Status")

plt.ylabel("Number of Loans")

plt.tight_layout()

plt.show()


# =====================================
# LOAN TYPE VISUALIZATION
# =====================================

loan_type_amount = loans.groupby(
    "loan_type"
)["loan_amount"].sum()

plt.figure(figsize=(10, 5))

plt.bar(
    loan_type_amount.index,
    loan_type_amount.values
)

plt.title("Total Loan Amount by Loan Type")

plt.xlabel("Loan Type")

plt.ylabel("Total Loan Amount")

plt.xticks(rotation=20)

plt.tight_layout()

plt.show()
