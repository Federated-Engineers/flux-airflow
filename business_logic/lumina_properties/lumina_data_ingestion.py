import os
import pandas as pd
import boto3
import logging

from dotenv import load_dotenv
from io import BytesIO
from airflow.models import Variable
from plugins.utils.database import get_db_connection

load_dotenv()

logger = logging.getLogger(__name__)

def extract_lumina_data():
    logger.info("Starting Lumnina data extration process")

    credentials = Variable.get("postgres_conn_string")
    # credentials = os.getenv("postgres_conn_string")
    engine = get_db_connection(credentials)

    s3_bucket = "demo-03-bucket"
    s3_prefix = "historical"
    s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

    tables = [
        "historical_transactions",
        "property_metadata",
        "renovation_ledgers",
        "neighborhood_demographics",
        "zoning_permits"
    ]

    partition_columns = {
        "historical_transactions": "sale_date",
        "zoning_permits": "application_date"
    }

    for table_name in tables:

        logger.info(f"Starting extraction for table: {table_name}")

        query = f"SELECT * FROM historical.{table_name}"

        try:
            with engine.connect() as conn:
                raw_conn = conn.connection
                chunk_filter = pd.read_sql_query(query, con=raw_conn, chunksize=40000)

                for i, chunk_df in enumerate(chunk_filter):

                    if table_name in partition_columns:
                        date_column = partition_columns[table_name]

                        logger.info(f"Applying partitioning using column: {date_column}")

                        chunk_df[date_column] = pd.to_datetime(chunk_df[date_column], errors="coerce")

                        chunk_df["year"] = chunk_df[date_column].dt.year
                        chunk_df["month"] = chunk_df[date_column].dt.month

                        for (year, month), partition_df in chunk_df.groupby(["year", "month"]):

                            buffer = BytesIO()

                            partition_df.to_parquet(buffer, index=False)

                            buffer.seek(0)

                            s3_key = f"{s3_prefix}/{table_name}/year={year}/month={month}/{table_name}_{i}.parquet"

                            s3.upload_fileobj(buffer, s3_bucket, s3_key)

                            logger.info(f"Uploaded file to s3://{s3_bucket}/{s3_key}")

                    else:
                        logger.info(f"Uploading non-partitioned chunk {i} for table {table_name}")

                        buffer = BytesIO()

                        chunk_df.to_parquet(buffer, index=False)

                        buffer.seek(0)

                        s3_key = f"{s3_prefix}/{table_name}/{table_name}_batch{i}.parquet"

                        s3.upload_fileobj(buffer, s3_bucket, s3_key)

                        logger.info(f"Uploaded file to s3://{s3_bucket}/{s3_key}")

                    logger.info(f"Finished processing table: {table_name}")

        except Exception as e:
                logger.error(f"Error occurred while processing table {table_name}: {str(e)}")
                raise ValueError(f"Could not read {table_name}. Error: {str(e)}")
        
    logger.info("Lumina data extraction completed successfully")

    return "Extraction was Successful"
