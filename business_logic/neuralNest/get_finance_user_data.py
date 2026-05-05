"""
Fetch finance DataWH user data from Google Sheets.
"""

import json
import logging

import awswrangler as wr
import pandas as pd
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.google.suite.hooks.sheets import GSheetsHook

logger = logging.getLogger(__name__)


def _get_finance_user_data(**context):
    """
    This function performs the following steps:
    1. Retrieves the execution date from Airflow context.
    2. Initializes a GSheetsHook for secure authentication.
    3. Fetches the Google Sheets file ID from Airflow Variables.
    4. Reads the user data sheet of the specified Google Sheets file.
    5. Converts the sheet data into a Pandas DataFrame.
    6. Adds an execution date column.
    7. Writes the DataFrame to S3 in Parquet format using awswrangler
    """
    try:
        # Get execution date for partitioning (YYYYMMDD format)
        execution_date = context["ds"].replace("-", "")
        logger.info(f"Execution date: {execution_date}")

        # Initialize hook for secure authentication
        gsheets_hook = GSheetsHook(gcp_conn_id="google_cloud_default")

        # Get file ID from Airflow Variables.
        finance_file_id = Variable.get(
            "FINANCE_USER_DATAWH_FILE_ID", default_var=None)

        if not finance_file_id:
            raise ValueError("Missing variable: FINANCE_USER_DATAWH_FILE_ID")

        logger.info(
            f"Fetching user data from file ID: {finance_file_id}")

        # Get sheet metadata to find correct sheet name
        spreadsheet = gsheets_hook.get_spreadsheet(
            spreadsheet_id=finance_file_id)
        sheet_names = [sheet["properties"]["title"]
                       for sheet in spreadsheet["sheets"]]
        logger.info(f"Available sheets: {sheet_names}")

        # Find user_data sheet
        user_sheet = next(
            (
                name
                for name in sheet_names
                if "user" in name.lower() or "data" in name.lower()
            ),
            sheet_names[0],
        )
        logger.info(f"Reading from sheet: {user_sheet}")

        # Get values from sheet
        values = gsheets_hook.get_values(
            spreadsheet_id=finance_file_id, range_=user_sheet
        )

        if not values:
            logger.warning("No data found for finance user data")
            return json.dumps({"status": "empty", "data": None})

        # Convert to DataFrame
        headers = values[0]
        data_rows = values[1:]

        # Handle row padding if columns are missing in some rows
        max_cols = len(headers)
        for row in data_rows:
            if len(row) < max_cols:
                row.extend([""] * (max_cols - len(row)))
            elif len(row) > max_cols:
                row[:] = row[:max_cols]

        finance_userdata_df = pd.DataFrame(data_rows, columns=headers)

        # Add execution date for partitioning
        finance_userdata_df["date"] = execution_date
        logger.info(
            f"Finance user data loaded: {len(finance_userdata_df)} rows")

        # Initialize S3 session using Airflow connection
        s3_hook = S3Hook(aws_conn_id="aws_cloud")
        aws_session = s3_hook.get_session()

        path = Variable.get("FINANCE_USER_DATAWH_PATH")

        wr.engine.set("python")
        wr.memory_format.set("pandas")

        wr.s3.to_parquet(
            finance_userdata_df,
            path,
            dataset=True,
            mode="overwrite",
            # partition_cols=["date"],
            boto3_session=aws_session,
        )

    except Exception as e:
        logger.error(f"Error reading finance user data: {str(e)}")
        raise
