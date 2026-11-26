
-- Read-only portfolio checks for the locally generated synthetic database.

SELECT 'customers' AS table_name, COUNT(*) AS record_count
FROM customers
UNION ALL
SELECT 'transactions', COUNT(*)
FROM transactions
UNION ALL
SELECT 'loans', COUNT(*)
FROM loans;

SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(CASE WHEN transaction_status = 'Success' THEN amount ELSE 0 END), 2)
        AS successful_amount
FROM transactions
GROUP BY transaction_type
ORDER BY transaction_type;

SELECT
    COUNT(*) AS total_loans,
    SUM(CASE WHEN loan_status = 'Default' THEN 1 ELSE 0 END) AS defaulted_loans,
    ROUND(
        100.0 * SUM(CASE WHEN loan_status = 'Default' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS default_rate_percent
FROM loans;
