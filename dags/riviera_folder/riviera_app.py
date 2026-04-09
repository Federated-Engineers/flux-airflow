from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from business_logic.riviera_soleil.main import get_load_data


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 04, 11),
    'email': ['chinyere.nwigwe126@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)}

dag = DAG(
    dag_id="google_sheets_to_s3",
    description="Moving data from Google Sheets to S3",
    schedule_interval="@weekly",
    start_date=datetime(2026, 4, 11),
    default_args=default_args,
) 

upload_to_s3 = PythonOperator(
    task_id="upload_to_s3",
    python_callable=get_load_data,
    dag=dag,
)

upload_to_s3