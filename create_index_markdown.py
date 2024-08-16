#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import pytz
from datetime import datetime

# Define today's date
eastern = pytz.timezone("US/Eastern")
now = datetime.now(eastern)

last_updated_str = (
    now.strftime("%-I %p ET, %B %-d").replace("AM", "a.m.").replace("PM", "p.m.")
)

# Load JSON data from previous scripts
states_fte = pd.read_json('data/polls_avg/avgs/state_averages_latest.json')
df = pd.read_json('data/polls_avg/avgs/averages_latest.json')

# Calculate averages
harris_avg = df['harris'].mean().round(2).astype(float)
trump_avg = df['trump'].mean().round(2).astype(float)

if harris_avg > trump_avg:
    avg_winning = "Vice President Kamala Harris"
    avg_losing = "former President Donald Trump"
    avg_margin = round(harris_avg - trump_avg, 1)
    avg_winning_color = '#5194C3'
else:
    avg_winning = "Former President Donald Trump"
    avg_losing = "Vice President Kamala Harris"
    avg_margin = round(trump_avg - harris_avg, 1)
    avg_winning_color = '#c52622'

number_map = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six"
}

# Calculate the number of states where each candidate is leading
harris_leads = states_fte['winning'].str.startswith('D').sum()
trump_leads = states_fte['winning'].str.startswith('R').sum()
ties = len(states_fte) - (harris_leads + trump_leads)

if harris_leads > trump_leads:
    state_msg = f"<span style='background: #5194C3; padding:1px 4px; color: #ffffff; font-weight: bold;'>{avg_winning}</span> is leading in <span style='background: #5194C3; padding:1px 4px; color: #ffffff; font-weight: bold;'>{number_map[harris_leads]}</span> of the six key swing states over {avg_losing}, according to FiveThirtyEight's averages."
elif trump_leads > harris_leads:
    state_msg = f"<span style='background: #c52622; padding:1px 4px; color: #ffffff; font-weight: bold;'>{avg_losing}</span> is leading in <span style='background: #c52622; padding:1px 4px; color: #ffffff; font-weight: bold;'>{number_map[trump_leads]}</span> of the six key swing states over {avg_winning}, according to FiveThirtyEight's averages."
else:
    state_msg = f"The state of the race is mixed, with **{avg_winning}** ahead in **{number_map[harris_leads]}** states, **{avg_losing}** ahead in **{number_map[trump_leads]}** states, and the candidates tied in **{ties}** states."

# Format sources
def format_sources(sources):
    sorted_sources = sorted(sources)
    if not sorted_sources:
        return ""
    elif len(sorted_sources) == 1:
        return f"`{sorted_sources[0]}`"
    return ", ".join(f"`{source}`" for source in sorted_sources[:-1]) + " and " + f"`{sorted_sources[-1]}`"

sources = list(df['source'].unique())
formatted_sources = format_sources(sources)

msg = f"<span style='background: {avg_winning_color}; padding:1px 4px; color: #ffffff; font-weight: bold;'>{avg_winning}</span> is leading in the national polls by a <span style='background: {avg_winning_color}; padding:1px 4px; color: #ffffff; font-weight: bold;'>{avg_margin} percentage point</span> margin over {avg_losing}, according an average of prominent polling averages."

# Links for each polling source
source_links = {
    "Cook Report": "https://www.cookpolitical.com/survey-research/cpr-national-polling-average/2024/harris-trump-overall",
    "FiveThirtyEight": "https://projects.fivethirtyeight.com/polls/president-general/2024/national/",
    "RealClearPolitics": "https://www.realclearpolling.com/polls/president/general/2024/trump-vs-harris",
    "Nate Silver": "https://www.natesilver.net/p/nate-silver-2024-president-election-polls-model",
    "270toWin": "https://www.270towin.com/2024-presidential-election-polls/",
    "Economist": "https://www.economist.com/interactive/us-2024-election/trump-harris-polls",
    "New York Times": "https://www.nytimes.com/interactive/2024/us/elections/polls-president.html"
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
.markdown-body table th, .markdown-body table td {{
    padding: 5px 10px;
    border: 1px solid #dfe2e5;
}}
th, td {{
    text-align: left;
}}
.markdown-body>*:last-child {{
    display: none;
}}
@media (max-width: 400px) {{
    th, td {{
        font-size: .9em;  /* Smaller font size on small screens */
    }}
}}
@media (max-width: 320px) {{
    th, td {{
        font-size: .8em;  /* Smaller font size on small screens */
    }}
}}
</style>

## Harris v. Trump: The latest

### Swing state polling averages
{state_msg}

| Place | Margin | Source |
|-------|--------|--------|
"""

for _, row in states_fte.iterrows():
    # Determine the background color based on the winner
    if row['winning'].startswith('D'):
        background_color = '#5194C3'  # Blue for Democrat
    elif row['winning'].startswith('R'):
        background_color = '#c52622'  # Red for Republican
    elif row['winning'].startswith('T'):
        background_color = '#7c4ea5'  # Purple for Tie
    else:
        background_color = '#c52622'  # Default to Red if no match (shouldn't happen if data is clean)
    
    # Apply the determined background color to the margin style
    margin_style = f"<span style='background: {background_color}; padding:1px 4px; color: #ffffff; font-weight: bold;'>{row['winning']}</span>"
    source_link = f"[FiveThirtyEight]({row['source_url']})"
    markdown_content += f"| {row['state']} | {margin_style} | {source_link} |\n"

markdown_content += f"""

**Data:** [Latest](https://stilesdata.com/polling/harris_trump/polls_avg/avgs/state_averages_latest.json), [trend](https://stilesdata.com/polling/harris_trump/polls_avg/avgs/state_averages_trend.json)

### All the national polling averages
{msg}

| Place             | Margin               | Source       |
|-------------------|----------------------|--------------|
"""

# Append each row of the DataFrame to the markdown table with links
for index, row in df.iterrows():
    source_name = row['source']
    source_location = 'US'
    source_link = source_links.get(source_name, "#")
    margin_style = f"<span style='background: {'#5194C3' if 'D' in row['winning'] else '#c52622'}; padding:1px 4px; color: #ffffff; font-weight: bold;'>{row['winning']}</span>"
    
    # Style the Harris and Trump percentage with respective text colors, rounded to 1 decimal place
    harris_style = f"<span style='color: #5194C3; font-weight: bold;'>{row['harris']:.1f}</span>"
    trump_style = f"<span style='color: #c52622; font-weight: bold;'>{row['trump']:.1f}</span>"
    
    # markdown_content += f"| [{source_name}]({source_link}) | {harris_style} / {trump_style} | {margin_style} |\n"
    markdown_content += f"| {source_location} | {margin_style} |[{source_name}]({source_link}) \n"



# Add additional content after the table
markdown_content += f'\n\n **Data:** [Latest](https://stilesdata.com/polling/harris_trump/polls_avg/avgs/averages_latest.json), [trend](https://stilesdata.com/polling/harris_trump/polls_avg/avgs/averages_trend.json) \n\n **About this page:** [Github repo](https://github.com/stiles/polls) \n\n **Last update:** *{last_updated_str}*.'

# Write markdown to file
with open("index.md", "w") as f:
    f.write(markdown_content)