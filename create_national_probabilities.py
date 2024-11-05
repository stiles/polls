#!/usr/bin/env python
# coding: utf-8

import json
import requests
import pandas as pd
import pytz
from io import StringIO
from datetime import datetime
from bs4 import BeautifulSoup

# Define today's date
eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)

today = now.strftime('%Y-%m-%d')

# Convert current time to epoch seconds
epoch_seconds = int(now.timestamp() * 1000)  # Convert to milliseconds

# Headers for requests
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

ARCHIVE_URL = 'data/probability/probability_by_outlet_archive.json'
ARCHIVE_OUTPUT = 'data/probability/probability_by_outlet_archive.json'

# The Hill
# It's data file is tricky so grabbing prediction from the page

hill_url = 'https://elections2024.thehill.com/forecast/2024/president/'
hill_response = requests.get(hill_url, headers=headers)
hill_html = BeautifulSoup(hill_response.text, 'html.parser')

prediction_date = hill_html.find('p', class_='italic text-neutral text-sm mt-2').text.replace('Last Updated: ', '')
prediction_text = hill_html.find('p', class_='text-lg')
prediction_ahead = prediction_text.find('span').text.replace('Kamala ', '').replace('Donald ', '')
prediction_ahead_value = int(prediction_text.find('span', class_="px-2").text.replace('%', ''))
prediction_date_formatted = prediction_date.split(',')[1].split(' at')[0] + ', 2024'

if prediction_ahead == 'Harris':
    harris_value = prediction_ahead_value
    trump_value = 100 - prediction_ahead_value
else:
    trump_value = prediction_ahead_value
    harris_value = 100 - prediction_ahead_value

hill_prediction = [{
    'date': prediction_date_formatted,
    'source':'The Hill',
    'harris': harris_value,
    'trump': trump_value,
}]

hill_latest = pd.DataFrame(hill_prediction)

hill_latest['date'] = pd.to_datetime(hill_latest['date'])

# Nate Silver
# Pulling the latest CSV from his Datawrapper chart for win probability

nate_url = f'https://static.dwcdn.net/data/U7Nxm.csv?v={epoch_seconds}'
nate_src = pd.read_csv(nate_url, storage_options=headers)
nate_src['source'] = 'Nate Silver'
nate_latest = nate_src.pivot(index='source', values='ec_win', columns='Candidate').reset_index().drop('nonmag', axis=1)
nate_latest.columns = nate_latest.columns.str.lower()
nate_latest['date'] = today

# FiveThirtyEight
# The data feed is confusing so just pulling from the page

fte_page_response = requests.get('https://projects.fivethirtyeight.com/2024-election-forecast', headers=headers)
fte_html = BeautifulSoup(fte_page_response.text, 'html.parser')

harris = fte_html.find('div', class_="dem")
harris_value = harris.find('span', class_='odds').text

trump = fte_html.find('div', class_="rep")
trump_value = trump.find('span', class_='odds').text

fte_latest = pd.DataFrame(
    [{
    'date': today,
    'source': 'FiveThirtyEight',
    'harris': harris_value,
    'trump': trump_value,
}]
)

fte_latest['harris'] = fte_latest['harris'].astype(int)
fte_latest['trump'] = fte_latest['trump'].astype(int)

# Economist
# Snag CSV that feed its electoral college forecast

econ_url = 'https://cdn.economistdatateam.com/2024-us-tracker/forecast/president/main/national_ec_popvote_topline.csv?nocache=1726416620976'
econ_response = requests.get(econ_url, headers=headers)
econ_src = pd.read_csv(StringIO(econ_response.text))
econ_latest = econ_src[['date', 'dem_win_prob', 'rep_win_prob']].rename(columns={'dem_win_prob':'harris','rep_win_prob':'trump'})
econ_latest['harris'] = (econ_latest['harris'] * 100).round(2).astype(int)
econ_latest['trump'] = (econ_latest['trump'] * 100).round(2).astype(int)
econ_latest['source'] = 'Economist'



# Combine the dataframes

df = pd.concat([nate_latest, fte_latest, econ_latest.round(), hill_latest]).reset_index(drop=True)

# Function to determine the winner
def determine_winner(row):
    if row['harris'] > row['trump']:
        return 'Harris'
    elif row['trump'] > row['harris']:
        return 'Trump'
    else:
        return 'Tie'  # In case of a tie
    
def winner_value(row):
    if row['ahead'] == 'Harris':
        return row['harris']
    elif row['ahead'] == 'Trump':
        return row['trump']
    else:
        return '0'  # In case of a tie

# Apply the function to create the 'winning' column
df['ahead'] = df.apply(determine_winner, axis=1)
df['ahead_value'] = df.apply(winner_value, axis=1).round(1)

# Export

df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
df['fetched'] = today

cols = ['source', 'harris', 'trump', 'date', 'fetched']

# Create/export JSON latest
df[cols].to_json('data/probability/probability_by_outlet_latest.json', indent=4, orient='records')

# Add latest to timeseries archive
archive_df = pd.read_json(ARCHIVE_URL, dtype={'date': 'str'})

# Concatenate them and save a new archive
combined_df = pd.concat([df, archive_df]).reset_index(drop=True).drop_duplicates(subset=['fetched', 'source'], keep='first')
combined_df.to_json(ARCHIVE_OUTPUT, indent=4, orient='records')