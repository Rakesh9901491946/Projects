from pyspark.sql import SparkSession
from pyspark.sql.types import TimestampType
from pyspark.sql.functions import col, from_unixtime

# Initialize Spark session with GCS and BigQuery support
spark = SparkSession.builder \
    .appName("StackOverflowETL") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.30.0") \
    .getOrCreate()

# GCS Bucket and file info
bucket_name = "stackoverflow-data-pipeline"
input_file_path = f"gs://{bucket_name}/latest_stack_overflow_user_data.csv"
output_file_path = f"gs://{bucket_name}/data/transformed_data/output.csv"

# Load CSV file from GCS into a Spark DataFrame
print("Reading CSV file from GCS...")
df = spark.read.option("header", "true").csv(input_file_path)

# Basic Transformation 1: Remove columns with all null values
df_non_null = df.dropna(how="all", subset=df.columns)

# Convert 'creation_date' and 'last_access_date' from Unix timestamp format to TimestampType
if 'creation_date' in df_non_null.columns:
    df_non_null = df_non_null.withColumn("creation_date", from_unixtime(col("creation_date").cast("long")).cast(TimestampType()))

if 'last_access_date' in df_non_null.columns:
    df_non_null = df_non_null.withColumn("last_access_date", from_unixtime(col("last_access_date").cast("long")).cast(TimestampType()))

# Drop the last three columns if there are more than three columns in the DataFrame
if len(df_non_null.columns) > 3:
    df_non_null = df_non_null.drop(*df_non_null.columns[-3:])

# Print schema and preview data for verification
print("Schema after transformations and dropping columns:")
df_non_null.printSchema()
print("Data preview after transformations:")
df_non_null.show(5)

# Save the transformed DataFrame as a CSV file to GCS
print("Writing transformed data to GCS...")
df_non_null.write.csv(output_file_path, mode="overwrite", header=True)

# Specify BigQuery destination table
destination_table = "team-ayra-441115.stackoverflow_data.latest_stack_overflow_user_data"

# Write the DataFrame to BigQuery
print("Writing data to BigQuery...")
df_non_null.write \
    .format("bigquery") \
    .option("table", destination_table) \
    .option("temporaryGcsBucket", bucket_name) \
    .mode("overwrite") \
    .save()

print("Data successfully written to GCS and BigQuery")

# Stop the Spark session
spark.stop()
