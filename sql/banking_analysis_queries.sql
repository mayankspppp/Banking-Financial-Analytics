-- ============================================================
-- BANKING & FINANCIAL ANALYTICS | SQL REVISION FILE
-- Database: banking.db
-- Tables: customers, transactions, loans
---- ============================================================

-- 1. CHECK TABLES
SELECT name
FROM sqlite_master
WHERE type = 'table';


-- 2. BASIC TABLE COUNTS
SELECT COUNT(*) AS total_customers FROM customers;

SELECT COUNT(*) AS total_transactions FROM transactions;

SELECT COUNT(*) AS total_loans FROM loans;


-- 3. TOTAL BANK BALANCE
SELECT ROUND(SUM(account_balance), 2) AS total_bank_balance
FROM customers;


-- 4. TRANSACTION TYPE ANALYSIS
SELECT
    transaction_type,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount
FROM transactions
GROUP BY transaction_type
ORDER BY total_transactions DESC;


-- 5. CUSTOMER TRANSACTION ANALYSIS
SELECT
    c.customer_id,
    c.city,
    c.account_type,
    t.transaction_type,
    t.amount,
    t.transaction_date
FROM customers c
INNER JOIN transactions t
    ON c.customer_id = t.customer_id
LIMIT 10;


-- 6. CITY-WISE TRANSACTION ANALYSIS
SELECT
    c.city,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(SUM(t.amount), 2) AS total_amount,
    ROUND(AVG(t.amount), 2) AS average_amount
FROM customers c
INNER JOIN transactions t
    ON c.customer_id = t.customer_id
GROUP BY c.city
ORDER BY total_transactions DESC;


-- 7. ACCOUNT TYPE ANALYSIS
SELECT
    account_type,
    COUNT(*) AS total_customers,
    ROUND(AVG(account_balance), 2) AS average_balance,
    ROUND(SUM(account_balance), 2) AS total_balance
FROM customers
GROUP BY account_type
ORDER BY total_customers DESC;


-- 8. TOP 10 HIGH-VALUE CUSTOMERS
SELECT
    customer_id,
    city,
    account_type,
    account_balance,
    credit_score
FROM customers
ORDER BY account_balance DESC
LIMIT 10;


-- 9. CREDIT SCORE CATEGORY ANALYSIS
SELECT
    CASE
        WHEN credit_score >= 750 THEN 'Excellent'
        WHEN credit_score >= 700 THEN 'Good'
        WHEN credit_score >= 650 THEN 'Average'
        ELSE 'Low'
    END AS credit_category,
    COUNT(*) AS total_customers,
    ROUND(AVG(credit_score), 2) AS average_score
FROM customers
GROUP BY credit_category
ORDER BY average_score DESC;


-- 10. LOAN STATUS ANALYSIS
SELECT
    loan_status,
    COUNT(*) AS total_loans,
    ROUND(SUM(loan_amount), 2) AS total_loan_amount,
    ROUND(AVG(interest_rate_pct), 2) AS average_interest_rate
FROM loans
GROUP BY loan_status
ORDER BY total_loans DESC;


-- 11. CREDIT SCORE VS LOAN DEFAULT ANALYSIS
SELECT
    CASE
        WHEN c.credit_score >= 750 THEN 'Excellent'
        WHEN c.credit_score >= 700 THEN 'Good'
        WHEN c.credit_score >= 650 THEN 'Average'
        ELSE 'Low'
    END AS credit_category,
    COUNT(l.loan_id) AS total_loans,
    SUM(
        CASE
            WHEN l.loan_status = 'Default' THEN 1
            ELSE 0
        END
    ) AS default_loans,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN l.loan_status = 'Default' THEN 1
                ELSE 0
            END
        ) / COUNT(l.loan_id),
        2
    ) AS default_percentage
FROM customers c
INNER JOIN loans l
    ON c.customer_id = l.customer_id
GROUP BY credit_category
ORDER BY default_percentage DESC;



-- 12. CITY-WISE LOAN RISK ANALYSIS

WITH city_loan_risk AS (

    SELECT
        c.city,

        COUNT(l.loan_id) AS total_loans,

        SUM(
            CASE
                WHEN l.loan_status = 'Default'
                THEN 1
                ELSE 0
            END
        ) AS default_loans,

        ROUND(
            100.0 * SUM(
                CASE
                    WHEN l.loan_status = 'Default'
                    THEN 1
                    ELSE 0
                END
            ) / COUNT(l.loan_id),
            2
        ) AS default_percentage,

        ROUND(SUM(l.loan_amount), 2) AS total_loan_amount

    FROM customers c

    INNER JOIN loans l
        ON c.customer_id = l.customer_id

    GROUP BY c.city
)

SELECT *
FROM city_loan_risk
ORDER BY default_percentage DESC;

-- ROW_NUMBER: TOP CUSTOMERS

SELECT
    customer_id,
    city,
    account_balance,

    ROW_NUMBER() OVER(
        ORDER BY account_balance DESC
    ) AS row_num

FROM customers

LIMIT 10;

-- Rank():

SELECT
    customer_id,
    account_balance,
    RANK() OVER(
        ORDER BY account_balance DESC
    ) AS customer_rank
FROM customers
LIMIT 10;

--RANK() vs DENSE_RANK():

SELECT
    customer_id,
    account_balance,
    DENSE_RANK() OVER(
        ORDER BY account_balance DESC
    ) AS customer_rank
