
# US election polls

This project is a non-commercial exercise in the automated collection of political polls. It fetches, processes and stores political polling data, focusing on key state and national matchups in the upcoming presidential election. It uses Python scripts to retrieve data and stores the outputs in CSV and JSON formats in the `data` directory and on AWS S3. The process runs three times per day — at 6 am, noon and 6 pm Pacific Time — using a Github Actions workflow, which finishes by copying all data to S3. 

## Sources

### RealClearPolitics

- **Source**: [RealClearPolitics](https://www.realclearpolitics.com/)
- **Data: Poll JSON files**: Outlined in `data/polls_config.json`
- **Poll subjects**: The head-to-head general election matchup between former President Trump and Vice President Harris at the national level and in several "swing" states: Pennsylvania, Michigan, Wisconsin, Georgia, North Carolina, Nevada and Arizona. Polls tangential to the race, such as the national mood about the country's trajectory, the generic partisan congressional ballot and Harris' political favorability, are also collected. 

## Process

1. **Data fetching**: A python script — `fetch_polls.py` retrieves poll data and RealClearPolitics averages from json endpoints (outlined in `data/polls_config.json`) for each poll group (general election, state, topic, etc.). 

2. **Data processing**: 
    - Extract relevant fields, including poll dates, candidates, topics and spread values.
    - Clean and format data into structured dataframes.
    - Splits individual polls and RCP averages into separate outputs.

3. **Data cleaning**:
    - Standardizes date formats to `%Y-%m-%d`.
    - Converts numerical fields for analysis.

4. **Data storage**:
    - Saves processed data as CSV and JSON files.
    - Uploads files to AWS S3 for persistent storage.

### Outputs

Below is a table of poll data files available on S3:

| Subject                         | Location       | All polls                                                                | Current average                                                         |
|---------------------------------|----------------|----------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Trump v. Harris                 | National       | [JSON](https://stilesdata.com/polling/harris_trump/polls/general.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/general.csv)         | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/general.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/general.csv)         |
| Trump v. Harris + third parties | National       | [JSON](https://stilesdata.com/polling/harris_trump/polls/general_third_parties.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/general_third_parties.csv) | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/general_third_parties.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/general_third_parties.csv) |
| Trump v. Harris                 | Arizona        | [JSON](https://stilesdata.com/polling/harris_trump/polls/arizona.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/arizona.csv)         | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/arizona.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/arizona.csv)         |
| Trump v. Harris                 | Georgia        | [JSON](https://stilesdata.com/polling/harris_trump/polls/georgia.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/georgia.csv)         | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/georgia.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/georgia.csv)         |
| Trump v. Harris                 | Michigan       | [JSON](https://stilesdata.com/polling/harris_trump/polls/michigan.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/michigan.csv)       | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/michigan.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/michigan.csv)       |
| Trump v. Harris                 | Nevada         | [JSON](https://stilesdata.com/polling/harris_trump/polls/nevada.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/nevada.csv)           | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/nevada.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/nevada.csv)           |
| Trump v. Harris                 | North Carolina | [JSON](https://stilesdata.com/polling/harris_trump/polls/north_carolina.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/north_carolina.csv) | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/north_carolina.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/north_carolina.csv) |
| Trump v. Harris                 | Pennsylvania   | [JSON](https://stilesdata.com/polling/harris_trump/polls/pennsylvania.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/pennsylvania.csv) | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/pennsylvania.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/pennsylvania.csv) |
| Trump v. Harris                 | Wisconsin      | [JSON](https://stilesdata.com/polling/harris_trump/polls/wisconsin.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/wisconsin.csv)     | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/wisconsin.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/wisconsin.csv)     |
| Congress generic ballot         | National       | [JSON](https://stilesdata.com/polling/harris_trump/polls/congress_generic.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/congress_generic.csv) | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/congress_generic.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/congress_generic.csv) |
| Direction of country            | National       | [JSON](https://stilesdata.com/polling/harris_trump/polls/country_direction.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/country_direction.csv) | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/country_direction.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/country_direction.csv) |
| Harris favorability             | National       | [JSON](https://stilesdata.com/polling/harris_trump/polls/harris_favorability.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls/harris_favorability.csv) | [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/harris_favorability.json) \| [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/harris_favorability.csv) |

In addition, the `process_trend.py` script outputs a timeseries file with the Harris-Trump head-to-head average. This is derived from daily snapshots as part of the workflow in the `data/polls_avg/_trend/daily` directory. 

That trend collection began with the birth of the repo on August 1, 2024. An extended historical trend was also created by scraping past RCP averages from Wayback Machine snapshots like [this one](https://web.archive.org/web/20240221200133/https://www.realclearpolling.com/polls/president/general/2024/trump-vs-harris). That latter process is documented in `notebooks/fetch_harris_trump_rcp_avg_archive.ipynb`. 

- **Harris-Trump RCP average trend:** [JSON](https://stilesdata.com/polling/harris_trump/polls_avg/_trend/harris_trump_trend.json) | [CSV](https://stilesdata.com/polling/harris_trump/polls_avg/_trend/harris_trump_trend.csv)

### Data structure

#### Example: Harris-Trump general election polls (CSV)
```csv
id,type,pollster,date,sampleSize,marginError,link,spread_winner,spread_value,trump_value,harris_value,name,slug,polling_start_date,polling_end_date
146390,poll_rcp_avg,Daily Kos/Civiqs,7/27 - 7/30,1123 RV,3.0,https://civiqs.com/documents/Civiqs_DailyKos_banner_book_2024_07_7knl31.pdf,Harris,4.0,45,49,2024 General Election: Trump vs Harris,general,2024-07-27,2024-07-30
146395,poll_rcp_avg,Rasmussen Reports,7/24 - 7/31,2163 LV,2.0,https://www.rasmussenreports.com/public_content/politics/biden_administration/election_2024_trump_49_harris_44,Trump,5.0,49,44,2024 General Election: Trump vs Harris,general,2024-07-24,2024-07-31
146332,poll_rcp_avg,Reuters/Ipsos,7/26 - 7/28,879 RV,3.5,https://www.reuters.com/world/us/harris-trump-locked-tight-us-presidential-race-reutersipsos-poll-finds-2024-07-30/,Harris,1.0,42,43,2024 General Election: Trump vs Harris,general,2024-07-26,2024-07-28
146302,poll_rcp_avg,Harvard-Harris,7/26 - 7/28,2196 RV,2.1,https://harvardharrispoll.com/crosstabs-july-3/,Trump,4.0,52,48,2024 General Election: Trump vs Harris,general,2024-07-26,2024-07-28
146324,poll_rcp_avg,Morning Consult,7/26 - 7/28,11538 RV,1.0,https://pro.morningconsult.com/trackers/2024-presidential-election-polling,Harris,1.0,46,47,2024 General Election: Trump vs Harris,general,2024-07-26,2024-07-28
```
*Note: The `type` column has both "poll_rcp_avg" and "poll" listed as string values. The former indicates that the particular poll was used to calculate the RCP average at fetch time, not that it represents the RCP average.*

#### Example: Harris-Trump average snapshot (JSON)
```json
[
    {
        "id":"7386",
        "type":"rcp_average",
        "polling_period":"7\/22 - 7\/31",
        "polling_start_date":"2024-07-22",
        "polling_end_date":"2024-07-31",
        "spread_winner":"Trump",
        "spread_value":1.2,
        "trump_value":"47.7",
        "harris_value":"46.5",
        "fetch_date":"2024-08-01"
    }
]
```

## Using this repo

To set up the project and run the data collection scripts, follow these steps:

1. Clone the repository to your local machine.

2. Install the necessary Python packages using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

3. Optional: To store data on S3, update `.github/workflows/fetch_polls.yml` with your path to S3: `s3://{YOUR_BUCKET_NAME}` and configure environment variables (passed in the workflow) in as Github secrets. S3 storage only happens when the workflow runs.
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

4. Execute scripts to fetch and process poll data and trend timeseries locally or by running the workflow:
   ```bash
   python fetch_polls.py
   python process_polls.py
   ```

## Contributing

Please submit any issues or pull requests to contribute to this project. Questions? [Holler](mailto:mattstiles@gmail.com).

## License

This project is licensed under Creative Commons. See the [LICENSE](LICENSE) file for more details.

## Disclaimer

This repo is a personal project that serves as an example for how to create simple data pipelines. It is not affiliated with or used by my employer.