
import pandas as pd
import numpy as np

# ==================================
# BANKING & FINANCIAL ANALYTICS
# ==================================

# Loading datasets

customers = pd.read_csv("dataset/customers.csv")

transactions = pd.read_csv("dataset/transactions.csv")

loans = pd.read_csv("dataset/loans.csv")


# Display project heading

print("=" * 50)
print("BANKING & FINANCIAL ANALYTICS PROJECT")
print("=" * 50)


# Display Customer Data

print("\n CUSTOMER DATA")
print(customers.head())


# Display Transaction Data

print("\n TRANSACTION DATA")
print(transactions.head())


# Display Loan Data

print("\n LOAN DATA")
print(loans.head())


# Dataset Information

print("\n DATASET SHAPES")

print("Customers:", customers.shape)

print("Transactions:", transactions.shape)

print("Loans:", loans.shape)

# ==================================
# DATA CLEANING
# ==================================

print("\n===== MISSING VALUES CHECK =====")

print("\nCustomer Missing Values:")
print(customers.isnull().sum())

print("\nTransaction Missing Values:")
print(transactions.isnull().sum())

print("\nLoan Missing Values:")
print(loans.isnull().sum())

print("\n===== DUPLICATE RECORDS =====")

print("Customers:", customers.duplicated().sum())

print("Transactions:", transactions.duplicated().sum())

print("Loans:", loans.duplicated().sum())

print("\n===== DATA TYPES =====")

print(customers.dtypes)

print(transactions.dtypes)

print(loans.dtypes)

# ==================================
# DATE FORMAT CONVERSION
# ==================================

customers["join_date"] = pd.to_datetime(
    customers["join_date"]
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

loans["loan_date"] = pd.to_datetime(
    loans["loan_date"]
)

print("\n===== UPDATED DATA TYPES =====")

print(customers.dtypes)
print(transactions.dtypes)
print(loans.dtypes)


import sqlite3
import pandas as pd

# Connect to SQLite database

conn = sqlite3.connect("banking.db")

# Load CSV datasets

customers = pd.read_csv("dataset/customers.csv")
transactions = pd.read_csv("dataset/transactions.csv")
loans = pd.read_csv("dataset/loans.csv")

# Convert datasets into SQL tables

customers.to_sql(
    "customers",
    conn,
    if_exists="replace",
    index=False
)

transactions.to_sql(
    "transactions",
    conn,
    if_exists="replace",
    index=False
)

loans.to_sql(
    "loans",
    conn,
    if_exists="replace",
    index=False
)

print("All tables created successfully!")

# Verify tables

cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

print(cursor.fetchall())

conn.close()
