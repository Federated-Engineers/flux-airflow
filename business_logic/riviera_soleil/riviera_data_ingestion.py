from airflow.sdk import Variable

from plugins.aws_ssm import get_credentials
from plugins.date_time import get_date
from plugins.google_setup import connect_get_data_from_google_sheet
from plugins.load_data_s3_glue_cat import load_data_s3


def load_data():
    riviera_config = Variable.get("riviera_properties", deserialize_json=True)

    SHEET_NAME = riviera_config["SHEET_NAME"]
    FILE_PATH = riviera_config["FILE_PATH"]
    BUCKET_NAME = riviera_config["BUCKET_NAME"]
    DATABASE_NAME = riviera_config["DATABASE_NAME"]

    year, month, day = get_date()
    get_credentials(FILE_PATH)
    all_sheets_data = connect_get_data_from_google_sheet(SHEET_NAME, FILE_PATH)
    for sheet_data in all_sheets_data:
        df = sheet_data["df"]
        FILE_NAME = sheet_data["FILE_NAME"]
        load_data_s3(
            BUCKET_NAME, DATABASE_NAME, FILE_NAME, year, month, day, df
        )
    return "Data loaded successfully"
