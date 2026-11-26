# Banking & Financial Analytics — Synthetic Dataset

This project dataset is synthetic and contains no real customer or bank information.

Files:
- customers.csv: 500 customer records
- transactions.csv: 5,000 transaction records
- loans.csv: 800 loan records

Join keys:
- customers.customer_id = transactions.customer_id
- customers.customer_id = loans.customer_id

Suggested first tasks:
1. Inspect shape, columns, data types, and missing values.
2. Check duplicate customer_id, transaction_id, and loan_id.
3. Convert date columns to datetime.
4. Summarize transaction amount by type and channel.
5. Calculate loan counts and default rate by loan type.
