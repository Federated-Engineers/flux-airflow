import logging

import awswrangler as wr
import pandas as pd
from airflow.models import Variable

from plugins.utils.database import get_db_connection

logger = logging.getLogger(__name__)


def extract_lumina_data():
    """
    This function connects to the Lumina brick source database (hosted on Supabase),
    retrieves data from selected tables within the `historical` schema, and writes
    the results to S3 using AWS Wrangler. Tables with date columns are partitioned
    by year and month to optimize downstream analytics and query performance.
    """
    logger.info("Starting Lumnina data extration process")

    engine = get_db_connection(Variable.get("postgres_conn_string"))
    config = Variable.get("lumina_config", deserialize_json=True)

    s3_bucket = config["s3_bucket"]
    s3_prefix = config["s3_prefix"]
    tables = config["tables"]
    partition_columns = config["partition_columns"]

    for table_name in tables:

        logger.info(f"Starting extraction for table: {table_name}")

        query = f"SELECT * FROM historical.{table_name}"
        df = pd.read_sql_query(sql=query, con=engine)

        if table_name in partition_columns:

            date_col = partition_columns[table_name]
            df[date_col] = df[date_col].astype("datetime64[ns]")
            df["year"] = df[date_col].dt.year
            df["month"] = df[date_col].dt.month

            wr.s3.to_parquet(
                df=df,
                path=f"s3://{s3_bucket}/{s3_prefix}/{table_name}/",
                dataset=True,
                mode="overwrite_partitions",
                partition_cols=["year", "month"],
            )
        else:
            wr.s3.to_parquet(
                df=df,
                path=f"s3://{s3_bucket}/{s3_prefix}/{table_name}/",
                dataset=True,
                mode="overwrite",
            )

        logger.info(f"Finished loading {table_name} into {s3_bucket}")

    logger.info("Lumina data extraction completed")  # ← F541: removed f-string, no placeholder

    return "Extraction Sucessful"