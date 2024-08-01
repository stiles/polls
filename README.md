
# Polls

Practicing automated collection of political polls.

This project the fetches, processes and stores political polling data, focusing on key matchups in upcoming elections. It uses Python scripts to retrieve data from various sources and stores the outputs in CSV and JSON formats on AWS S3. The process runs twice daily using Github Actions. 

## Sources

### RealClearPolitics

- **Source**: [RealClearPolitics](https://www.realclearpolitics.com/)
- **API endpoint**: `https://www.realclearpolitics.com/api/polls-feed`
- **Poll example**: 2024 General Election: Trump vs Harris

## Process

1. **Data fetching**: The script retrieves poll data from the RealClearPolitics API using POST requests. 

2. **Data processing**: 
    - Extracts relevant fields, including poll dates, candidates and spread values.
    - Cleans and formats the data into structured DataFrames.
    - Splits `polling_period` into `polling_start_date` and `polling_end_date` for averages.

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

### Paths on S3

- **CSV files**:
  - All Harris-Trump polls (*2022-present*): 
  [https://stilesdata.com/polling/harris_trump_polls.csv](https://stilesdata.com/polling/harris_trump_polls.csv)
  - Latest Harris-Trump average: 
  [https://stilesdata.com/polling/harris_trump_avg.csv](https://stilesdata.com/polling/harris_trump_avg.csv)
  - Harris-Trump average archive files (*stored by date*):
  [https://stilesdata.com/polling/archive/harris_trump_avg_YYYY-MM-DD.csv](https://stilesdata.com/polling/archive/harris_trump_avg_YYYY-MM-DD.csv)

- **JSON files**:
  - All Harris-Trump polls (*2022-present*): 
  [https://stilesdata.com/polling/harris_trump_polls.json](https://stilesdata.com/polling/harris_trump_polls.json)
  - Latest Harris-Trump average: 
  [https://stilesdata.com/polling/harris_trump_avg.json](https://stilesdata.com/polling/harris_trump_avg.json)

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
        "id": 12345,
        "type": "rcp_average",
        "polling_start_date": "2024-07-01",
        "polling_end_date": "2024-07-10",
        "spread_winner": "Trump",
        "spread_value": 1.5,
        "trump_value": 47.5,
        "harris_value": 46.0
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

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.