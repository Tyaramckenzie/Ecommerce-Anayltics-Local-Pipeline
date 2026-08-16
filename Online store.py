#Data extraction:
# 1.) Downloaded from Kaggle -> 2.) Unzipped data locally 3.) Moved data into correct directory "GitHub projects"

#Data loading:
#Loaded csv file into pandas DataFrame

#Data inspection
#Check all columns available, check for nulls/NAs, describe data (~1M+ rows/transactions, data types, distribution)

import pandas as pd
from collections import Counter
import re


#Load CSV into pandas DataFrame
df = pd.read_csv("online_retail_II.csv")
print(df.head())
print(df.shape)
print(df.columns)
print(df.info())


#Data Inspection

#Check for missing values
df.isnull().sum()
#Customer ID column has 824,000 filled IDs while 243,007 are null : guest check out, returns, etc
#Description column has 1062989 filled product descriptions while 4, 382 are null

#Cleansing data

# Replace null entries with values / Drop missing customer IDs
df = df.dropna(subset=["Customer ID"])
# Replace missing descriptions
df["Description"] = df["Description"].fillna("UNKNOWN PRODUCT")


#Fix the data types
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["Customer ID"] = df["Customer ID"].astype(int)

#Remove invalid transactions
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

#------
#Adding columns/ providing more data for end user not offered from initial data source
#Revenue
df["Revenue"] = df["Quantity"] * df["Price"]
df["Total Price"] = df["Quantity"] * df["Price"]

#Date metrics
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.strftime("%Y-%m")

#NLP, scanning description column to make subsets of data for better dashboard use/analysis
# Combine all descriptions
all_descriptions = " ".join(df["Description"].astype(str))

# Extract words
words = re.findall(r'\b[A-Z]{3,}\b', all_descriptions.upper())

# Remove weak/common words
stop_words = {
    "SET", "OF", "AND", "THE",
    "WITH", "FOR", "TO", "IN", "ON"
}

filtered_words = [
    word for word in words
    if word not in stop_words
]

# Count word frequency
word_counts = Counter(filtered_words)

# Top 10 most repetitive words
top_10_words = [
    word for word, count in word_counts.most_common(10)
]

print("Top 10 Most Common Words:")
print(top_10_words)


# New column:
# repetitive_word

def repetitive_word(desc):
    desc = str(desc).upper()
    for word in top_10_words:
        if word in desc:
            return word
    return "OTHER"
df["repetitive_word"] = df["Description"].apply(repetitive_word)


# New column
# size_category
def size_category(desc):
    desc = str(desc).upper()
    if "SMALL" in desc:
        return "Small"
    elif "MEDIUM" in desc:
        return "Medium"
    elif "LARGE" in desc:
        return "Large"
    return "Unknown"

df["size_category"] = df["Description"].apply(size_category)


# New Columns
# Customer Segmentation : Wholesale vs Retail
def customer_segment(row):
    if row["Quantity"] > 10 or row["Total Price"] > 100:
        return "Wholesale"
    return "Retail"
df["customer_segment"] = df.apply(customer_segment, axis=1)


# New Column
# Seasonal item flags
def season_category(month):
    month_num = int(month.split("-")[1])
    if month_num in [11, 12]:
        return "Holiday Peak"
    elif month_num in [1, 2]:
        return "Winter"
    elif month_num in [3, 4, 5]:
        return "Spring"
    elif month_num in [6, 7, 8]:
        return "Summer"
    return "Fall"

df["season_category"] = df["Month"].apply(season_category)


# New column
# Price tiers
def price_tier(price):
    if price < 1:
        return "Budget"
    elif price <= 10:
        return "Standard"
    return "Premium"

df["price_tier"] = df["Price"].apply(price_tier)


# New column
# Repeat customer flags
# Calculate unique orders per customer
customer_unique_orders = df.groupby("Customer ID")["Invoice"].transform("nunique")

# Flag based on unique visits
df["repeat_customer"] = customer_unique_orders.apply(
    lambda x: "Repeat" if x > 1 else "One-Time"
)


# New Column
# Basket size analysis -> based on how much money is spent
def basket_size(total):
    if total < 20:
        return "Small Basket"
    elif total < 100:
        return "Medium Basket"
    return "Large Basket"

df["basket_size"] = df["Total Price"].apply(basket_size)


