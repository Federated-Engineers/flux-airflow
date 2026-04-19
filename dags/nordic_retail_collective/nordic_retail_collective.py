
from datetime import timedelta

from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from business_logic.nordic_retail_collective.nordic_data_transform import \
    transform_json_to_parquet_s3

DAG_ID = 'nordic_retail_collective'

default_args = {
    "owner": "nordic_retail_collective",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

# constants
S3_BUCKET = "federated-engineers-production-flux-data-engineers-nordic"
S3_KEY = "nordic_logistics/"
REDSHIFT_SCHEMA = "nordic_retail"
REDSHIFT_TABLE = "logistics"
REDSHIFT_CONN_ID = "redshift"

dag = DAG(
    dag_id="nordic_retail_collective",
    description="Loads NRC \
        transactional data to Redshift daily",
    default_args=default_args,
    schedule="0 0 * * *",
    catchup=False,
)

generate_transaction_data = PythonOperator(
    task_id="transform_to_s3",
    python_callable=transform_json_to_parquet_s3,
    op_kwargs={
        "source_bucket": "nrc-logistics-raw",
        "source_path": "shipcloud-api/",
        "target_bucket": "federated-engineers-production-flux-data-engineers-nordic",
        "target_path": "nordic_logistics"
    },
    dag=dag
)

execute_query = SQLExecuteQueryOperator(
    task_id="create_table",
    conn_id=REDSHIFT_CONN_ID,
    database="nordic_logistics_warehouse",
    sql="./sql/create_table.sql",
    split_statements=True,
    return_last=False,
)

s3_to_redshift = S3ToRedshiftOperator(
    task_id="s3_to_redshift",
    schema="public",
    table=REDSHIFT_TABLE,
    s3_bucket=S3_BUCKET,
    s3_key=S3_KEY,
    copy_options=["FORMAT AS PARQUET"],
    redshift_conn_id=REDSHIFT_CONN_ID,
    dag=dag
)

generate_transaction_data >> execute_query >> s3_to_redshift
