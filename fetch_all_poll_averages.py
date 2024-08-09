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

last_updated = now.isoformat()
last_updated_str = (
    now.strftime("%-I %p ET, %B %-d").replace("AM", "a.m.").replace("PM", "p.m.")
)
today = (
    now.strftime('%Y-%m-%d')
)

# Convert current time to epoch seconds
epoch_seconds = int(now.timestamp() * 1000)  # Convert to milliseconds

# Headers for requests
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

# Function to determine the winner and margin with color styling
def determine_winner(row):
    """Determine the winner and margin between Harris and Trump with color."""
    if row['harris'] > row['trump']:
        winner = "Harris"
        margin = row['harris'] - row['trump']
    else:
        winner = "Trump"
        margin = row['trump'] - row['harris']
    return f"{winner}: +{margin:.1f}"

def format_sources(sources):
    """Format the list of sources for the summary message."""
    sorted_sources = sorted(sources)
    if not sorted_sources:
        return ""
    elif len(sorted_sources) == 1:
        return f"`{sorted_sources[0]}`"
    return ", ".join(f"`{source}`" for source in sorted_sources[:-1]) + " and " + f"`{sorted_sources[-1]}`"

# Fetch and prepare the data

# Cook Political Report
# Cook url w/ epoch
cook_url = f'https://static.dwcdn.net/data/KTtuN.csv?v={epoch_seconds}'

cook_src = pd.read_csv(cook_url, storage_options=headers, parse_dates=['Date/Time'])
cook_src = cook_src[['Date/Time', 'Harris Trend', 'Trump2 Trend']].dropna().rename(columns={'Date/Time': 'date', 'Harris Trend': 'harris', 'Trump2 Trend': 'trump'}).reset_index(drop=True).round(1)
cook_src['date'] = pd.to_datetime(cook_src['date']).dt.strftime('%Y-%m-%d')
cook_src['source'] = 'Cook Political Report'
cook_src['notes'] = ''
cook_latest = cook_src.query('date == date.max()').head(1)

# RCP
rcp_src = pd.read_csv('https://stilesdata.com/polling/harris_trump/polls_avg/_trend/harris_trump_trend.csv')[['fetch_date', 'harris_value', 'trump_value']].rename(columns={'trump_value': 'trump', 'harris_value': 'harris', 'fetch_date': 'date'})

rcp_src['source'] = "Real Clear Politics"
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

# Format the Silver Bulletin URL with the epoch seconds
nate_url = f'https://static.dwcdn.net/data/wB0Zh.csv?v={epoch_seconds}'

nate_src = pd.read_csv(nate_url, storage_options=headers).query('state=="National"').dropna(subset='harris')[nate_cols].rename(columns={'modeldate': 'date', 'rfk': 'kennedy'}).round(1)

nate_src['source'] = 'Silver Bulletin'
nate_src['date'] = pd.to_datetime(nate_src['date'], format='mixed').dt.strftime('%Y-%m-%d')

nate_latest = nate_src.query('date == date.max()').drop('kennedy', axis=1)

# 270toWin
data_dict = requests.get('https://www.270towin.com/polls/php/get-polls-by-state.php?election_year=2024&candidate_name_dem=Harris&candidate_name_rep=Trump&sort_by=date').json()['results']

src_270_cols = ['poll_date_timestamp', 'poll_dem_avg', 'poll_rep_avg']

# Create a DataFrame from the dictionary
src_270 = pd.DataFrame.from_dict(data_dict, orient='index')[src_270_cols].rename(columns={'index': 'state', 'poll_date_timestamp':'date', 'poll_dem_avg': 'harris', 'poll_rep_avg':'trump'}).reset_index()

src_270['date'] = pd.to_datetime(src_270['date'], unit='s').dt.strftime('%Y-%m-%d')

src_270['notes'] = ''
src_270['source'] = '270toWin'

src_270df = src_270.query('index=="0"').drop('index', axis=1).copy()

latest_270 = src_270df.query('date == date.max()').round(1)

# Economist
econ_src = pd.read_csv('https://cdn.economistdatateam.com/2024-us-tracker/harris/data/polls/polltracker-latest-trend.csv', storage_options=headers).pivot(columns='candidate_name', index='date', values='pct').reset_index().rename(columns={'Donald Trump': 'trump', 'Kamala Harris': 'harris'}).round(1)

econ_src['source'] = "Economist"
econ_src['notes'] = ""


# NYT
nyt_page_content = requests.get('https://www.nytimes.com/interactive/2024/us/elections/polls-president.html', headers=headers)
nyt_soup = BeautifulSoup(nyt_page_content.text, 'html.parser')

# Find the relevant divs
divs = nyt_soup.find_all('div', class_='g-label-large')[:2]

# Parsing the data
nyt_data = {}
for div in divs:
    label = div.find('span', class_='g-label-fill').text.strip()
    percentage = div.find('strong').text.strip('%')
    
    if 'Trump' in label:
        nyt_data['trump'] = float(percentage)
    elif 'Harris' in label:
        nyt_data['harris'] = float(percentage)

# Adding date to the dictionary
nyt_data['date'] = today

# Creating a DataFrame
nyt_df = pd.DataFrame([nyt_data])
nyt_df['source'] = 'The New York Times'
nyt_df['notes'] = ''

