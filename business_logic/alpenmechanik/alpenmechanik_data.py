import hashlib
import logging

import awswrangler as wr
from airflow.models import Variable

from plugins.current_date import get_current_day_month_year
from plugins.google_sheets import connect_get_data_from_google_sheet

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CONFIG = Variable.get("asset_repairs_config", deserialize_json=True)
upload_date = get_current_day_month_year()


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
    Upload dataframe to S3 while preserving a chronological file history.
    Only skips uploads if data matches the most recent historical snapshot.
    """
    # Convert the dictionary into a clean string (YYYY-MM-DD)
    formatted_date = (
                        f"{upload_date['year']}-"
                        f"{upload_date['month']:02d}-"
                        f"{upload_date['day']:02d}"
    )
    # Define the base directory path in S3
    base_prefix_path = (
                        f"s3://{CONFIG['S3_BUCKET_NAME']}/"
                        f"{CONFIG['S3_PREFIX']}/"
    )
    try:
        # Unique file path for the incoming run
        new_s3_path = (
                        f"{base_prefix_path}"
                        f"{formatted_date}_{CONFIG['FILENAME']}"
        )
        new_hash = generate_dataframe_hash(df)
        logger.info("Data hash: %s", new_hash)

        # Safely attempt to fetch objects under the prefix folder
        objects_meta_list = wr.s3.list_objects(path=base_prefix_path)

        # If files exist, find the latest snapshot to check against
        if objects_meta_list:
            all_objects_meta = wr.s3.describe_objects(path=base_prefix_path)
            sorted_history_paths = sorted(all_objects_meta.keys())
            latest_historical_file = sorted_history_paths[-1]
            logger.info("Comparing hash against latest history snapshot: %s",
                        latest_historical_file,
                        )
            # Pull hash metadata from that specific historical data file
            metadata = (
                all_objects_meta[latest_historical_file].get("Metadata", {})
            )
            # Skip if the content matches your latest historical version
            if metadata.get("data-hash") == new_hash:
                logger.info("Data hash matches latest history file."
                            "Skip upload to preserve storage.")
                # RETURN FALSE: Path found, but NO new upload happened
                return latest_historical_file, False

        # Data changed,
        # Upload a new file to maintain full historical records
        logger.info("Data changed or first run."
                    "Uploading historical file to %s",
                    new_s3_path,
                    )
        wr.s3.to_csv(
            df=df,
            path=new_s3_path,
            index=False,
            dataset=False,
            s3_additional_kwargs={"Metadata": {"data-hash": new_hash}}
        )
    except Exception:
        logger.info("Successfully uploaded historical data to %s", new_s3_path)

    # RETURN TRUE: A new history file was actually uploaded
    return new_s3_path, True


def run_pipeline():
    """
    ETL workflow.
    """
    try:
        logger.info("Starting asset repair ETL pipeline")

        df = get_and_transform_data()
        # Unpack both the path and the action flag
        s3_path, was_uploaded = load_to_s3(df)

        if was_uploaded:
            logger.info("Pipeline completed successfully -"
                        "New historical data saved.")
            return {
                "status": "success_uploaded",
                "records": len(df),
                "s3_path": s3_path,
                "data_changed": True
            }
        # If it wasn't uploaded, log the specific skipped message explicitly
        logger.info("Pipeline completed -"
                    "No data changes detected. Upload skipped.")
        return {
            "status": "success_skipped",
            "records": len(df),
            "s3_path": s3_path,
            "data_changed": False
        }
    except Exception:
        logger.exception("Pipeline execution failed")
        raise


# Execute the pipeline
run_pipeline()
