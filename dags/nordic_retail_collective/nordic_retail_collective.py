from datetime import timedelta

from airflow.models import Variable
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk import DAG

DAG_ID = 'nordic_retail_collective'

default_args = {
    "owner": "nordic_retail_collective",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

config = Variable.get("nrc_config", deserialize_json=True)

dag = DAG(
    dag_id="nordic_retail_collective",
    description="Loads NRC \
        transactional data to Redshift daily",
    default_args=default_args,
    schedule="0 0 * * *",
    catchup=False,
    tags=["nrc", "redshift", "s3", "etl"]
)

execute_query = SQLExecuteQueryOperator(
    task_id="create_table",
    conn_id=config["redshift_conn_id"],
    database="nordic_logistics_warehouse",
    sql="./sql/create_table.sql",
    split_statements=True,
    return_last=False,
)

s3_to_redshift = S3ToRedshiftOperator(
    task_id="s3_to_redshift",
    schema=config["redshift_schema"],
    table=config["redshift_table"],
    s3_bucket=config["s3_bucket"],
    s3_key=config["s3_key"],
    copy_options=["FORMAT AS JSON 'auto'"],
    redshift_conn_id=config["redshift_conn_id"],
    dag=dag
)

execute_query >> s3_to_redshift
