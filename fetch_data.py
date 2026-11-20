from pathlib import Path

import pandas as pd
import requests

# Settings for the COVID-19 by country API
URL = "https://disease.sh/v3/covid-19/countries"
PARAMS = {}
RECORDS_KEY = None  # The API reply is already a list

RENAME = {}
KEEP = [
    "country",
    "continent",
    "cases",
    "deaths",
    "recovered",
    "tests",
    "population",
    "active",
]
MUST_HAVE = ["cases", "continent"]

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


def get_data(url, params):
    """Ask the API for data. Return None if the request fails."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Turn the API's list of records into a pandas table."""
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    """Keep the chosen columns and remove rows missing required values."""
    df = df.rename(columns=RENAME)
    df = df[KEEP]
    return df.dropna(subset=MUST_HAVE)


def save_data(df, path):
    """Create the DATA folder if needed, then save the table as a CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    data = get_data(URL, PARAMS)

    if data is not None:
        table = make_table(data, RECORDS_KEY)
        tidy = tidy_data(table)
        print(tidy.head())
        save_data(tidy, RAW_FILE)