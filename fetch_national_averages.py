#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import pytz
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

# Fetch national poll averages from various sources

# Cook Political Report
cook_url = f'https://static.dwcdn.net/data/KTtuN.csv?v={epoch_seconds}'
cook_src = pd.read_csv(cook_url, storage_options=headers, parse_dates=['Date/Time'])
cook_src = cook_src[['Date/Time', 'Harris Trend', 'Trump2 Trend']].dropna().rename(columns={'Date/Time': 'date', 'Harris Trend': 'harris', 'Trump2 Trend': 'trump'}).reset_index(drop=True).round(1)
cook_src['date'] = pd.to_datetime(cook_src['date']).dt.strftime('%Y-%m-%d')
cook_src['source'] = 'Cook Report'
cook_src['notes'] = ''
cook_latest = cook_src.query('date == date.max()').head(1)

# RCP
rcp_src = pd.read_csv('https://stilesdata.com/polling/harris_trump/polls_avg/_trend/harris_trump_trend.csv')[['fetch_date', 'harris_value', 'trump_value']].rename(columns={'trump_value': 'trump', 'harris_value': 'harris', 'fetch_date': 'date'})
rcp_src['source'] = "RealClearPolitics"
rcp_src['notes'] = ''
rcp_latest = rcp_src.query('date == date.max()')

# FiveThirtyEight
fte_src = pd.read_json('https://projects.fivethirtyeight.com/polls/president-general/2024/national/polling-average.json').pivot(columns='candidate', values='pct_estimate', index='date').reset_index().rename(columns={'Trump': 'trump', 'Harris': 'harris', 'Kennedy': 'kennedy'}).round(1)
fte_src['source'] = 'FiveThirtyEight'
fte_src['date'] = pd.to_datetime(fte_src['date']).dt.strftime('%Y-%m-%d')
fte_src['notes'] = 'w/Kennedy'
fte_latest = fte_src.query('date == date.max()').drop('kennedy', axis=1)

# Nate Silver
nate_cols = ['modeldate','state', 'trump','harris', 'rfk']
nate_url = f'https://static.dwcdn.net/data/wB0Zh.csv?v={epoch_seconds}'
nate_src = pd.read_csv(nate_url, storage_options=headers).query('state=="National"').dropna(subset='harris')[nate_cols].rename(columns={'modeldate': 'date', 'rfk': 'kennedy'}).round(1)
nate_src['source'] = 'Nate Silver'
nate_src['date'] = pd.to_datetime(nate_src['date'], format='mixed').dt.strftime('%Y-%m-%d')
nate_latest = nate_src.query('date == date.max()').drop('kennedy', axis=1)

# 270toWin
data_dict = requests.get('https://www.270towin.com/polls/php/get-polls-by-state.php?election_year=2024&candidate_name_dem=Harris&candidate_name_rep=Trump&sort_by=date').json()['results']
src_270_cols = ['poll_date_timestamp', 'poll_dem_avg', 'poll_rep_avg']
src_270 = pd.DataFrame.from_dict(data_dict, orient='index')[src_270_cols].rename(columns={'index': 'state', 'poll_date_timestamp':'date', 'poll_dem_avg': 'harris', 'poll_rep_avg':'trump'}).reset_index()
src_270['date'] = pd.to_datetime(src_270['date'], unit='s').dt.strftime('%Y-%m-%d')
src_270['notes'] = ''
src_270['source'] = '270toWin'
latest_270 = src_270.query('index=="0"').drop('index', axis=1).copy()

# Economist
econ_src = pd.read_csv('https://cdn.economistdatateam.com/2024-us-tracker/harris/data/polls/polltracker-latest-trend.csv', storage_options=headers).pivot(columns='candidate_name', index='date', values='pct').reset_index().rename(columns={'Donald Trump': 'trump', 'Kamala Harris': 'harris'}).round(1)
econ_src['source'] = "Economist"
econ_src['notes'] = ""

# NYT
nyt_page_content = requests.get('https://www.nytimes.com/interactive/2024/us/elections/polls-president.html', headers=headers)
nyt_soup = BeautifulSoup(nyt_page_content.text, 'html.parser')
divs = nyt_soup.find_all('span', class_='g-endlabel-inner')[:2]
nyt_data = {}
for div in divs:
    label = div.find('span', class_='g-label-fill').text.strip()
    percentage = div.find('span', class_='g-value').text.strip('%')

    if 'Trump' in label:
        nyt_data['trump'] = float(percentage)
    elif 'Harris' in label:
        nyt_data['harris'] = float(percentage)
nyt_data['date'] = today
nyt_df = pd.DataFrame([nyt_data])
nyt_df['source'] = 'New York Times'
nyt_df['notes'] = ''

# Combine all sources
df = pd.concat([cook_latest, rcp_latest, fte_latest, nate_latest, latest_270, econ_src, nyt_df]).reset_index(drop=True)

# Apply the function to create the 'winning' and 'winning_margin' columns
df['winning'] = df.apply(determine_winner, axis=1)
df['winning_margin'] = df['winning'].str.extract(r'([+-]?\d+\.?\d*)').astype(float)

# Save to JSON files with the required columns
df_slim = df.drop(['state', 'notes'], axis=1)  # Keep 'winning' and 'winning_margin' columns
df_slim['fetched_date'] = today
df_slim.to_json('data/polls_avg/avgs/averages_latest.json', indent=4, orient='records')

# Create/export JSON avg archive
archive = pd.read_json('https://stilesdata.com/polling/harris_trump/polls_avg/avgs/averages_trend.json')
archive['date'] = pd.to_datetime(archive['date']).dt.strftime('%Y-%m-%d')
combined = pd.concat([df_slim, archive]).drop_duplicates(subset=['fetched_date', 'source'], keep='first').reset_index(drop=True)
combined.to_json('data/polls_avg/avgs/averages_trend.json', indent=4, orient='records')