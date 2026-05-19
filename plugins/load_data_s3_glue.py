import logging

import awswrangler as wr

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_data_to_s3(
    BUCKET_NAME, DATABASE_NAME, TABLE_NAME, year, month, day, df
):  # remember to add database_name,
    """Get data from google sheet and load into s3 in parquet format,
    and create glue catalog database and table if not exist, and add
    the data to the table.
    Args:
        BUCKET_NAME (str): the name of the s3 bucket to store the data
        DATABASE_NAME (str): the name of the glue catalog database to store the
        data
        TABLE_NAME (str): the name of the table to store the data in s3
        year (int): the year of the data
        month (int): the month of the data
        day (int): the day of the data
        df (pandas.DataFrame): the dataframe to be loaded into s3
    Returns:
        None
    """
    wr.s3.to_parquet(
        df=df,
        path=(
            f"s3://{BUCKET_NAME}/{TABLE_NAME}/"
        ),
        database=DATABASE_NAME,
        partition_cols=["year", "month", "day"],
        table=TABLE_NAME,
        dataset=True,
        mode="overwrite_partitions",
    )
    logger.info(f"saved: {len(df)} rows into s3 for {TABLE_NAME} successfully")
