from pyspark.sql import SparkSession
import requests
import time
from datetime import datetime, timedelta, timezone
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType


# Initialize Spark session
spark = SparkSession.builder.appName("FetchRecentGitHubUsersData").getOrCreate()

# GitHub API and Cloud Storage configuration
my_token = "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"  # Use environment variable for security
if not my_token:
    raise ValueError("GitHub token not found. Please set the 'GITHUB_TOKEN' environment variable.")

bucket_name = "flight-data-pipeline-bucket"  # Replace with your Cloud Storage bucket name
output_path = f"gs://{bucket_name}/github_users_data.csv"
num_of_users = 10000  # Fetching 10,000 users
users_per_query = 1000  # Maximum users per query due to API limitations

# Define schema for the DataFrame
schema = StructType([
    StructField("Username", StringType(), True),
    StructField("ID", IntegerType(), True),
    StructField("Profile URL", StringType(), True),
    StructField("Type", StringType(), True),
    StructField("Site Admin", BooleanType(), True),
    StructField("Name", StringType(), True),
    StructField("Company", StringType(), True),
    StructField("Blog", StringType(), True),
    StructField("Location", StringType(), True),
    StructField("Email", StringType(), True),
    StructField("Bio", StringType(), True),
    StructField("Public Repos", IntegerType(), True),
    StructField("Public Gists", IntegerType(), True),
    StructField("Followers", IntegerType(), True),
    StructField("Following", IntegerType(), True),
    StructField("Account Created At", StringType(), True),
    StructField("Last Updated At", StringType(), True)
])

# Function to fetch users for a given date range
def fetch_users_by_date_range(start_date, end_date):
    users = []
    headers = {'Authorization': f'token {my_token}'}
    search_url = "https://api.github.com/search/users"
    per_page = 100  # Maximum results per page
    max_pages = 10  # To get up to 1000 results per date range

    for page in range(1, max_pages + 1):
        params = {
            'q': f'created:{start_date.strftime("%Y-%m-%d")}..{end_date.strftime("%Y-%m-%d")}',
            'sort': 'created',
            'order': 'desc',
            'per_page': per_page,
            'page': page
        }
        while True:
            response = requests.get(search_url, headers=headers, params=params)
            if response.status_code == 200:
                break
            elif response.status_code == 403:
                # Handle rate limit errors
                print("Rate limit exceeded. Sleeping for 60 seconds.")
                time.sleep(60)
                continue
            elif response.status_code == 401:
                raise ValueError("Authentication failed. Check your GitHub token.")
            else:
                print(f"Failed to retrieve users data: {response.status_code} {response.text}")
                return users  # Return what we have so far

        data = response.json()
        items = data.get('items', [])
        if not items:
            break  # No more users to fetch

        users.extend(items)
        print(f"Fetched {len(users)} users in current date range...")

        # Sleep to respect rate limits (30 requests per minute)
        time.sleep(2)

    return users

# Function to fetch details of each user by username
def fetch_user_details(username):
    user_url = f"https://api.github.com/users/{username}"
    headers = {'Authorization': f'token {my_token}'}
    while True:
        response = requests.get(user_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            # Handle rate limit errors
            print(f"Rate limit exceeded while fetching details for {username}. Sleeping for 60 seconds.")
            time.sleep(60)
            continue
        elif response.status_code == 401:
            raise ValueError("Authentication failed. Check your GitHub token.")
        else:
            print(f"Failed to fetch details for {username}: {response.status_code} {response.text}")
            return None

# Main code to fetch users
all_users = []
current_date = datetime.now(timezone.utc)
days_back = 0

print("Starting data fetch...")

while len(all_users) < num_of_users:
    # Adjust the date range to one day at a time
    end_date = current_date - timedelta(days=days_back)
    start_date = end_date - timedelta(days=1)

    print(f"Fetching users created between {start_date.date()} and {end_date.date()}")
    users = fetch_users_by_date_range(start_date, end_date)
    
    if not users:
        print(f"No users found for date range {start_date.date()} to {end_date.date()}")
        days_back += 1
        continue

    all_users.extend(users)
    days_back += 1

    # Break if we have fetched enough users
    if len(all_users) >= num_of_users:
        break

    # Sleep to respect rate limits
    time.sleep(2)

# Truncate to desired number of users
all_users = all_users[:num_of_users]

print(f"Total users fetched: {len(all_users)}")

# Fetch detailed information for each user
detailed_users_data = []
for idx, user in enumerate(all_users, 1):
    username = user['login']
    details = fetch_user_details(username)
    
    if details:
        detailed_users_data.append([
            details.get("login"),
            details.get("id"),
            details.get("html_url"),
            details.get("type"),
            details.get("site_admin"),
            details.get("name"),
            details.get("company"),
            details.get("blog"),
            details.get("location"),
            details.get("email"),
            details.get("bio"),
            details.get("public_repos"),
            details.get("public_gists"),
            details.get("followers"),
            details.get("following"),
            details.get("created_at"),
            details.get("updated_at")
        ])
    else:
        print(f"Details not found for user: {username}")
    
    print(f"Processed {idx}/{len(all_users)} users")
    
    # Sleep to avoid hitting rate limits for user detail requests
    time.sleep(1.5)

# Convert the list of detailed user data to a Spark DataFrame
df = spark.createDataFrame(detailed_users_data, schema=schema)

# Coalesce DataFrame to 1 partition for writing a single CSV file
df_single_partition = df.coalesce(1)

# Write DataFrame as a single CSV file to Cloud Storage
df_single_partition.write.option("header", "true").mode("overwrite").csv(output_path)

print("Data fetching and CSV export to Cloud Storage complete!")