FROM customers
LIMIT 10;

--compare all():

SELECT
    customer_id,
    account_balance,

    ROW_NUMBER() OVER(
        ORDER BY account_balance DESC
    ) AS row_num,

    RANK() OVER(
        ORDER BY account_balance DESC
    ) AS rank_num,

    DENSE_RANK() OVER(
        ORDER BY account_balance DESC
    ) AS dense_rank_num

FROM customers
LIMIT 10;

---PARTITION BY:
SELECT
    customer_id,
    city,
    account_balance,

    RANK() OVER(
        PARTITION BY city
        ORDER BY account_balance DESC
    ) AS city_rank

FROM customers
ORDER BY city, city_rank;

----PARTITION BY, RANK() aur CTE ko combine karenge.

WITH customer_ranking AS (
    SELECT
        customer_id,
        city,
        account_balance,
        RANK() OVER(
            PARTITION BY city
            ORDER BY account_balance DESC
        ) AS city_rank
    FROM customers
)

SELECT *
FROM customer_ranking
WHERE city_rank <= 3
ORDER BY city, city_rank;

---Aggregate Window Functions : SUM() OVER() – Total transaction amount

SELECT
    transaction_id,
    customer_id,
    amount,

    SUM(amount) OVER() AS total_transaction_amount

FROM transactions
LIMIT 10;

-----Running Total (Cumulative Sum):

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    SUM(amount) OVER(
        ORDER BY transaction_date, transaction_id
    ) AS running_total

FROM transactions
LIMIT 10;

--------Customer-wise Running Total:

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    SUM(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS customer_running_total

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

-----AVG() OVER():

SELECT
    transaction_id,
    customer_id,
    amount,

    ROUND(AVG(amount) OVER(), 2) AS average_transaction_amount

FROM transactions
LIMIT 10;

------------customer-wise average transaction amount.:

SELECT
    transaction_id,
    customer_id,
    amount,

    ROUND(
        AVG(amount) OVER(
            PARTITION BY customer_id
        ), 2
    ) AS customer_avg_transaction

FROM transactions
LIMIT 20;

-----LAG(): 

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    LAG(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS previous_transaction_amount

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

----LEAD():

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    LEAD(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS next_transaction_amount

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

-------Previous vs Next Transaction():

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    LAG(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS previous_amount,

    LEAD(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS next_amount,

    amount - LAG(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS amount_difference

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

-----------ROW_NUMBER(): arrange customer balance

SELECT
    customer_id,
    city,
    account_balance,
    ROW_NUMBER() OVER(
        ORDER BY account_balance DESC
    ) AS row_num
FROM customers
LIMIT 10;

------------------RANK():

SELECT
    customer_id,
    city,
    account_balance,
    RANK() OVER(
        ORDER BY account_balance DESC
    ) AS customer_rank
FROM customers
LIMIT 10;

--------DENSE_RANK():

SELECT
    customer_id,
    city,
    account_balance,
    DENSE_RANK() OVER(
        ORDER BY account_balance DESC
    ) AS dense_rank
FROM customers
LIMIT 10;

------difference above three ():

SELECT
    customer_id,
    city,
    account_balance,

    ROW_NUMBER() OVER(
        ORDER BY account_balance DESC
    ) AS row_num,

    RANK() OVER(
        ORDER BY account_balance DESC
    ) AS customer_rank,

    DENSE_RANK() OVER(
        ORDER BY account_balance DESC
    ) AS dense_rank

FROM customers
LIMIT 10;

---------PARTITION BY(): in each city high account balance customer?

SELECT
    customer_id,
    city,
    account_balance,

    RANK() OVER(
        PARTITION BY city
        ORDER BY account_balance DESC
    ) AS city_rank

FROM customers
ORDER BY city, city_rank;

----------CTE + RANK() + WHERE(): top 3 customer in each city

WITH city_ranking AS (
    SELECT
        customer_id,
        city,
        account_balance,

        RANK() OVER(
            PARTITION BY city
            ORDER BY account_balance DESC
        ) AS city_rank

    FROM customers
)

SELECT *
FROM city_ranking
WHERE city_rank <= 3
ORDER BY city, city_rank;

-------------------LAG() and LEAD():
----------LAG() — fetch previous amount.
----------LEAD() — fetch next transaction.

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    LAG(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS previous_amount,

    LEAD(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS next_amount

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

--------practical business analysis(): behaviour of customer,current transaction, previous transaction.

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    LAG(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
    ) AS previous_amount,

    ROUND(
        amount - LAG(amount) OVER(
            PARTITION BY customer_id
            ORDER BY transaction_date, transaction_id
        ), 2
    ) AS amount_difference

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

--------Running Total(): transaction ke saath customer ka cumulative transaction amount calculate karna.

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    amount,

    SUM(amount) OVER(
        PARTITION BY customer_id
        ORDER BY transaction_date, transaction_id
        ROWS BETWEEN UNBOUNDED PRECEDING
        AND CURRENT ROW
    ) AS running_total

FROM transactions
ORDER BY customer_id, transaction_date, transaction_id
LIMIT 20;

--------ROUND():
SELECT
    ROUND(8170.379999, 2) AS rounded_amount;

------------Customer Total Amount():

SELECT
    transaction_id,
    customer_id,
    amount,

    ROUND(
        SUM(amount) OVER(
            PARTITION BY customer_id
        ), 2
    ) AS customer_total_amount

FROM transactions
LIMIT 20;