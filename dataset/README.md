# Fictional demonstration data

The CSV files in this directory are generated locally by
[`python/generate_synthetic_data.py`](../python/generate_synthetic_data.py).
They are not source data and are not included in Git.

The generator defaults to 500 customers, 5,000 transactions, and 800 loans.
Names are Faker-generated and prefixed with `Demo`; IDs, dates, locations,
balances, credit scores, transaction details, and loan details are generated
from the selected reproducible seed. No original project database, workbook,
or CSV records are read or copied. The generated SQLite database contains a
metadata label identifying it as **FICTIONAL DEMONSTRATION DATA**.
