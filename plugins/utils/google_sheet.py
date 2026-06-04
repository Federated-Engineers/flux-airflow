import json
import logging

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from plugins.utils.aws import get_ssm_parameter

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_google_sheets_client(ssm_path: str):
    """
    Authenticate to Google Sheets using credentials
    stored in AWS SSM Parameter Store.
    """

    try:
        credentials_dict = json.loads(
            get_ssm_parameter(ssm_path)
        )

        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=SCOPES,
        )

        logger.info("Google Sheets authentication successful")

        return gspread.authorize(credentials)

    except Exception:
        logger.exception(
            "Failed to authenticate with Google Sheets"
        )
        raise


def get_data_from_gsheet(gsheet_id: str, ssm_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Extract data from a specific Google Sheet worksheet
    and return it as a pandas DataFrame.

    Args:
        gsheet_id:
            Google Spreadsheet ID

        ssm_path:
            SSM parameter containing service account JSON

        sheet_name:
            Worksheet/tab name

    Returns:
        pandas.DataFrame
    """

    logger.info(
        "Starting extraction from sheet '%s'",
        sheet_name,
    )

    gc = get_google_sheets_client(ssm_path)

    try:
        workbook = gc.open_by_key(gsheet_id)

        worksheet = workbook.worksheet(sheet_name)

        records = worksheet.get_all_records()

        df = pd.DataFrame(records)

        logger.info(
            "Successfully extracted %s rows and %s columns from '%s'",
            len(df),
            len(df.columns),
            sheet_name,
        )

        return df

    except gspread.WorksheetNotFound:
        logger.exception(
            "Worksheet '%s' does not exist",
            sheet_name,
        )
        raise

    except Exception:
        logger.exception(
            "Failed extracting data from '%s'",
            sheet_name,
        )
        raise
