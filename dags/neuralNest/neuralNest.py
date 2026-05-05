import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from business_logic.neuralNest.get_ehealth_data import get_ehealth_data
from business_logic.neuralNest.get_finance_classification_data import \
    get_finance_classification_data
from business_logic.neuralNest.get_finance_user_data import \
    _get_finance_user_data
from business_logic.neuralNest.get_patient_data import \
    _get_patient_hospital_visit_data

logger = logging.getLogger(__name__)

default_args = {
    "owner": "neural_nest",
    "depends_on_past": False,
    "start_date": datetime(2026, 5, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="neural_nest_dag",
    start_date=datetime(2026, 5, 1),
    catchup=False,
    default_args=default_args,
    description="Fetch from Google Drive/Sheets API and upload to S3",
    tags=["FE", "neural_nest", "google_sheets", "google_drive", "s3"],
) as dag:

    # Task 1: Get patient hospital visit data
    task_get_patient = PythonOperator(
        task_id="get_patient_data",
        python_callable=_get_patient_hospital_visit_data
    )

    # Task 2: Get finance user data
    task_get_finance_user = PythonOperator(
        task_id="get_finance_user",
        python_callable=_get_finance_user_data
    )

    # Task 3: Get finance classification data
    task_get_finance_classification = PythonOperator(
        task_id="get_finance_classification",
        python_callable=get_finance_classification_data,
    )

    # Task 4: Get ehealth data
    task_get_ehealth = PythonOperator(
        task_id="get_ehealth_data",
        python_callable=get_ehealth_data
    )

[
    task_get_patient,
    task_get_finance_user,
    task_get_finance_classification,
    task_get_ehealth,
]
