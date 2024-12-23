import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, monotonically_increasing_id
import requests

# Initialize Spark session
spark = SparkSession.builder.appName("StackOverflowUserDataPipeline").getOrCreate()
sc = spark.sparkContext

# Your Stack Exchange API key
api_key = "rl_USGxi6B7hmcJsv6MkaThKWhah"  # Replace with your actual API key

# Desired number of records
total_records = 100
pagesize = 100  # Set to 100 to minimize API calls and fetch maximum in each request

# Function to fetch data from the Stack Exchange API
def fetch_user_data():
    all_data = []
    page = 1
    collected_records = 0
    
    while collected_records < total_records:
        url = (
            f"https://api.stackexchange.com/2.3/users"
            f"?order=desc&sort=creation&site=stackoverflow"
            f"&pagesize={pagesize}&page={page}&key={api_key}"
        )
        print(f"Fetching page {page} with URL: {url}")
        
        response = requests.get(url)
        data = response.json()
        
        # Check for 'backoff' in all responses and respect it
        if 'backoff' in data:
            backoff_time = data['backoff']
            print(f"Backoff requested. Waiting {backoff_time} seconds.")
            time.sleep(backoff_time)
        
        if response.status_code == 200:
            results = data.get('items', [])
            if not results:
                print("No more data available.")
                break
            all_data.extend(results[:total_records - collected_records])  # Limit to remaining needed records
            collected_records += len(results)
            print(f"Collected {collected_records} records so far.")
            
            if collected_records >= total_records or not data.get("has_more"):
                break

            page += 1
            # Default delay to respect rate limits
            time.sleep(5)
        else:
            print(f"Error fetching data: {response.status_code}")
            print(f"Response details: {data}")
            if response.status_code == 502:
                print("Throttle violation encountered. Waiting 60 seconds before retrying.")
                time.sleep(60)
            else:
                print("An error occurred. Stopping data fetch.")
                break  # Exit on non-200 status to debug further if necessary
    
    return all_data[:total_records]  # Return only the latest 100 records

# Fetch data
print("Fetching user data from Stack Exchange API...")
data = fetch_user_data()
print(f"Fetched {len(data)} records.")

# Proceed if data is available
if data:
    # Create Spark DataFrame from data
    df = spark.createDataFrame(data)
    
    # Add index column with unique values
    df = df.withColumn("index", monotonically_increasing_id())
    
    # Convert Unix timestamp to readable date format
    df = df.withColumn("creation_date", from_unixtime(df["creation_date"]))
    df = df.withColumn("last_access_date", from_unixtime(df["last_access_date"]))
    
    # Reorder columns to match your desired order
    desired_columns = [
        'index', 'account_id', 'reputation', 'user_id', 'user_type',
        'profile_image', 'display_name', 'link', 'creation_date',
        'last_access_date'
    ]
    df = df.select(*desired_columns)
    
    # Coalesce to 1 partition to get a single output file
    df = df.coalesce(1)
    
    # Define temporary output path
    temp_output_path = "gs://stackoverflow-data-pipeline/temp_output/"
    
    # Write the data to GCS as CSV in a temporary directory
    df.write.mode("overwrite").option("header", "true").csv(temp_output_path)
    
    # Use Hadoop FileSystem API to rename the part file to desired output file
    def move_and_rename_file(temp_path, final_path):
        # Get Hadoop FileSystem for the GCS path
        uri = sc._jvm.java.net.URI.create(temp_path)
        fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(uri, sc._jsc.hadoopConfiguration())
        # Convert paths to Hadoop Path objects
        temp_path_hadoop = sc._jvm.org.apache.hadoop.fs.Path(temp_path)
        final_path_hadoop = sc._jvm.org.apache.hadoop.fs.Path(final_path)
        # List files in the temporary output directory
        files = fs.listStatus(temp_path_hadoop)
        for file in files:
            filename = file.getPath().getName()
            if filename.startswith('part-') and filename.endswith('.csv'):
                src_path = file.getPath()
                # Move and rename the file
                fs.rename(src_path, final_path_hadoop)
                break
        # Delete the temporary directory
        fs.delete(temp_path_hadoop, True)
    
    # Define final output path
    final_output_path = "gs://stackoverflow-data-pipeline/latest_stack_overflow_user_data.csv"
    
    # Move and rename the file
    move_and_rename_file(temp_output_path, final_output_path)
    
    print(f'Data saved to {final_output_path}')
else:
    print("No data fetched. Exiting.")
    
# Stop the Spark session
spark.stop()
