from airflow.sdk import Variable

from plugins.aws import get_ssm_parameter
from plugins.current_date import get_current_day_month_year
from plugins.google_sheets import connect_get_data_from_google_sheet
from plugins.load_data_s3_glue import load_data_to_s3


def ingest_riviera_data_into_s3():
    riviera_config = Variable.get("riviera_properties", deserialize_json=True)

    SHEET_NAME = riviera_config["SHEET_NAME"]
    FILE_PATH = riviera_config["FILE_PATH"]
    BUCKET_NAME = riviera_config["BUCKET_NAME"]
    DATABASE_NAME = riviera_config["DATABASE_NAME"]

    get_ssm_parameter(FILE_PATH)
    all_sheets_data = connect_get_data_from_google_sheet(SHEET_NAME, FILE_PATH)
    for sheet_data in all_sheets_data:
        df = sheet_data["df"]
        dt = get_current_day_month_year()
        df['year'] = dt['year']
        df['month'] = dt['month']
        df['day'] = dt['day']
        TABLE_NAME = sheet_data["FILE_NAME"]
        load_data_to_s3(
            BUCKET_NAME, DATABASE_NAME, TABLE_NAME,
            dt['year'], dt['month'], dt['day'], df
        )
    return "Data loaded successfully"
