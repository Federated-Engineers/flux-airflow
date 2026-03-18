from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator

from business_logic.lumina_properties.lumina_data_ingestion import \
    extract_lumina_data


default_args = {
    "owner": "flux",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

with DAG(
    dag_id="flux_dag",
    default_args=default_args,
    start_date=datetime(2026, 3, 16),
    schedule="@daily",
    catchup=False,
) as dag:
    
    start = EmptyOperator(task_id="start")

    run_extraction = PythonOperator(
        task_id="run_extraction",
        python_callable=extract_lumina_data
    )

    start >> run_extraction