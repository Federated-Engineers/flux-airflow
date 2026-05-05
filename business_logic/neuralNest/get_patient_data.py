"""
Fetch patient hospital visit data from Google Sheets.
"""
import io
import logging

import awswrangler as wr
import pandas as pd
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.google.suite.hooks.drive import GoogleDriveHook

logger = logging.getLogger(__name__)


def _get_patient_hospital_visit_data(**context):
    """
    This function performs the following steps:
    1. Retrieves the execution date from Airflow context.
    2. Initializes a GoogleDriveHook for secure authentication.
    3. Fetches the Google Sheets file ID from Airflow Variables.
    4. Reads the first sheet of the specified Google Sheets file.
    5. Converts the sheet data into a Pandas DataFrame.
    6. Adds an execution date column for partitioning.
    7. Writes the DataFrame to S3 in Parquet format using awswrangler
    """
    try:
        # Get execution date for partitioning (YYYYMMDD format) 
        execution_date = context['ds'].replace('-', '')
        logger.info(f"Execution date: {execution_date}")
        
        # Initialize hook for Google Drive since the source is a CSV file
        drive_hook = GoogleDriveHook(gcp_conn_id='google_cloud_default')

        # Get file ID from Airflow Variables
              
        patient_file_id = "13nkQlxiSfQmz6ibjFP5H9se6rXL4wxcV"
        #patient_file_id = Variable.get('PATIENT_HOSPITAL_VISIT_FILE_ID', default_var=None)
        
        if not patient_file_id:
            raise ValueError("Missing required Airflow variable: PATIENT_HOSPITAL_VISIT_FILE_ID")
        
        patient_file_id = patient_file_id.strip()
        logger.info(f"Downloading CSV from Google Drive, file ID: {patient_file_id}")
        
        # Download the file content into a memory buffer
        file_handle = io.BytesIO()
        drive_hook.download_file(file_id=patient_file_id, file_handle=file_handle)
        
        # Load buffer directly into DataFrame
        file_handle.seek(0)  # Reset the file pointer to the beginning, read the data from the start
        patient_hospital_visit_df = pd.read_csv(file_handle)
        
        # Add execution date for partitioning
        patient_hospital_visit_df['date'] = execution_date
        logger.info(f"Patient hospital visit data loaded: {len(patient_hospital_visit_df)} rows")
        
        # Get S3 hook to retrieve AWS credentials from Airflow connection
        s3_hook = S3Hook(aws_conn_id='aws_cloud')
        aws_session = s3_hook.get_session()
        
        #path = f"s3://athena-test-bucket-2026/patient_hospital_visit/patient_hospital_visit.parquet"
        path = Variable.get("PATIENT_HOSPITAL_VISIT_DATAWH_PATH")
        
        # Force 'python' engine to allow passing boto3_session and avoid Ray serialization issues
        wr.engine.set("python")
        wr.memory_format.set("pandas")
        
        wr.s3.to_parquet(patient_hospital_visit_df, path, 
                         dataset=True, 
                         mode="overwrite", 
                         partition_cols=["date"],
                         boto3_session=aws_session)
    
    except Exception as e:
        logger.error(f"Error reading patient hospital visit data: {str(e)}")
        raise
