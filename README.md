
# Polls

Automating the collection of political polls.

This project automates the fetching, processing and storing of political poll data, focusing on key matchups in upcoming elections. It uses Python scripts to retrieve data from various sources and stores the outputs in CSV and JSON formats on AWS S3.

## Sources

### RealClearPolitics

- **Website**: [RealClearPolitics](https://www.realclearpolitics.com/)
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

- **Bucket**: `stilesdata.com`

- **CSV files**:
  - [Harris-Trump Polls CSV](s3://stilesdata.com/polling/harris_trump_polls.csv)
  - [Harris-Trump Average CSV](s3://stilesdata.com/polling/harris_trump_avg.csv)
  - [Harris-Trump Average Archive CSV](s3://stilesdata.com/polling/archive/harris_trump_avg_YYYY-MM-DD.csv)

- **JSON files**:
  - [Harris-Trump Polls JSON](s3://stilesdata.com/polling/harris_trump_polls.json)
  - [Harris-Trump Average JSON](s3://stilesdata.com/polling/harris_trump_avg.json)

### Sample outputs

#### Harris-Trump Polls (CSV)
```
id,type,pollster,polling_start_date,polling_end_date,sampleSize,marginError,spread_winner,spread_value,trump_value,harris_value
12345,Poll,ABC Polling,2024-07-01,2024-07-10,1000,3.0,Trump,2.0,48,46
```

#### Harris-Trump Average (JSON)
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
