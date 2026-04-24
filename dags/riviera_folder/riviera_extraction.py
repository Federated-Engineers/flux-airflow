from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from business_logic.riviera_soleil.riviera_data_ingestion import load_data

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 4, 10),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    dag_id="google_sheets_to_s3",
    description="Moving data from Google Sheets to S3",
    schedule="0 0 * * *",
    start_date=datetime(2026, 4, 10),
    default_args=default_args,
    catchup=False,
)

upload_to_s3 = PythonOperator(
    task_id="upload_to_s3",
    python_callable=load_data,
    dag=dag,
)

upload_to_s3
