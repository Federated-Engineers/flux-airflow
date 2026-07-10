import hashlib
import logging

import awswrangler as wr
from airflow.models import Variable

from plugins.google_sheets import connect_get_data_from_google_sheet

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
        data = connect_get_data_from_google_sheet(
            SHEET_NAME=CONFIG["SHEET_KEY"],
            FILE_PATH=CONFIG["SSM_PATH"]
        )

        if not data:
            raise ValueError("Google Sheet returned no data")

        # Transformation
        df = data[0]["df"]

        logger.info("Successfully extracted %s records", len(df))

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

        new_hash = generate_dataframe_hash(df)

        logger.info("Data hash: %s", new_hash)

        # Get metadata
        metadata = wr.s3.describe_objects(s3_path)\
            .get(s3_path, {})\
            .get("Metadata", {})
        if metadata.get("data-hash") == new_hash:
            logger.info("Data hash matches S3 metadata. Skip upload.")
            return s3_path

        # Upload file with the new hash stored in S3 metadata
        logger.info("Data changed, uploading file to %s", s3_path)
        wr.s3.to_csv(
            df=df,
            path=s3_path,
            index=False,
            dataset=False,
            s3_additional_kwargs={"Metadata": {"data-hash": new_hash}}
        )
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
