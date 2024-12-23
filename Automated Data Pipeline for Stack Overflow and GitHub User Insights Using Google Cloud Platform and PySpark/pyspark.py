from pyspark.sql import SparkSession
import requests
import datetime
import json
from google.cloud import storage

# API and GCP configuration
api_key = "Api_Key"  # Replace with your actual API key
project_id = "aviation-440417"
bucket_name = "flight-data-pipeline-bucket"
output_file_name = "aviation_flight_data.csv"

def fetch_data_from_api(start_time, end_time):
    url = 'http://api.aviationstack.com/v1/flights'
    params = {
        'access_key': api_key,
        'limit': 100,
        'flight_date_from': start_time,
        'flight_date_to': end_time
    }

    all_flights = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('data', [])
            all_flights.extend(data)
            if len(data) < 100:
                break  # Stop if fewer than 100 records, as no more pages are available
            params['offset'] = len(all_flights)  # Continue from where left off
        else:
            print(f"Error fetching data: {response.status_code}")
            break
    return all_flights

def main():
    spark = SparkSession.builder.appName("FetchFlightData").getOrCreate()

    # Calculate the 24-hour time window
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=24)
    
    # Format times in ISO 8601 format (required by the API)
    end_time_str = end_time.isoformat() + "Z"
    start_time_str = start_time.isoformat() + "Z"
    
    # Fetch flight data from the API within the last 24-hour window
    flight_data = fetch_data_from_api(start_time_str, end_time_str)

    if flight_data:
        # Create Spark DataFrame from the data
        df = spark.createDataFrame(flight_data)
        
        # Define Cloud Storage path for the CSV file
        output_path = f"gs://{bucket_name}/{output_file_name}"
        
        # Save the data as CSV to Cloud Storage, overwriting each time
        df.write.option("header", "true").mode("overwrite").csv(output_path)
        print(f"Data saved to {output_path}")
    else:
        print("No new data fetched from the API.")

if __name__ == "__main__":
    main()
