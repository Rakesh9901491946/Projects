from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fetch_transform_load_to_bigquery',
    default_args=default_args,
    description='Fetch Stack Overflow data, transform it, and load it to BigQuery',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
)

# Task 1: Fetch Data from Stack Exchange API as a Python job on Dataproc
fetch_task = DataprocSubmitJobOperator(
    task_id="fetch_data_with_dataproc",
    job={
        "placement": {"cluster_name": "stack-overflow"},
        "pyspark_job": {"main_python_file_uri": "gs://stackoverflow-data-pipeline/fetch_data_from_api.py"},
    },
    region="us-central1",
    project_id="team-ayra-441115",
    dag=dag
)

# Task 2: Transform Data with Dataproc (includes writing to GCS and BigQuery)
transform_task = DataprocSubmitJobOperator(
    task_id="transform_data_with_dataproc",
    job={
        "placement": {"cluster_name": "stack-overflow"},
        "pyspark_job": {"main_python_file_uri": "gs://stackoverflow-data-pipeline/transform.py"},
    },
    region="us-central1",
    project_id="team-ayra-441115",
    dag=dag
)

# Define Task Dependencies
fetch_task >> transform_task
