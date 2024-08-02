import requests
import pandas as pd

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

url = 'https://www.realclearpolitics.com/poll/race/7386/polling_data.json'

response = requests.get(url, headers=headers)

poll_data = response.json()['poll']

src = pd.DataFrame(poll_data)

print(src.iloc[1])