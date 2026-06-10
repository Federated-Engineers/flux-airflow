import logging

import awswrangler as wr
import pandas as pd
from plugins.utils.google_sheet import get_data_from_gsheet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


SHEET_KEY = "1IIr3cYvnT7T7IWMD-naJ-IqghvOgP5aFEybT-7ecO2w"
SSM_PATH = "/production/google-service-account/credentials"


def get_data():
    """
    To fetch the data from the goooglesheet.
    """
    all_data = get_data_from_gsheet(SHEET_KEY, SSM_PATH)
    return all_data


def transform_all_data_to_csv(all_data):
    """
    Takes the already fetched data and returns a DataFrame.
    """
    df = pd.DataFrame(all_data)

    logger.info(f"Successfully transformed {len(df)} records into a DataFrame")

    return df


def load_df_to_s3(df):
    """"
    Load the dataframe to s3 bucket.
    """
    filename = "asset_repair_condition.csv"
    s3_bucket = "alpenmechanik-datalake"
    s3_folder = "asset_repairs"
    s3_pathway = f"{s3_bucket}/{s3_folder}"
    s3_pathway = f"s3://{s3_bucket}/{s3_folder}/{filename}"
    wr.s3.to_csv(
                 df=df,
                 path=s3_pathway,
                 index=False,
                 dataset=False
                )


logger.info("successfully uploaded")


def run_pipeline():
    """
    Extract, transform and load.
    """
    extract = get_data()
    transform = transform_all_data_to_csv(extract)
    load_df_to_s3(transform)


logger.info("Successfull")

if __name__ == "__main__":
    run_pipeline()
