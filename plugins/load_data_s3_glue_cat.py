import logging

import awswrangler as wr

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_data_s3(
    BUCKET_NAME, DATABASE_NAME, FILE_NAME, year, month, day, df
):  # remember to add database_name,
    """Get data from google sheet and load into s3 in parquet format,  and create glue catalog database and table if not exist, and add the data to the table.
    Args:
        BUCKET_NAME (str): the name of the s3 bucket to store the data
        DATABASE_NAME (str): the name of the glue catalog database to store the data
        FILE_NAME (str): the name of the file to store the data in s3
        year (int): the year of the data
        month (int): the month of the data
        day (int): the day of the data
        df (pandas.DataFrame): the dataframe to be loaded into s3
    Returns:
        None
    """
    wr.catalog.create_database(name=DATABASE_NAME, exist_ok=True)
    wr.s3.to_parquet(
        df=df,
        path=f"s3://{BUCKET_NAME}/year={year}/month={month}/day={day}/{FILE_NAME}.parquet",
        dataset=True,
        database=DATABASE_NAME,
        table=FILE_NAME,
        mode="overwrite_partition",  # Depending on your use case, you might want to use  'append' if you want to replace the existing data in the table.
    )
    logger.info(f"saved: {len(df)} rows into s3 for {FILE_NAME} successfully")
