import hashlib
import logging

import awswrangler as wr
import pandas as pd
from airflow.models import Variable
from plugins.utils.google_sheet import get_data_from_gsheet

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CONFIG = Variable.get("asset_repairs_config", deserialize_json=True)


def get_and_transform_data():
    """
    Extract data from Google Sheet and transform it into a pandas DataFrame.
    """

    try:
        logger.info("Fetching data from Google Sheet")

        # Extraction
        data = get_data_from_gsheet(
            gsheet_id=CONFIG["SHEET_KEY"],
            ssm_path=CONFIG["SSM_PATH"]
        )

        if not data:
            raise ValueError("Google Sheet returned no data")

        logger.info("Successfully extracted %s records", len(data))

        # Transformation
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
            f"s3://{CONFIG['S3_BUCKET_NAME']}/"
            f"{CONFIG['S3_PREFIX']}/{CONFIG['FILENAME']}"
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

        df = get_and_transform_data()
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


# Execute the pipeline
run_pipeline()
