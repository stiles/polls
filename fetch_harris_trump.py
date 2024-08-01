#!/usr/bin/env python
# coding: utf-8

# RealClearPolitics Harris-Trump polls

import os
import json
import boto3
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Date format for naming files
today = datetime.today().strftime("%Y-%m-%d")

# Headers for requests
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Function to clean point spread between Trump/Harris
def clean_spread(df):
    df["spread_value"] = pd.to_numeric(
        df["spread_value"]
        .str.replace("+", "")
        .str.replace(".0", "")
        .str.strip()
        .fillna("0"),
        errors='coerce'
    ).fillna(0)

# Function to clean dates
def clean_dates(df):
    df["polling_start_date"] = pd.to_datetime(df["polling_start_date"], errors='coerce').dt.strftime("%Y-%m-%d")
    df["polling_end_date"] = pd.to_datetime(df["polling_end_date"], errors='coerce').dt.strftime("%Y-%m-%d")

# Function to fetch poll data
def fetch_poll_data():
    params = [
        {
            "type": "Poll",
            "name": "2024 General Election: Trump vs Harris",
            "slug": "trump-vs-harris",
            "fullPath": "president/general/2024",
            "pollingType": "Poll",
            "pollingDataUrl": "https://www.realclearpolitics.com/poll/race/7386/polling_data.json",
            "category": {"name": "General"},
        }
    ]
    params_json = json.dumps({"landingPolls": params})

    try:
        # Fetch poll data from RCP
        response = requests.post(
            "https://www.realclearpolling.com/api/polls-feed",
            headers=headers,
            data=params_json,  # Pass the data as raw text
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # There's only one poll, so we want the first list item
    return response.json()[0]

# Function to process poll data
def process_poll_data(polls_json):
    # Select just the poll key with results, excluding chart properties, meta, etc., in the json
    poll = polls_json["poll"]

    # Empty list to store the data
    flattened_data = []

    # Extract items from each poll into its own dictionary
    for individual_poll in poll:
        poll_info = {
            "id": individual_poll.get("id"),
            "type": individual_poll.get("type"),
            "pollster": individual_poll.get("pollster"),
            "polling_period": individual_poll.get("date"),
            "polling_start_date": individual_poll.get("data_start_date"),  # Corrected key
            "polling_end_date": individual_poll.get("data_end_date"),  # Corrected key
            "sampleSize": individual_poll.get("sampleSize"),
            "marginError": individual_poll.get("marginError"),
            "link": individual_poll.get("link"),
            "spread_winner": individual_poll.get("spread", {}).get("name"),
            "spread_value": individual_poll.get("spread", {}).get("value"),
        }
        # Extract nested candidate information from each poll
        for candidate in individual_poll.get("candidate", []):
            candidate_name = candidate.get("name")
            poll_info[f"{candidate_name.lower().replace(' ', '_')}_value"] = candidate.get(
                "value"
            )
        # Store the dictionaries from each poll into a list
        flattened_data.append(poll_info)

    return flattened_data

# Function to export data to S3
def export_data_to_s3(dataframes):
    # Initialize S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("MY_AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("MY_AWS_SECRET_ACCESS_KEY"),
    )

    # Set S3 bucket name
    S3_BUCKET = "stilesdata.com"

    # Export both dfs to CSV and JSON and upload to S3
    for name, df in dataframes.items():
        csv_out = BASE / f"data/{name}.csv"
        json_out = BASE / f"data/{name}.json"

        # Save locally
        df.to_csv(csv_out, index=False)
        df.to_json(json_out, indent=4, orient="records")

        # Define S3 keys
        s3_csv_key = f"polling/{name}.csv"
        s3_json_key = f"polling/{name}.json"

        # For harris_trump_avg, also save to archive
        if name == "harris_trump_avg":
            s3_csv_key_archive = f"polling/archive/{name}_{today}.csv"
            s3_client.upload_file(str(csv_out), S3_BUCKET, s3_csv_key_archive)
            print(f"CSV archive uploaded to s3://{S3_BUCKET}/{s3_csv_key_archive}")

        # Upload files to S3
        s3_client.upload_file(str(csv_out), S3_BUCKET, s3_csv_key)
        print(f"CSV file uploaded to s3://{S3_BUCKET}/{s3_csv_key}")

        s3_client.upload_file(str(json_out), S3_BUCKET, s3_json_key)
        print(f"JSON file uploaded to s3://{S3_BUCKET}/{s3_json_key}")

def main():
    polls_json = fetch_poll_data()
    if not polls_json:
        return

    flattened_data = process_poll_data(polls_json)

    # Create a dataframe for just the poll average from the list
    harris_trump_avg = (
        pd.DataFrame(flattened_data).query('type=="rcp_average"').assign(fetch_date=today)
    ).drop(
        [
            "sampleSize",
            "marginError",
            "pollster",
            "link",
        ],
        axis=1,
    )

    # Process dates for Harris-Trump average by splitting "polling_period"
    if 'polling_period' in harris_trump_avg.columns:
        harris_trump_avg[['polling_start_date', 'polling_end_date']] = harris_trump_avg[
            "polling_period"
        ].str.split(" - ", expand=True)

    # Convert to datetime and format as %Y-%m-%d
    harris_trump_avg['polling_start_date'] = pd.to_datetime(
        harris_trump_avg['polling_start_date'] + "/2024", errors='coerce'
    ).dt.strftime("%Y-%m-%d")

    harris_trump_avg['polling_end_date'] = pd.to_datetime(
        harris_trump_avg['polling_end_date'] + "/2024", errors='coerce'
    ).dt.strftime("%Y-%m-%d")

    # Create a dataframe for just the individual polls from the list, excluding averages
    harris_trump_polls = (
        pd.DataFrame(flattened_data)
        .query('type!="poll_rcp_avg" and type!="rcp_average"')
        .drop(["polling_period", "type"], axis=1)
    )

    # Apply cleaning functions only to the individual polls dataframe
    clean_spread(harris_trump_polls)
    clean_dates(harris_trump_polls)

    # Dictionary mapping names to dfs
    dataframes = {
        "harris_trump_polls": harris_trump_polls,
        "harris_trump_avg": harris_trump_avg,
    }

    export_data_to_s3(dataframes)

if __name__ == "__main__":
    # Determine the absolute paths for input and output files
    BASE = Path(__file__).resolve().parent
    main()
