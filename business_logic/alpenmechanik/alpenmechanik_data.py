import hashlib
import logging
import os

import awswrangler as wr
import pandas as pd

from plugins.utils.google_sheet import get_data_from_gsheet

logger = logging.getLogger()
logger.setLevel(logging.INFO)


SHEET_KEY = os.environ["SHEET_KEY"]
SSM_PATH = os.environ["SSM_PATH"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

S3_PREFIX = "asset_repairs"
FILENAME = "asset_repair_condition.csv"


def get_data():
    """
    Extract data from Google Sheet.
    """

    try:
        logger.info("Fetching data from Google Sheet")

        data = get_data_from_gsheet(
            sheet_key=SHEET_KEY,
            ssm_path=SSM_PATH)

        if not data:
            raise ValueError("Google Sheet returned no data")

        logger.info("Successfully extracted %s records", len(data))

        return data
    except Exception:
        logger.exception("Failed to extract data from Google Sheet")
        raise


def transform_data(data):
    """
    Convert extracted data to DataFrame.
    """

    try:
        if data is None:
            raise ValueError("Input data is None")
        df = pd.DataFrame(data)

        if df.empty:
            raise ValueError("Generated DataFrame is empty")

        logger.info(
            "Transformed %s rows",
            len(df))

        return df

    except Exception:
        logger.exception(
            "Failed during data transformation")
        raise


def generate_dataframe_hash(df):
    """
    Generate deterministic hash for change detection.
    """

    try:
        csv_string = df.to_csv(index=False)

        return hashlib.md5(csv_string.encode("utf-8")).hexdigest()

    except Exception:
        logger.exception("Failed to generate dataframe hash")
        raise


def load_to_s3(df):
    """
    Upload dataframe to S3.
    """

    try:
        s3_path = (
            f"s3://{S3_BUCKET_NAME}/"
            f"{S3_PREFIX}/{FILENAME}"
        )

        data_hash = generate_dataframe_hash(df)

        logger.info("Data hash: %s", data_hash)

        logger.info("Uploading file to %s", s3_path)

        wr.s3.to_csv(
            df=df,
            path=s3_path,
            index=False,
            dataset=False)

        logger.info("Successfully uploaded to %s", s3_path)

        return s3_path

    except Exception:
        logger.exception("Failed to upload dataframe to S3")
        raise


def run_pipeline():
    """
    ETL workflow.
    """

    try:
        logger.info("Starting asset repair ETL pipeline")

        data = get_data()
        df = transform_data(data)
        s3_path = load_to_s3(df)

        logger.info("Pipeline completed successfully")

        return {
            "status": "success",
            "records": len(df),
            "s3_path": s3_path
        }
    except Exception:
        logger.exception("Pipeline execution failed")
        raise


if __name__ == "__main__":
    run_pipeline()