import os

import pandas as pd
import awswrangler as wr
# from airflow.providers.amazon.aws.hooks.s3 import S3HooK
from datetime import datetime
from airflow.models import Variable
from plugins.utils.database import get_db_connection


def extract_lumina_data():
    credentials = Variable.get("postgres_conn_string")
    conn = get_db_connection(credentials)
    bucket_name = "demo-03-bucket"

    today = datetime.now().strftime('%Y-%m-%d')

    tables = [
        # "historical.historical_transactions",
        # "historical.property_metadata",
        # "historical.renovation_ledgers",
        "historical.neighborhood_demographics",
        "historical.zoning_permits"
    ]

    for table_name in tables:
        s3_folder = table_name.replace('.', '_')
        
        query = f"SELECT * FROM {table_name}"

        try:
            chunk_filter = pd.read_sql(query, con=conn, chunksize=50)

            for i, chunk_df in enumerate(chunk_filter):
               
                s3_path = f"s3://{bucket_name}/raw_data/{s3_folder}/{table_name}_{today}_{i}.parquet"

                wr.s3.to_parquet(
                    df=chunk_df,
                    path=s3_path,
                    index=False
                )
                print(f"Uploaded to:{s3_path}")

        except Exception as e:
            raise ValueError(
                f"Could not read {table_name}. Error: {str(e)}")

    return "Extraction was Successful"
