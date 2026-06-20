import json
import logging

import gspread
from google.oauth2.service_account import Credentials

from plugins.utils.aws import get_ssm_parameter

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"]


def get_google_sheets_client(ssm_path: str):
    """
    Authenticate with Google Sheets using credentials stored in AWS SSM.

    Args:
        ssm_path: The SSM parameter path where the Google service
        account credentials are stored.
    """

    credentials_dict = json.loads(get_ssm_parameter(ssm_path))

    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=SCOPES,
    )

    logger.info("Google Sheets authentication successful")
    return gspread.authorize(credentials)


def get_data_from_gsheet(gsheet_id: str, ssm_path: str,
                         sheet_name: str = None):
    """Ingest all records from the first worksheet of a Google Sheet.

    Args:
        gsheet_id: The Google Sheet ID/key.
        ssm_path: The SSM parameter path where the Google service account
        credentials are stored.
    Returns:
        A list of records from the sheet.
    """

    logger.info("Starting data ingestion from Google Sheet")

    gc = get_google_sheets_client(ssm_path)
    workbook = gc.open_by_key(gsheet_id)

    if sheet_name:
        worksheet = workbook.worksheet(sheet_name)
    else:
        worksheet = workbook.sheet1

    data = worksheet.get_all_records()
    logger.info("Data ingestion completed")

    return data
