import datetime
import logging
#import boto3
#import awswrangler as wr
import gspread
import pandas as pd
#from airflow.sdk import Variable
from google.oauth2.service_account import Credentials
import json



BUCKET = "riviera_bucket" # temporal name for the bucket, to be replaced with the actual bucket name in production
SHEET_NAME = Variable.get("SHEET_NAME")


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_credentials(param_name):
    """ Get credentials from AWS ssm 
        - param_name: the name of the parameter in ssm to retrieve the credentials for google service account
        Args:
        Returns:
        The parameter value as a string
        Raise:
        connectionError: if there is an issue connecting to AWS SSM
    """
    try:
        ssm = boto3.client('ssm' )
        response = ssm.get_parameter(
        Name=param_name,
        WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"failed to get credentials for {param_name}: {e}")
        raise ConnectionError(f"failed to get credentials for {param_name}: {e}")

# get last row count
def get_last_rowcount(file_name:str):
    """ Getting the row count from s3 path for tracking folder 
    """
    track_path = f"s3://{BUCKET}/tracking/{file_name}_row_count.parquet"
    try:
        row_track = wr.s3.read_parquet(track_path)
        count = int(row_track['row_count'].iloc[0])
        return count
    except Exception as e:
        logger.warning(f"no row count found for {file_name} ")
        return 0
    

# Module for the date partitioning in s3

def get_date():
    """ Get current date for partitioning in s3
    """
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return year, month, day

# save row count
def save_row_count(file_name:str, row_count):
    """ Save current row into s3 for tracking
    """
    try:
        df_track = pd.DataFrame({"row_count":[row_count]})
        wr.s3.to_parquet(
            df= df_track, 
            path = f"s3://{BUCKET}/tracking/{file_name}_row_count.parquet",
            index = False)
        logger.info(f"row count updated for {file_name}:{row_count}")
    except Exception as e:
        logger.error(f"failed to save row count for {file_name}:{e}")
        raise Exception(f"failed to save row count for {file_name}:{e}")

# Module to initialize the connection to google sheet

def connect_to_google_sheet():
    """ Initialize the connection to google sheet using gspread and google service account credentials
    """
    try:
        SERVICE_ACCOUNT_INFO  = json.loads(get_credentials("/production/google-service-account/credentials"))
        credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPE)
        client = gspread.authorize(credentials)
        spreadsheet = client.open(SHEET_NAME)
        logger.info(f"connected successfully into Googlesheet:{SHEET_NAME}")
        return spreadsheet
    except Exception as e:
        logger.error(f"failed to connect to google sheet: {e}")
        raise ConnectionError(f"failed to connect to google sheet: {e}")

def get_load_data():
    """ Get data from google sheet and load into s3 in parquet format, 
        also track the row count for each sheet to avoid duplicate loading   
    """
    try:
        spreadsheet = connect_to_google_sheet()
        worksheets = spreadsheet.worksheets()[1:]
        logger.info(f"total sheets found: {len(worksheets)}")
        for ws in worksheets:
            values= ws.get_all_values()
            if not values:
                logger.info("No data found")
                continue
        
            df = pd.DataFrame(values[1:], columns = values[0])
            file_name = ws.title
            current_row_count = len(df)
            last_row_count = get_last_rowcount(file_name)

            if current_row_count > last_row_count:
                logger.info(f"new data found for {file_name}. Current row count: {current_row_count}, Last row count: {last_row_count}")
                date = get_date()
                year = date["year"]
                month = date["month"]
                day = date["day"]

                new_data = df.iloc[last_row_count:]
                logger.info(f"new data to be loaded for {file_name}: {len(new_data)} rows") 
                wr.catalog.create_database(name='riviera_db', exist_ok=True)   
                wr.s3.to_parquet(
                    df=new_data,
                    path=f"s3://{BUCKET}/year={year}/month={month}/day={day}/{file_name}/",
                    dataset=True,
                    database="riviera_db",
                    table= file_name,
                    mode = 'append'
               )
                logger.info(f"saved: {file_name}")
                save_row_count(file_name, current_row_count)
            else:
                logger.info(f"No new data found for {file_name}. Current row count: {current_row_count}, Last row count: {last_row_count}")
    except Exception as e:
        logger.error(f"failed to load data due to {e}")
        raise Exception(f"failed to load data due to {e}")




if __name__ == "__main__":
  get_load_data()