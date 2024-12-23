import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session with BigQuery support
spark = SparkSession.builder \
    .appName("StackOverflowETL") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.30.0") \
    .getOrCreate()

# Arguments passed from Airflow
input_path = sys.argv[1]  # GCS path of the CSV file
dataset_name = sys.argv[2]  # BigQuery dataset name
table_name = sys.argv[3]  # BigQuery table name

# Load CSV data from GCS into a Spark DataFrame
print("Reading data from GCS...")
df = spark.read.option("header", "true").csv(input_path)

# (Optional) Transform the data - e.g., casting column types
df_transformed = df \
    .withColumn("account_id", col("account_id").cast("long")) \
    .withColumn("reputation", col("reputation").cast("long")) \
    .withColumn("user_id", col("user_id").cast("long")) \
    .withColumn("creation_date", col("creation_date").cast("timestamp")) \
    .withColumn("last_access_date", col("last_access_date").cast("timestamp"))

# Define BigQuery table destination
destination_table = f"{dataset_name}.{table_name}"

# Write the transformed DataFrame to BigQuery
print("Writing data to BigQuery...")
df_transformed.write \
    .format("bigquery") \
    .option("table", destination_table) \
    .mode("overwrite") \
    .save()

print(f"Data successfully written to BigQuery table {destination_table}")

# Stop the Spark session
spark.stop()