def get_region(Country):
    Country = str(Country).strip()

    mapping = {
        # Europe and Central Asia
        'Austria': 'Europe and Central Asia',
        'Belgium': 'Europe and Central Asia',
        'Channel Islands': 'Europe and Central Asia',
        'Cyprus': 'Europe and Central Asia',
        'Czech Republic': 'Europe and Central Asia',
        'Denmark': 'Europe and Central Asia',
        'EIRE': 'Europe and Central Asia',
        'European Community': 'Europe and Central Asia',
        'Finland': 'Europe and Central Asia',
        'France': 'Europe and Central Asia',
        'Germany': 'Europe and Central Asia',
        'Greece': 'Europe and Central Asia',
        'Iceland': 'Europe and Central Asia',
        'Italy': 'Europe and Central Asia',
        'Lithuania': 'Europe and Central Asia',
        'Malta': 'Europe and Central Asia',
        'Netherlands': 'Europe and Central Asia',
        'Norway': 'Europe and Central Asia',
        'Poland': 'Europe and Central Asia',
        'Portugal': 'Europe and Central Asia',
        'Spain': 'Europe and Central Asia',
        'Sweden': 'Europe and Central Asia',
        'Switzerland': 'Europe and Central Asia',
        'United Kingdom': 'Europe and Central Asia',

        # North America
        'Canada': 'North America',
        'USA': 'North America',

        # Latin America and Caribbean
        'Brazil': 'Latin America and Caribbean',
        'West Indies': 'Latin America and Caribbean',

        # Middle East and North Africa
        'Bahrain': 'Middle East and North Africa',
        'Israel': 'Middle East and North Africa',
        'Lebanon': 'Middle East and North Africa',
        'Saudi Arabia': 'Middle East and North Africa',
        'United Arab Emirates': 'Middle East and North Africa',

        # Sub-Saharan Africa
        'Nigeria': 'Sub-Saharan Africa',
        'RSA': 'Sub-Saharan Africa',

        # East Asia and Pacific
        'Australia': 'East Asia and Pacific',
        'Japan': 'East Asia and Pacific',
        'Korea': 'East Asia and Pacific',
        'Singapore': 'East Asia and Pacific',
        'Thailand': 'East Asia and Pacific',

        # South Asia - not present in list
    }

    # Return mapping or 'Unspecified' for the rest
    return mapping.get(Country, 'Unspecified/Other')


df['region'] = df['Country'].apply(get_region)


print(df.isnull().sum())
print(df.describe())

print(df[[
    "Description",
    "repetitive_word",
    "size_category",
    "customer_segment",
    "season_category",
    "price_tier",
    "repeat_customer",
    "basket_size"
]].head(10))

#Save file
df.to_csv("clean_retail_II.csv", index=False)

#Convert csv data table for SQL using a dictionary
df = df.rename(columns={
    "Invoice": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country",
    "Region": "region", #created
    "Revenue": "revenue", #created
    "Total Price": "total_price",
    "Year": "year", #created
    "Month": "month", #created
    "repetitive_word": "repetitive_word", #created
    "size_category": "size_category", # created
    "customer_segment" : "customer_segment", #created
    "season_category" : "season_category", #created
    "price_tier" : "price_tier", #created
    "repeat_customer": "repeat_customer" , #created
    "basket_size" : "basket_size" #created

})

#Schema validation
print(df.columns)
print(df.dtypes)
print(len(df))


df[["quantity", "unit_price"]].head()
df["invoice_date"] = pd.to_datetime(df["invoice_date"])

print(df["invoice_date"])
print(df["quantity"])

print(df.head(10))
print(df.columns.tolist())
print([repr(col) for col in df.columns])


df.columns = df.columns.str.strip()


#updated column selection list
df = df[[
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "region",
    "revenue",
    "total_price",
    "year",
    "month",
    "repetitive_word",
    "size_category",
    "customer_segment",
    "season_category",
    "price_tier",
    "repeat_customer",
    "basket_size"
]]

#Final assertion list
assert df.columns.tolist() == [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "region",
    "revenue",
    "total_price",
    "year",
    "month",
    "repetitive_word",
    "size_category",
    "customer_segment",
    "season_category",
    "price_tier",
    "repeat_customer",
    "basket_size"
]


#PostgresSQL connection format
#SQLAlchemy = translator
#psycopg2 = actual line to Postgres


from sqlalchemy import create_engine
print("OK")

engine = create_engine(
    "postgresql+psycopg2://tyaramckenzie@localhost:5432/retail_project"
)

with engine.connect() as conn:
    print("CONNECTED TO retail_project")

#Loading DataFrame into postgreSQL
df.to_sql(
    "raw_transactions",
    engine,
    if_exists="replace",
    index=False,
    chunksize=5000,
    method="multi"
)



#PostgreSQL to DuckDB
import duckdb
con = duckdb.connect('analytics.duckdb')
con.execute("""
INSTALL postgres;
LOAD postgres;
""")

con.execute("""
ATTACH 'dbname=retail_project user=tyaramckenzie host=localhost' AS pg (TYPE postgres);
""")


#Create Warehouse table
#Load from Postgres
#Load into DuckDB
con.execute("""
CREATE OR REPLACE TABLE transactions AS 
SELECT * FROM pg.raw_transactions
""")

#Run analytics
con.execute("""
SELECT 
    country,
    SUM(total_price) AS revenue
FROM transactions
GROUP BY country
ORDER BY revenue DESC
""").df()


#Open DuckDB - show tables in DuckDB
print(con.execute("SHOW TABLES").fetchall())


#Export warehouse table for Tableau
final_df = con.execute("""
SELECT * FROM transactions
""").df()

final_df.to_csv("tableau_retail_data.csv", index=False)

#Closing Database connection to DuckDB
con.close()


