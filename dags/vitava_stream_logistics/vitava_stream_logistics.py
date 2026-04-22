from airflow.sdk import DAG
from airflow.providers.amazon.aws.operators.dms import DmsStartReplicationOperator
from airflow.providers.amazon.aws.operators.dms import DmsCreateReplicationConfigOperator

from airflow.models import Variable
from datetime import datetime, timedelta
import json

endpoints = Variable.get("vsl_dms_endpoints", deserialize_json=True)

default_args = {
    "owner": "Vitava Stream Logistics (VSL)",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="vitava_stream_logistics_dms_replication",
    description="DMS replication pipeline for VSL",
    default_args=default_args,
    schedule="0 0 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    create_replication_config = DmsCreateReplicationConfigOperator(
        task_id="create_replication_config",
        replication_config_id="vitava-replication",
        source_endpoint_arn=endpoints["source_endpoint_arn"],
        target_endpoint_arn=endpoints["target_endpoint_arn"],
        replication_type="full-load",
        compute_config={
            "MaxCapacityUnits": 4,
            "MinCapacityUnits": 1,
            "MultiAZ": False,
            "ReplicationSubnetGroupId": "default",
        },
        table_mappings = json.dumps({
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "1",
                    "object-locator": {
                        "schema-name": "%",
                        "table-name": "%"
                    },
                    "rule-action": "include"
                }
            ]
    })
    )

    start_replication = DmsStartReplicationOperator(
        task_id="replicate",
        replication_config_arn="{{ ti.xcom_pull(task_ids='create_replication_config') }}",
        replication_start_type="start-replication",
        wait_for_completion=True,
        waiter_delay=60,
        waiter_max_attempts=200
    )
    create_replication_config >> start_replication