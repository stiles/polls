#!/usr/bin/env python
# coding: utf-8

import json
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

hill_url = 'https://elections2024.thehill.com/forecast/2024/president/'
hill_response = requests.get(hill_url, headers=headers)
hill_html = BeautifulSoup(hill_response.text, 'html.parser')
hill_script_tag = hill_html.find('script', id="__NUXT_DATA__")
hill_json = json.loads(hill_script_tag.text)

# Nate

nate_url = f'https://static.dwcdn.net/data/Vu4Pa.csv?v={epoch_seconds}'
nate_src = pd.read_csv(nate_url, storage_options=headers).drop('RFK', axis=1)
nate_src['source'] = 'Nate Silver'
nate_src['date'] = pd.to_datetime(nate_src['modeldate'], format='mixed').dt.strftime('%Y-%m-%d')
nate_src.columns = nate_src.columns.str.lower()
nate_latest = nate_src.query('date == date.max()')

print(nate_latest)


df = pd.concat([nate_latest]).reset_index(drop=True)
