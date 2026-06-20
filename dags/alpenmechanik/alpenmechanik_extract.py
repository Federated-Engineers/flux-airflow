from datetime import datetime, timedelta

from airflow.providers.amazon.aws.operators.lambda_function import \
    LambdaInvokeFunctionOperator
from airflow.sdk import DAG

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

    trigger_lambda = LambdaInvokeFunctionOperator(
        task_id="trigger_sheet_transformer",
        function_name="sheet-transformer",
        aws_conn_id="aws_default",
        invocation_type="RequestResponse",
        log_type="Tail",
    )