# All sources
cols = ['date', 'source', 'harris', 'trump']

df = pd.concat([cook_latest, rcp_latest, fte_latest, nate_latest, latest_270, econ_src, nyt_df]).reset_index(drop=True)

# Apply the function to create the 'winning' column
df['margin'] = df.apply(determine_winner, axis=1)

harris_avg = df['harris'].mean().round(2).astype(float)
trump_avg = df['trump'].mean().round(2).astype(float)

if harris_avg > trump_avg:
    avg_winning = "Vice President Kamala Harris"
    avg_losing = "former President Donald Trump"
    avg_margin = round(harris_avg - trump_avg, 1)
    avg_winning_value = harris_avg
    avg_losing_value = trump_avg
else:
    avg_winning = "Former President Donald Trump"
    avg_losing = "Vice President Kamala Harris"
    avg_margin = round(trump_avg - harris_avg, 1)
    avg_winning_value = trump_avg
    avg_losing_value = harris_avg

# Example list of sources
sources = list(df['source'].unique())

# Format the sources list
formatted_sources = format_sources(sources)

fetched = pd.Timestamp.today().strftime("%B %-d, %Y at %-I %p PT").replace("AM", "a.m.").replace("PM", "p.m.")

msg = f'**{avg_winning}** is leading in the national polls to {avg_losing} by a margin of **{avg_margin}** percentage points, according an average of seven prominent polling averages.'

# Links for each polling source
source_links = {
    "Cook Political Report": "https://www.cookpolitical.com/survey-research/cpr-national-polling-average/2024/harris-trump-overall",
    "FiveThirtyEight": "https://projects.fivethirtyeight.com/polls/president-general/2024/national/",
    "Real Clear Politics": "https://www.realclearpolling.com/polls/president/general/2024/trump-vs-harris",
    "Silver Bulletin": "https://www.natesilver.net/p/nate-silver-2024-president-election-polls-model",
    "270toWin": "https://www.270towin.com/2024-presidential-election-polls/",
    "Economist": "https://www.economist.com/interactive/us-2024-election/trump-harris-polls",
    "The New York Times": "https://www.nytimes.com/interactive/2024/us/elections/polls-president.html"
}

# Generate Markdown Content with inline CSS for better mobile responsiveness
markdown_content = f"""
<style>

table {{
    width: 100%;
    border-collapse: collapse;
}}
table, th, td {{
    border: 0px solid black;
}}
a {{
    color: inherit;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: .2em;
    text-decoration-color: #0003;
    transition: text-decoration-color .3s ease-out; 
}}
a:visited {{
    color: inherit;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: .2em;
    text-decoration-color: #0003;
    transition: text-decoration-color .3s ease-out; 
}}
th, td {{
    padding: 8px;
    text-align: left;
}}
.markdown-body>*:last-child {{
    display: none;
}}
@media (max-width: 600px) {{
    th, td {{
        font-size: 12px;  /* Smaller font size on small screens */
    }}
}}
</style>

## Harris v. Trump: The latest
{msg}

## Sources: All the poll averages

| Source               | Harris (%) | Trump (%) | Margin      |
|----------------------|------------|-----------|-------------|
"""

# Append each row of the DataFrame to the markdown table with links
for index, row in df.iterrows():
    source_name = row['source']
    source_link = source_links.get(source_name, "#")
    margin_style = f"<span style='color: {'#5194C3' if 'Harris' in row['margin'] else '#c52622'}; font-weight: bold;'>{row['margin']}</span>"
    
    # Style the Harris and Trump percentage with respective colors
    harris_style = f"<span style='color: #5194C3; font-weight: bold;'>{row['harris']}</span>"
    trump_style = f"<span style='color: #c52622; font-weight: bold;'>{row['trump']}</span>"
    
    markdown_content += f"| [{source_name}]({source_link}) | {harris_style} | {trump_style} | {margin_style} |\n"

# Add additional content after the table
markdown_content += f'\n\n**More:** Read [about this data](https://github.com/stiles/polls). Download [the latest averages](https://stilesdata.com/polling/harris_trump/polls_avg/avgs/averages_trend.json). \n\n *Last hourly update: {last_updated_str}*'

# Write markdown to file
with open("index.md", "w") as f:
    f.write(markdown_content)

# Clean up averages dataframe
df['winning'] = df['margin'].str.split(': +', expand=True)[0]
df['winning_margin'] = df['margin'].str.split('+', expand=True)[1].astype(float)
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

# Prepare for JSON export
df_slim = df.drop(['state', 'notes', 'margin'], axis=1)
df_slim['fetched_date'] = today
df_slim.to_json('data/polls_avg/avgs/averages_latest.json', indent=4, orient='records')

# Create/export JSON avg archive
archive = pd.read_json('https://stilesdata.com/polling/harris_trump/polls_avg/avgs/averages_trend.json')
archive['date'] = pd.to_datetime(archive['date']).dt.strftime('%Y-%m-%d')
combined = pd.concat([df_slim, archive]).drop_duplicates(subset=['fetched_date', 'source'], keep='first').reset_index(drop=True)
combined.to_json('data/polls_avg/avgs/averages_trend.json', indent=4, orient='records')