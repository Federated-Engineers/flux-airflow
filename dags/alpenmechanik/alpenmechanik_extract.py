from datetime import timedelta

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from business_logic.alpenmechanik.alpenmechanik_data import run_pipeline

DAG_ID = 'alpenmechanik_data_AG'

default_args = {
    "owner": "alpenmechanik_data_AG",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    dag_id="alpenmechanik_data_AG",
    default_args=default_args,
    schedule="0 0 * * *",
    catchup=False,
)

write_data_to_s3 = PythonOperator(
    dag=dag,
    python_callable=run_pipeline,
    task_id="write_data_to_s3"
    )

write_data_to_s3
