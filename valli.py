import pandas as pd
from bs4 import BeautifulSoup
import requests

LOG_FILE = "code_log.txt"

def log_progress(message):
    """Append progress messages to the log file."""
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")


def extract(url):
    """Extract the 'By market capitalization' table into a DataFrame."""
    log_progress("Starting data extraction")

    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    # Locate the table containing 'By market capitalization'
    tables = soup.find_all("table")

    # Adjust selection logic based on the page structure
    df = pd.read_html(str(tables[0]))[0]

    log_progress("Data extraction completed")
    return df


def transform(df, exchange_rates):
    """
    Add Market Capitalization columns in GBP, EUR, and INR.
    exchange_rates is a dictionary such as:
    {'GBP': 0.79, 'EUR': 0.92, 'INR': 83.12}
    """
    log_progress("Starting transformation")

    df["MC_GBP_Billion"] = (df["Market Cap (US$ Billion)"] *
                            exchange_rates["GBP"]).round(2)

    df["MC_EUR_Billion"] = (df["Market Cap (US$ Billion)"] *
                            exchange_rates["EUR"]).round(2)

    df["MC_INR_Billion"] = (df["Market Cap (US$ Billion)"] *
                            exchange_rates["INR"]).round(2)

    log_progress("Transformation completed")
    return df
