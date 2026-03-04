import datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from business_logic.lumina_properties.lumina_data_ingestion import \
    extract_lumina_data

my_dag = DAG(
    dag_id="lumina",
    start_date=datetime.datetime(2026, 3, 4),
    schedule="@daily",
)

lumina_pipeline = PythonOperator(
    dag=my_dag,
    python_callable=extract_lumina_data,
    task_id="lumina_pipeline"
    )

lumina_pipeline