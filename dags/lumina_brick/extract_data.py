from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator

from business_logic.lumina_properties.lumina_data_ingestion import \
    extract_lumina_data


default_args = {
    "owner": "lumina_bricks_property",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="lumina_dag",
    default_args=default_args,
    start_date=datetime(2026, 3, 16),
    schedule="@daily",
    catchup=False,
) as dag:
    
    start = EmptyOperator(task_id="start")

    extract_db_to_s3 = PythonOperator(
        task_id="extract_db_to_s3",
        python_callable=extract_lumina_data
    )

    start >> extract_db_to_s3