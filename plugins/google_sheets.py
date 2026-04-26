import json
import logging

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from plugins.aws_ssm import get_credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def connect_get_data_from_google_sheet(SHEET_NAME, FILE_PATH):
    """Initialize the connection to google sheet using gspread
    and google service account credentials
    Here we assume that the google credentials are stored in a JSON file
    """
    try:

        SERVICE_ACCOUNT_INFO = json.loads(get_credentials(FILE_PATH))
        credentials = Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO, scopes=SCOPE
        )
        client = gspread.authorize(credentials)
        spreadsheet = client.open(SHEET_NAME)
        worksheets = spreadsheet.worksheets()

        all_sheets_data = []
        for ws in worksheets:
            values = ws.get_all_values()
            if not values or len(values) < 2:
                logger.info(f"sheet {ws.title} is empty")
                continue
            df = pd.DataFrame(values[1:], columns=values[0])
            file_name = ws.title
            all_sheets_data.append({"df": df, "FILE_NAME": file_name})
        logger.info(
            f"""connected successfully into Googlesheet:{SHEET_NAME},
            len: {len(all_sheets_data)}"""
        )
        return all_sheets_data
    except Exception as e:
        logger.error(f"failed to connect to google sheet: {e}")
        raise ConnectionError(f"failed to connect to google sheet: {e}")
