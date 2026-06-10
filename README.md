# ==========================================
# Final Assignment: Acquiring and Processing
# Information on the World's Largest Banks
# ==========================================

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3

# -----------------------------
# Global Variables
# -----------------------------
url = "https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks"

table_attribs = ["Name", "MC_USD_Billion"]

csv_path = "Largest_banks_data.csv"
db_name = "Banks.db"
table_name = "Largest_banks"
log_file = "code_log.txt"

# -----------------------------
# Log Progress Function
# -----------------------------
def log_progress(message):

    timestamp_format = '%Y-%m-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)

    with open(log_file, "a") as f:
        f.write(timestamp + " : " + message + "\n")

# -----------------------------
# Extract Function
# -----------------------------
def extract(url, table_attribs):

    html_page = requests.get(url).text

    data = BeautifulSoup(html_page, 'html.parser')

    df = pd.DataFrame(columns=table_attribs)

    tables = data.find_all('tbody')

    rows = tables[0].find_all('tr')

    for row in rows:

        col = row.find_all('td')

        if len(col) != 0:

            bank_name = col[1].find_all('a')[1]['title']

            market_cap = float(col[2].contents[0])

            data_dict = {
                "Name": bank_name,
                "MC_USD_Billion": market_cap
            }

            temp_df = pd.DataFrame(data_dict, index=[0])

            df = pd.concat([df, temp_df], ignore_index=True)

    return df

# -----------------------------
# Transform Function
# -----------------------------
def transform(df, exchange_rate_csv):

    exchange_rate = pd.read_csv(exchange_rate_csv)

    exchange_rate.set_index('Currency', inplace=True)

    GBP_rate = exchange_rate.loc['GBP', 'Rate']
    EUR_rate = exchange_rate.loc['EUR', 'Rate']
    INR_rate = exchange_rate.loc['INR', 'Rate']

    df["MC_GBP_Billion"] = np.round(
        df["MC_USD_Billion"] * GBP_rate, 2)

    df["MC_EUR_Billion"] = np.round(
        df["MC_USD_Billion"] * EUR_rate, 2)

    df["MC_INR_Billion"] = np.round(
        df["MC_USD_Billion"] * INR_rate, 2)

    return df

# -----------------------------
# Load to CSV Function
# -----------------------------
def load_to_csv(df, output_path):

    df.to_csv(output_path, index=False)

# -----------------------------
# Load to Database Function
# -----------------------------
def load_to_db(df, sql_connection, table_name):

    df.to_sql(
        table_name,
        sql_connection,
        if_exists='replace',
        index=False
    )

# -----------------------------
# Run Query Function
# -----------------------------
def run_query(query_statement, sql_connection):

    print(query_statement)

    query_output = pd.read_sql(query_statement, sql_connection)

    print(query_output)

    log_progress("Query executed successfully")

# -----------------------------
# ETL Process
# -----------------------------
log_progress("Preliminaries complete. Initiating ETL process")

df = extract(url, table_attribs)

log_progress(
    "Data extraction complete. Initiating Transformation process")

df = transform(df, "exchange_rate.csv")

log_progress(
    "Data transformation complete. Initiating Loading process")

load_to_csv(df, csv_path)

log_progress("Data saved to CSV file")

connection = sqlite3.connect(db_name)

load_to_db(df, connection, table_name)

log_progress(
    "Data loaded to Database as a table. Executing queries")

query_statement = f"SELECT * FROM {table_name}"
run_query(query_statement, connection)

query_statement = f"""
SELECT AVG(MC_GBP_Billion)
FROM {table_name}
"""
run_query(query_statement, connection)

query_statement = f"""
SELECT Name
FROM {table_name}
LIMIT 5
"""
run_query(query_statement, connection)

log_progress("Process Complete")

connection.close()
