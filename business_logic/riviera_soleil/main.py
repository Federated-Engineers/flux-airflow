import awswrangler as wr
import pandas as pd
import datetime
import gspread
from airflow.sdk import Variable
import logging


today =  datetime.date.today()
year = today.year
month = today.month
day = today.day
BUCKET = "riviera_bucket"
SHEET_NAME = Variable.get("SHEET_NAME")
SERVICE_ACCOUNT_FILE = Variable.get("SERVICE_ACCOUNT_FILE")

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# get last row count

def get_last_rowcount(file_name:str):
    """ Getting the row count from s3 path for tracking folder 
    """
    track_path = f"s3://{BUCKET}/tracking/{file_name}_row_count.csv"
    try:
        row_track = wr.s3.read_csv(track_path)
        count = int(row_track['row_count'].iloc[0])
        return count
    except Exception as e:
        logger.warning(f"no row count found for {file_name} ")
        return 0



def save_row_count(file_name:str, row_count):
    """ Save current row into s3 for tracking
    """
    try:
        df_track = pd.DataFrame({"row_count":[row_count]})
        wr.s3.to_csv(
            df= df_track, 
            path = f"s3://{BUCKET}/tracking/{file_name}_row_count.csv",
            index = False)
        logger.info(f"row count updated for {file_name}:{row_count}")
    except Exception as e:
        logger.error(f"failed to save row count for {file_name}:{e}")
        raise


def get_load_data():
    """ Get data from google sheet and load into s3 in parquet format, 
        also track the row count for each sheet to avoid duplicate loading   
    """
    try:
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
        client = gspread.authorize(credentials)
        spreadsheet = client.open(SHEET_NAME)
        worksheets = spreadsheet.worksheets()[1:]
        logger.info(f"connected successfully into Googlesheet:{SHEET_NAME}")
        logger.info(f"total sheets found: {len(worksheets)}")
        for ws in worksheets:
            values= ws.get_all_values()
            if not values:
                logger.info("No data found")
                continue
        
            df = pd.DataFrame(values[1:], columns = values[0])
            file_name = ws.title
            csv_file = f"{file_name}.csv"
            current_row_count = len(df)
            last_row_count = get_last_rowcount(file_name)

            if current_row_count <= last_row_count:
                logger.info(f"new data found for {file_name}. Current row count: {current_row_count}, Last row count: {last_row_count}")
                continue

            df.to_csv(csv_file, index=False)
        
        wr.catalog.create_database(name='riviera_db', exist_ok=True)   
        wr.s3.to_parquet(
                    df=df,
                    path=f"s3://{BUCKET}/year={year}/month={month}/day={day}/{file_name}",
                    dataset=True,
                    database="riviera_db",
                    table= file_name,
                    mode = 'append'
               )
        logger.info(f"saved: {file_name}")
        save_row_count(file_name, current_row_count)
        
    except Exception as e:
        logger.error(f"failed to load data due to {e}")
        raise




if __name__ == "__main__":
    get_load_data()