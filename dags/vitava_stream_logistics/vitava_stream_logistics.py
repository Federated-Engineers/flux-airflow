from airflow.sdk import DAG
from airflow.providers.amazon.aws.operators.dms import DmsStartReplicationOperator
from airflow.models import Variable
from datetime import datetime, timedelta

default_args = {
    "owner": "Vitava Stream Logistics (VSL)",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    dag_id="vitava_stream_logistics_dms_replication",
    description="DAG to start DMS replication task for Vitava Stream Logistics (VSL)",
    default_args=default_args,
    schedule="0 0 * * *",
    catchup=False,
)

replicate = DmsStartReplicationOperator(
    task_id="replicate",
    replication_config_arn=Variable.get("dms_replication_config_arn")
    replication_start_type="start-replication",
    wait_for_completion=True,
    waiter_delay=60,
    waiter_max_attempts=200,
    dag=dag
)