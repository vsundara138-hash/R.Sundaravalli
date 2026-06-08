from datetime import datetime
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup


# 1.1 log_progress function (1 point)
def log_progress(message):
    """Logs a given message with a timestamp to code_log.txt."""
    timestamp_format = "%Y-%b-%d-%H:%M:%S"
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)

    with open("code_log.txt", "a") as f:
        f.write(f"{timestamp} : {message}\n")


# 1.2 extract function (2 points)
def extract(url, table_attribs):
    """Extracts required information from the given website into a DataFrame,

    cleans the Market Cap column, and returns the DataFrame.
    """
    # Fetch web page
    html_page = requests.get(url).text
    data = BeautifulSoup(html_page, "html.parser")

    # Initialize empty DataFrame
    df = pd.DataFrame(columns=table_attribs)

    # TODO: Add your BeautifulSoup extraction logic here
    # 1. Find the target table
    # 2. Loop through rows, extract Bank Name and Market Cap
    # 3. Clean the Market Cap column (remove newlines, commas, convert to float)
    # 4. Append to df

    return df


# 1.3 transform function (2 points)
def transform(df, csv_path):
    """Reads exchange rate data from a CSV, adds transformed Market Cap columns

    for GBP, EUR, and INR, and returns the updated DataFrame.
    """
    # Read the exchange rate CSV
    exchange_rate_df = pd.read_csv(csv_path)

    # Convert dataframe to a dictionary for easy lookup
    # Expected keys in CSV typically look like: 'Currency', 'Rate'
    exchange_rate = exchange_rate_df.set_index("Currency").to_dict()["Rate"]

    # TODO: Calculate new columns based on the exchange rates
    # Example:
    # df['MC_GBP_Billion'] = [round(x * exchange_rate['GBP'], 2) for x in df['MC_USD_Billion']]
    # Do the same for EUR and INR

    return df


# 1.4 load_to_csv function (2 points)
def load_to_csv(df, output_path):
    """Saves the DataFrame to a CSV file at the specified path."""
    df.to_csv(output_path, index=False)


# 1.5 load_to_db function (2 points)
def load_to_db(df, sql_connection, table_name):
    """Saves the DataFrame to a database table with the given name."""
    df.to_sql(table_name, sql_connection, if_exists="replace", index=False)


# 1.6 run_query function (2 points)
def run_query(query_statement, sql_connection):
    """Executes a SQL query on the database, prints the results,

    and logs the execution using log_progress().
    """
    print(f"Executing Query: {query_statement}")

    # Execute and print the query dataframe
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)


# --- Execution Control (The ETL Process) ---
if __name__ == "__main__":
    # Define constants needed for the assignment
    url = "URL_PROVIDED_IN_YOUR_LAB_INSTRUCTIONS"
    table_attribs = ["Name", "MC_USD_Billion"]
    db_name = "Banks.db"
    table_name = "Largest_Banks"
    csv_path = "exchange_rate.csv"
    output_csv_path = "./Largest_Banks_data.csv"

    # Step 1: Logging initialization
    log_progress("Preliminaries complete. Initiating ETL process")

    # Step 2: Extraction
    df = extract(url, table_attribs)
    log_progress("Data extraction complete. Initiating Transformation process")

    # Step 3: Transformation
    df = transform(df, csv_path)
    log_progress(
        "Data transformation complete. Initiating Loading process"
    )  # Required for Question 5

    # Step 4: Load to CSV
    load_to_csv(df, output_csv_path)
    log_progress("Data saved to CSV file")

    # Step 5: Load to Database
    sql_connection = sqlite3.connect(db_name)
    log_progress("SQL Connection initiated")

    load_to_db(df, sql_connection, table_name)
    log_progress("Data loaded to Database as a table")

    # Step 6: Run verification queries (Needed for Question 4)
    query_statement = f"SELECT * FROM {table_name} LIMIT 5"
    run_query(query_statement, sql_connection)
    log_progress("Query execution complete")

    # Close connection
    sql_connection.close()
    log_progress("ETL Process Complete")
