from datetime import datetime, timedelta

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from business_logic.alpenmechanik.alpenmechanik_data import run_pipeline

DAG_ID = "alpenmechanik_data_AG"

default_args = {
    "owner": "alpenmechanik_data_AG",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=10),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    schedule="0 0 * * *",
    start_date=datetime(2026, 6, 13),
    catchup=False,
    tags=["alpenmechanik"],
) as dag:
    alpinemechanik_data = PythonOperator(
        task_id="alpinemechanik_data",
        python_callable=run_pipeline,
    )

alpinemechanik_data
