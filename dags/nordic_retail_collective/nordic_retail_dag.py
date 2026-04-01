
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator
from business_logic.nordic_retail_collective.nordic_data_transform import \
    transform_json_to_parquet_s3
DAG_ID = 'latest-demo'

default_args = {
    "owner": "lumina_bricks_property",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

# constants
S3_BUCKET = ""
S3_KEY = ""
REDSHIFT_SCHEMA = ""
REDSHIFT_TABLE = ""
REDSHIFT_CONN_ID = "redshift"
AWS_CONN_ID = "aws_default"


dag = DAG(
    dag_id="nordic_retail_collective",
    description="Loads NRC \
        transactional data to Redshift daily",
    default_args=default_args,
    schedule_interval="0 0 * * *",
    catchup=False,
)

generate_transaction_data = PythonOperator(
    task_id="transform_to_s3",
    python_callable=transform_json_to_parquet_s3,
    dag=dag
)

s3_to_redshift = S3ToRedshiftOperator(
    task_id="s3_to_redshift",
    schema=REDSHIFT_SCHEMA,
    table=REDSHIFT_TABLE,
    s3_bucket=S3_BUCKET,
    s3_key=S3_KEY,
    copy_options=["FORMAT AS PARQUET"],
    redshift_conn_id=REDSHIFT_CONN_ID,
    aws_conn_id=AWS_CONN_ID,
    dag=dag
)

generate_transaction_data >> s3_to_redshift
