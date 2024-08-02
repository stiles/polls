
# US election polls

This project is a non-commercial exercise in the automated collection of political polls. It fetches, processes and stores political polling data, focusing on key state and national matchups in the upcoming presidential election. It uses Python scripts to retrieve data and stores the outputs in CSV and JSON formats in the `data` directory and on AWS S3. The process runs three times per day — at 6 am, noon and 6 pm Pacific Time — using a Github Actions workflow.

## Sources

### RealClearPolitics

- **Source**: [RealClearPolitics](https://www.realclearpolitics.com/)
- **Poll JSON files**: Outlined in `data/polls_config.json`
- **Poll types**: The head-to-head general election matchup between former President Trump and Vice President Harris at the national level and in several "swing" states: Pennsylvania, Michigan, Wisconsin, Georgia, North Carolina, Nevada and Arizona. Polls tangential to the race, such as the national mood about the country's trajectory, the generic partisan congressional ballot and Harris' political favorability, are also collected. 

## Process

1. **Data fetching**: Python scripts retrieve poll data and RealClearPolitics averages from json endpoints for each poll group (general, state, topic, etc.). 

2. **Data processing**: 
    - Extract relevant fields, including poll dates, candidates, topics and spread values.
    - Clean and format data into structured DataFrames.
    - Splits listings of individual polls and RCP averages into separate outputs.

3. **Data cleaning**:
    - Standardizes date formats to `%Y-%m-%d`.
    - Converts numerical fields for analysis.

4. **Data storage**:
    - Saves processed data as CSV and JSON files.
    - Uploads files to AWS S3 for persistent storage.

## Outputs

### File formats

- **CSV**: Stores structured tabular data for easy analysis.
- **JSON**: Provides a flexible format suitable for web applications and APIs.

### What's collected





- **CSV files**:
  - All Harris-Trump polls (*2022-present*): 
  [https://stilesdata.com/polling/harris_trump_polls.csv](https://stilesdata.com/polling/harris_trump_polls.csv)
  - Latest Harris-Trump average: 
  [https://stilesdata.com/polling/harris_trump_avg.csv](https://stilesdata.com/polling/harris_trump_avg.csv)
  - Harris-Trump average archive files (*stored by date*):
  [https://stilesdata.com/polling/archive/harris_trump_avg_YYYY-MM-DD.csv](https://stilesdata.com/polling/archive/harris_trump_avg_YYYY-MM-DD.csv)
   - Harris-Trump average timeseries (archive files combined): 
  [https://stilesdata.com/polling/harris_trump_trend_data.csv](https://stilesdata.com/polling/harris_trump_trend_data.csv)

- **JSON files**:
  - All Harris-Trump polls (*2022-present*): 
  [https://stilesdata.com/polling/harris_trump_polls.json](https://stilesdata.com/polling/harris_trump_polls.json)
  - Latest Harris-Trump average: 
  [https://stilesdata.com/polling/harris_trump_avg.json](https://stilesdata.com/polling/harris_trump_avg.json)
   - Harris-Trump average timeseries (archive files combined): 
  [https://stilesdata.com/polling/harris_trump_trend_data.json](https://stilesdata.com/polling/harris_trump_trend_data.json)

### Formats

#### Harris-Trump polls (CSV)
```
id,pollster,polling_start_date,polling_end_date,sampleSize,marginError,link,spread_winner,spread_value,trump_value,harris_value
146230,Morning Consult,2024-07-22,2024-07-24,11297 RV,1.0,https://pro.morningconsult.com/trackers/2024-presidential-election-polling,Harris,1.0,45,46
```

#### Harris-Trump average (JSON)
```json
[
    {
        "id":"7386",
        "type":"rcp_average",
        "polling_period":"7\/22 - 7\/31",
        "polling_start_date":"2024-07-22",
        "polling_end_date":"2024-07-31",
        "spread_winner":"Trump",
        "spread_value":"+1.2",
        "trump_value":"47.7",
        "harris_value":"46.5",
        "fetch_date":"2024-08-01"
    }
]
```

## Use this repo

To set up the project and run the data collection script, follow these steps:

1. Clone the repository to your local machine.

2. Install the necessary Python packages using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up AWS credentials as environment variables for accessing S3:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

4. Execute the script to fetch and process poll data:
   ```bash
   python fetch_harris_trump.py
   ```

## Contributing

Feel free to submit issues or pull requests to contribute to this project.

## License

This project is licensed under Creative Commons. See the [LICENSE](LICENSE) file for more details.