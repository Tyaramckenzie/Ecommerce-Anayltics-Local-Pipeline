# Retail Analytics & Customer Behavior Pipeline

## Project Overview

This project is an end-to-end retail analytics pipeline built using:

* Python
* Pandas
* PostgreSQL
* DuckDB
* Tableau

The goal of the project is to transform raw transactional retail data into a structured analytics warehouse capable of supporting business intelligence dashboards and customer behavior analysis.

The dataset was sourced from Kaggle using the Online Retail II dataset.

---

# Tech Stack

| Layer                | Technology      |
| -------------------- | --------------- |
| Data Source          | Kaggle CSV      |
| Data Processing      | Python + Pandas |
| Relational Database  | PostgreSQL      |
| Analytical Warehouse | DuckDB          |
| Visualization        | Tableau         |


---

# Business Objectives

The project analyzes:

* Revenue trends
* Customer segmentation
* Product purchasing behavior
* Seasonal sales trends
* Basket size analysis
* Repeat customer behavior
* Product description NLP categorization

---

# ETL Pipeline Architecture

```text
Kaggle CSV
    ↓
Python/Pandas Cleaning & Feature Engineering
    ↓
PostgreSQL Relational Storage
    ↓
DuckDB Analytical Warehouse
    ↓
Tableau Dashboard
```

---

# Data Engineering Process

## 1. Data Extraction

The dataset was downloaded from Kaggle using the Kaggle API.

### Steps

1. Generated Kaggle API token
2. Downloaded dataset using terminal
3. Unzipped dataset locally
4. Moved dataset into project directory

### Kaggle Command

```bash
kaggle datasets download -d mashlyn/online-retail-ii-uci
```

---

# 2. Data Loading

The CSV file was loaded into a Pandas DataFrame.

```python
import pandas as pd

df = pd.read_csv("online_retail_II.csv")
```

---

# 3. Data Inspection

Initial inspection included:

* Viewing columns
* Checking row counts
* Identifying null values
* Validating data types
* Reviewing transaction distributions

### Key Findings

* Over 1 million retail transaction rows
* Missing Customer IDs
* Missing product descriptions
* Mixed data types

---

# 4. Data Cleansing

Data cleansing steps included:

## Null Handling

* Removed rows missing Customer IDs
* Replaced missing descriptions with placeholder values

## Data Type Standardization

* Converted InvoiceDate to datetime
* Converted Customer ID to integer

## Invalid Transaction Removal

* Removed negative quantities
* Removed negative or zero pricing

---

# 5. Feature Engineering

Additional analytical columns were created.

## Revenue Metrics

* revenue
* total_price

## Time Intelligence

* year
* month
* season_category

## NLP Categorization

* repetitive_word
* size_category

## Customer Analytics

* customer_segment
* repeat_customer

## Pricing Analytics

* price_tier

## Basket Analytics

* basket_size

---

# 6. PostgreSQL Loading

The cleaned dataset was loaded into PostgreSQL using SQLAlchemy.

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://username@localhost:5432/retail_project"
)
```

The DataFrame was inserted into a relational table:

```python
df.to_sql(
    "raw_transactions",
    engine,
    if_exists="replace",
    index=False
)
```

---

# 7. DuckDB Analytical Warehouse

DuckDB was used as the analytical warehouse layer.

PostgreSQL tables were attached directly into DuckDB.

```python
ATTACH 'dbname=retail_project user=username host=localhost'
AS pg (TYPE postgres);
```

Warehouse table creation:

```sql
CREATE OR REPLACE TABLE transactions AS
SELECT * FROM pg.raw_transactions;
```

---


