import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from datetime import datetime, timedelta
from airflow.decorators import dag, task

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

@dag(dag_id="flux_dag",default_args=default_args, start_date=datetime(2026, 3, 8), schedule= "@daily", catchup=False)
def lumina_pipeline():
    @task()
    def run_extraction():
        lumina_data = extract_lumina_data()
        return lumina_data
    
    run_extraction()

lumina_pipeline()
