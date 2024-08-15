#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import pytz
from datetime import datetime

# Define today's date in Eastern time
eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)

today = now.strftime('%Y-%m-%d')

# Function to find winner and format margin column
def determine_winner(row):
    """Determine the winner and margin between Harris and Trump."""
    if row['harris'] > row['trump']:
        winner = "D"
        margin = row['harris'] - row['trump']
    elif row['harris'] < row['trump']:
        winner = "R"
        margin = row['trump'] - row['harris']
    else:
        winner = "T"
        margin = 0
    return f"{winner} +{margin:.1f}"

# Which states are we interested in 
states = ['Pennsylvania', 'Michigan', 'Wisconsin', 'Georgia', 'Nevada', 'Arizona']
abbreviations = ['PA', 'MI', 'WI', 'GA', 'NV', 'AZ']

base_url = 'https://projects.fivethirtyeight.com/polls/president-general/2024/{}/polling-average.json'
dfs = []

# Loop through states list, reading into a list of dataframes
for state in states:
    url = base_url.format(state.replace(' ', '-').lower())
    src = pd.read_json(url)
    src['state'] = state
    src['source_url'] = url
    dfs.append(src)

# Most recent averages for each state
states_all_df = pd.concat(dfs)
states_df = pd.concat(dfs).query('date == date.max()')

# Pivot to a wide format
states_df_pivot = states_all_df.pivot(index=['state', 'date', 'source_url'], columns='candidate', values='pct_estimate').reset_index().round(1)
states_df_pivot.columns = states_df_pivot.columns.str.lower()
states_fte = states_df_pivot.drop('kennedy', axis=1)

# Apply winner function
states_fte['winning'] = states_fte.apply(determine_winner, axis=1)
states_fte['winning_margin'] = states_fte['winning'].str.extract(r'([+-]?\d+\.?\d*)').astype(float)

# Create the dictionary for full state names to abbreviations
state_to_abbreviation = {state: abbr for state, abbr in zip(states, abbreviations)}

# Now you can use this dictionary to map the full state names in your dataframe
states_fte['state_abbr'] = states_fte['state'].map(state_to_abbreviation)

# Add meta
states_fte['source'] = 'FiveThirtyEight'

states_fte['date'] = pd.to_datetime(states_fte['date']).dt.strftime('%Y-%m-%d')
states_fte_recent = states_fte.query('date == date.max()')

# Save to JSON files
states_fte.to_json('data/polls_avg/avgs/state_averages_trend.json', indent=4, orient='records')
states_fte_recent.to_json('data/polls_avg/avgs/state_averages_latest.json', indent=4, orient='records')