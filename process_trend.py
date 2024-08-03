import pandas as pd
from pathlib import Path
from datetime import datetime

# Determine the absolute paths for input and output files
BASE = Path(__file__).resolve().parent
TREND_DAILY_DIR = BASE / "data/polls_avg/_trend/daily/"
JSON_OUT = BASE / "data/polls_avg/_trend/harris_trump_trend.json"
CSV_OUT = BASE / "data/polls_avg/_trend/harris_trump_trend.csv"

# Function to read JSON files from a local directory and concatenate them into a DataFrame
def read_and_concatenate_json_from_local(directory):
    data_frames = []

    for file_path in directory.glob("*.json"):  # Read all JSON files in the directory
        try:
            df = pd.read_json(file_path)
            data_frames.append(df)
            print(f"Read data from {file_path}")
        except ValueError as e:
            print(f"Failed to read {file_path}: {e}")

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True).drop(
            ['polling_period', 'polling_start_date', 'polling_end_date'], axis=1, errors='ignore'
        ).round(2).sort_values('fetch_date')
        return combined_df
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data

# Read and concatenate JSON data from the local daily directory
trend_df = read_and_concatenate_json_from_local(TREND_DAILY_DIR)

# Save the concatenated DataFrame to CSV and JSON
trend_df.to_csv(CSV_OUT, index=False)
trend_df.to_json(JSON_OUT, indent=4, orient='records')

print(f"Trend data saved to {CSV_OUT} and {JSON_OUT}")