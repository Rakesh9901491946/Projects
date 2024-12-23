from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, col

# GCP configuration
project_id = "aviation-440417"
bucket_name = "flight-data-pipeline-bucket"
output_table = f"{project_id}.flight_data.processed_flights"

def main():
    spark = SparkSession.builder.appName("TransformAndLoadToBQ").getOrCreate()

    # Define the Cloud Storage path where the JSON files are stored
    input_path = f"gs://{bucket_name}/raw_data/*.json"
    
    # Read the JSON data from Cloud Storage
    df = spark.read.json(input_path)
    
    # Transform the data
    df = df.withColumn("flight_date", to_timestamp("flight_date", "yyyy-MM-dd"))
    df = df.filter(df.flight_date.isNotNull())  # Ensure flight_date is not null
    
    # Load the transformed data into BigQuery
    df.write \
        .format("bigquery") \
        .option("table", output_table) \
        .option("temporaryGcsBucket", bucket_name) \
        .mode("append") \
        .save()
    
    print("Data loaded into BigQuery successfully.")

if __name__ == "__main__":
    main()
