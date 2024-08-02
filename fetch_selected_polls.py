#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import requests
today = pd.Timestamp.today().strftime("%Y-%m-%d")


headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

# Read RCP polling config file to determine which polls to request
# Load the JSON config file
with open("data/polls_config.json", "r") as f:
    polls = json.load(f)



# Processing functions
def clean_numeric(df):
    df["spread_value"] = pd.to_numeric(
        df["spread_value"]
        .str.replace("+", "")
        .str.replace(".0", "")
        .str.strip()
        .fillna("0"),
        errors="coerce",
    ).fillna(0)

    df["marginError"] = pd.to_numeric(
        df["marginError"]
        .str.replace("+", "")
        .str.replace(".0", "")
        .str.strip()
        .fillna("0"),
        errors="coerce",
    ).fillna(0)


# Function to clean dates
def clean_polling_dates(df):
    df["polling_start_date"] = pd.to_datetime(
        df["data_start_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    df["polling_end_date"] = pd.to_datetime(
        df["data_end_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")


def clean_polling_period(df):
    df[["polling_start_date", "polling_end_date"]] = df["date"].str.split(
        " - ", expand=True
    )
    # Convert to datetime and format as %Y-%m-%d
    df["polling_start_date"] = pd.to_datetime(
        df["polling_start_date"] + "/2024"
    ).dt.strftime("%Y-%m-%d")

    df["polling_end_date"] = pd.to_datetime(
        df["polling_end_date"] + "/2024"
    ).dt.strftime("%Y-%m-%d")


# Fetch polls
# Empty dictoinaries to store results
poll_dataframes = {}
poll_dataframes_avg = {}

# Request data for each poll we've selected
for p in polls:

    # Variables we'll need
    url = p["pollingDataUrl"]
    slug = p["slug"]
    name = p["pollName"]

    # Make the request
    response = requests.get(url)
    poll_data = response.json()["poll"]

    # Loop through each poll in the response
    flattened_polls = []

    for individual_poll in poll_data:
        # Extract items from polling jsons
        poll_info = {
            "id": individual_poll.get("id"),
            "type": individual_poll.get("type"),
            "pollster": individual_poll.get("pollster"),
            "date": individual_poll.get("date"),
            "data_start_date": individual_poll.get("data_start_date"),
            "data_end_date": individual_poll.get("data_end_date"),
            "sampleSize": individual_poll.get("sampleSize"),
            "marginError": individual_poll.get("marginError"),
            "link": individual_poll.get("link"),
            "spread_winner": individual_poll.get("spread", {}).get("name"),
            "spread_value": individual_poll.get("spread", {}).get("value"),
        }

        # Extract nested candidate information
        for candidate in individual_poll.get("candidate", []):
            candidate_name = candidate.get("name")
            poll_info[f"{candidate_name.lower().replace(' ', '_')}_value"] = (
                candidate.get("value")
            )

        # One big dataframe with all the polls by subject
        flattened_polls.append(poll_info)
        all_df = pd.DataFrame(flattened_polls).assign(name=name).assign(slug=slug)

        # Clean up numeric values, isolate dfs based on average or independent poll
        clean_numeric(all_df)
        polls_df = all_df.query('type!="rcp_average"').copy()
        avg_df = all_df.query('type=="rcp_average"').copy()

        # Deal with dates
        clean_polling_dates(polls_df)
        clean_polling_period(avg_df)

        # Just the columns we need
        drop_cols = ["data_start_date", "data_end_date"]
        avg_df = avg_df.drop(drop_cols, axis=1)
        polls_df = polls_df.drop(drop_cols, axis=1)

        # Dictionaries of dataframes
        poll_dataframes[slug] = polls_df
        poll_dataframes_avg[slug] = avg_df


# Export json files for each subject's individual polls
for p in poll_dataframes:
    poll_dataframes[f"{p}"].to_json(
        f"data/polls/{p}.json", indent=4, orient="records"
    )


# Create a dictionary to hold all subjects' polls data
polls_data = {}

# Iterate over each DataFrame and convert to JSON-friendly structure
for slug, df in poll_dataframes.items():
    if not df.empty:
        # Convert entire DataFrame to a list of dictionaries
        polls_data[slug] = df.to_dict(orient="records")

# Write the JSON structure to a file
output_file = "data/polls/combined/select_poll_results.json"
with open(output_file, "w") as f:
    json.dump(polls_data, f, indent=4)

print(f"Polls data written to {output_file}")


# Export json files for each subject's average
for p in poll_dataframes_avg:
    poll_dataframes_avg[f"{p}"].to_json(
        f"data/polls_avg/{p}.json", indent=4, orient="records"
    )


# List to hold poll average dictionaries
avg_polls_list = []

# Iterate over each poll and transform DataFrame to dictionary
for slug, df in poll_dataframes_avg.items():
    if not df.empty:
        # Extract the first row as a dictionary
        poll_dict = df.iloc[0].to_dict()
        avg_polls_list.append(poll_dict)

# Write the list of polls to a JSON file
output_file = "data/polls_avg/combined/select_poll_averages.json"
with open(output_file, "w") as f:
    json.dump(avg_polls_list, f, indent=4)

print(f"Polls data written to {output_file}")