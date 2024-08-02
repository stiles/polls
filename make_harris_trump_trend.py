import os
import boto3
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Determine the absolute paths for input and output files
BASE = Path(__file__).resolve().parent
BASE_URL = "https://stilesdata.com/polling/archive/"
JSON_OUT = BASE / "data/harris_trump_trend_data.json"
CSV_OUT = BASE / "data/harris_trump_trend_data.csv"

# Function to list public archive URLs
def list_archive_urls(start_date, end_date):
    current_date = start_date
    urls = []

    while current_date <= end_date:
        url = f"{BASE_URL}harris_trump_avg_{current_date.strftime('%Y-%m-%d')}.json"
        urls.append(url)
        current_date += timedelta(days=1)

    return urls

# Function to read JSON files from URLs and concatenate them into a DataFrame
def read_and_concatenate_json_from_urls(urls):
    data_frames = []

    for url in urls:
        try:
            df = pd.read_json(url)
            data_frames.append(df)
            print(f"Read data from {url}")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to read {url}: {e}")

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data

# Set the date range for files to read
start_date = datetime(2024, 8, 1)  # Replace with the actual start date of your data
end_date = datetime.now()  # Up to today's date

# Get the list of archive URLs
archive_urls = list_archive_urls(start_date, end_date)

# Read and concatenate JSON data
trend_df = read_and_concatenate_json_from_urls(archive_urls)

trend_df.to_csv(CSV_OUT, index=False)
trend_df.to_json(JSON_OUT, indent=4, orient='records')

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("MY_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("MY_AWS_SECRET_ACCESS_KEY"),
)

# Set S3 bucket name
S3_BUCKET = "stilesdata.com"

# Export both dfs to CSV and JSON and upload to S3
# Define S3 keys
s3_csv_key = f"polling/harris_trump_trend_data.csv"
s3_json_key = f"polling/harris_trump_trend_data.json"

# Upload files to S3
s3_client.upload_file(str(CSV_OUT), S3_BUCKET, s3_csv_key)
print(f"CSV file uploaded to s3://{S3_BUCKET}/{s3_csv_key}")

s3_client.upload_file(str(JSON_OUT), S3_BUCKET, s3_json_key)
print(f"JSON file uploaded to s3://{S3_BUCKET}/{s3_json_key}")