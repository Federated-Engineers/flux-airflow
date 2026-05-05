"""
Fetch eHealth DataWH data from Google Sheets.
"""
import json
import logging

import awswrangler as wr
import pandas as pd
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.google.suite.hooks.sheets import GSheetsHook

logger = logging.getLogger(__name__)


def get_ehealth_data(**context):
    """
    This function performs the following steps:
    1. Retrieves the execution date from Airflow context.
    2. Initializes a GSheetsHook for secure authentication.
    3. Fetches the Google Sheets file ID from Airflow Variables.
    4. Reads the first sheet of the specified Google Sheets file.
    5. Converts the sheet data into a Pandas DataFrame.
    6. Adds an execution date column.
    7. Writes the DataFrame to S3 in Parquet format using awswrangler
        
    """
    try:
        execution_date = context['ds'].replace('-', '')
        logger.info(f"Execution date: {execution_date}")
        
        # Initialize hook for secure authentication with Google Sheets API
        gsheets_hook = GSheetsHook(gcp_conn_id='google_cloud_default')
        
        # Get file ID from Airflow Variables
        ehealth_file_id = Variable.get('EHEALTH_DATAWH_FILE_ID', default_var=None)
        ## ehealth_file_id = "1m63-lbh-4JgAAu2kPB530-I5lUFRwPsccnneJaThNh8"
        
        if not ehealth_file_id:
            raise ValueError("Missing required Airflow variable: EHEALTH_DATAWH_FILE_ID")
        
        logger.info(f"Fetching eHealth data from file ID: {ehealth_file_id}")
        
        # Get sheet metadata and values using a managed hook
        spreadsheet = gsheets_hook.get_spreadsheet(spreadsheet_id=ehealth_file_id)
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        logger.info(f"Available sheets in ehealth: {sheet_names}")
        
        # Read first sheet
        sheet_name = sheet_names[0]
        logger.info(f"Reading from sheet: {sheet_name}")
        
        # Get values from sheet
        values = gsheets_hook.get_values(
            spreadsheet_id=ehealth_file_id,
            range_=sheet_name
        )
        
        if not values:
            logger.warning("No data found for ehealth data")
            return json.dumps({"status": "empty", "data": None})
        
        # Convert to DataFrame
        headers = values[0]
        data_rows = values[1:]
        
        # Handle column mismatch
        max_cols = len(headers)
        for row in data_rows:
            if len(row) < max_cols:
                row.extend([''] * (max_cols - len(row)))
            elif len(row) > max_cols:
                row[:] = row[:max_cols]
        
        ehealth_dataWH_df = pd.DataFrame(data_rows, columns=headers)
        logger.info(f"eHealth data loaded: {len(ehealth_dataWH_df)} rows")
        
        # Add execution date
        ehealth_dataWH_df['date'] = execution_date  
        logger.info("Added execution date for partitioning")
        logger.info(f"eHealth data loaded: {len(ehealth_dataWH_df)} rows")
        
        # Initialize S3 session using Airflow connection
        s3_hook = S3Hook(aws_conn_id='aws_cloud')
        aws_session = s3_hook.get_session()

        # Force 'python' engine to allow passing boto3_session and avoid Ray issues
        wr.engine.set("python")
        wr.memory_format.set("pandas")
        
        ehealth_s3_path = f"s3://athena-test-bucket-2026/ehealth_dataWH/ehealth_dataWH.parquet" 
        
        wr.s3.to_parquet(ehealth_dataWH_df, ehealth_s3_path, 
                         dataset=True, 
                         mode="overwrite", 
                         boto3_session=aws_session)
    
    except Exception as e:
        logger.error(f"Error reading ehealth data: {str(e)}")
        raise
