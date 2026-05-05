"""
Fetch finance DataWH classification data from Google Sheets.
"""
import json
import logging

import awswrangler as wr
import pandas as pd
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.google.suite.hooks.sheets import GSheetsHook

logger = logging.getLogger(__name__)


def get_finance_classification_data(**context):
    """
    This function performs the following steps:
    1. Retrieves the execution date from Airflow context.
    2. Initializes a GSheetsHook for secure authentication.
    3. Fetches the Google Sheets file ID from Airflow Variables.
    4. Reads the classification sheet of the specified Google Sheets file.
    5. Converts the sheet data into a Pandas DataFrame.
    6. Adds an execution date column.
    7. Writes the DataFrame to S3 in Parquet format using awswrangler
    """
    try:
        execution_date = context['ds'].replace('-', '')
        logger.info(f"Execution date: {execution_date}")

        # Initialize hook for secure authentication
        gsheets_hook = GSheetsHook(gcp_conn_id='google_cloud_default')
        
        # Get file ID from Airflow Variables
        #finance_file_id = "1z9eoQjhiuFG5-tpU3Ty0Blg0X_8Nqtx_RpG1lbGIrks"
        finance_file_id = Variable.get('FINANCE_CLASSIFICATION_DATAWH_FILE_ID', default_var=None)
        
        if not finance_file_id:
            raise ValueError("Missing required Airflow variable: FINANCE_CLASSIFICATION_DATAWH_FILE_ID")
        
        logger.info(f"Fetching finance classification data from file ID: {finance_file_id}")
        
        # Get sheet metadata
        spreadsheet = gsheets_hook.get_spreadsheet(spreadsheet_id=finance_file_id)
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        # Find classification sheet
        class_sheet = next(
            (name for name in sheet_names if 'classification' in name.lower()),
            sheet_names[1] if len(sheet_names) > 1 else sheet_names[0]
        )
        logger.info(f"Reading classification from sheet: {class_sheet}")
        
        # Get values from sheet
        values = gsheets_hook.get_values(
            spreadsheet_id=finance_file_id,
            range_=class_sheet
        )
        
        if not values:
            logger.warning("No data found for finance classification data")
            return json.dumps({"status": "empty", "data": None})
        
        # Convert to DataFrame
        headers = values[0]
        data_rows = values[1:]
        
        # Handle row padding if columns are missing in some rows
        max_cols = len(headers)
        for row in data_rows:
            if len(row) < max_cols:
                row.extend([''] * (max_cols - len(row)))
            elif len(row) > max_cols:
                row[:] = row[:max_cols]
        
        finance_dataWH_classificationdata_df = pd.DataFrame(data_rows, columns=headers)
        logger.info(f"Finance classification data loaded: {len(finance_dataWH_classificationdata_df)} rows")
        
        # Add execution date for partitioning
        finance_dataWH_classificationdata_df['date'] = execution_date
        logger.info("Added execution date for partitioning")
        
        # Initialize S3 session using Airflow connection
        s3_hook = S3Hook(aws_conn_id='aws_cloud')
        aws_session = s3_hook.get_session()

        # Force 'python' engine to allow passing boto3_session and avoid Ray issues
        wr.engine.set("python")
        wr.memory_format.set("pandas")

        
        path = Variable.get("FINANCE_CLASSIFICATION_DATAWH_PATH")
        # path2 = f"s3://athena-test-bucket-2026/finance_dataWH/classificationdata/classificationdata.parquet" 
        
        wr.s3.to_parquet(finance_dataWH_classificationdata_df, path, 
                         dataset=True, 
                         mode="overwrite",
                         boto3_session=aws_session)
    
    except Exception as e:
        logger.error(f"Error reading finance classification data: {str(e)}")
        raise
