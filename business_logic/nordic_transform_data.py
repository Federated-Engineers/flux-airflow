import json
import logging

import awswrangler as wr
import boto3
import pandas as pd
from plugins.new_utils.aws import get_ssm_parameter
from plugins.new_utils.write_s3 import write_df_to_s3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

source_bucket = "nrc-logistics-raw"
source_path = "shipcloud-api/"
target_bucket = "new_logistics_bucket"
target_path = "new_data"


access_key = get_ssm_parameter("/staging/flux/aws-access-key")
secret_key = get_ssm_parameter("/staging/flux/aws-access-secret-key")

session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="eu-central-1" 
)
ssm_client = session.client('ssm', region_name="eu-central-1")
response = ssm_client.get_parameter(Name="/staging/flux/aws-access-key", WithDecryption=True)
print(response['Parameter']['Value'])


def transform_json_to_parquet_s3(source_bucket, source_path, target_bucket, target_path):
    """
    Extracts data from a JSON file in an S3 bucket, applies transformations,
    and loads the result as a Parquet file into a target S3 bucket.

    Args:
    source_bucket (str): Name of the source S3 bucket.
    source_path (str): Path to the JSON file in the source bucket.
    target_bucket (str): Name of the target S3 bucket.
    target_path (str): Destination path for the Parquet file in the target bucket.
    
    """
    
    source_path = f's3://{source_bucket}/{source_path}'
    target_path = f's3://{target_bucket}/{target_path}'

    logger.info(f"Reading JSON data from {source_path}...")

    df = wr.s3.read_json(path=source_path)

# Convert string to dict
    df['raw_json_payload'] = df['raw_json_payload'].apply(json.loads)

    # Flatten tracking_events
    df_flat = pd.json_normalize(
        df['raw_json_payload'],
        record_path=['shipping_details', 'tracking_events'],
        meta=[
            ['order_metadata', 'order_id'],
            ['order_metadata', 'warehouse_origin'],
            ['order_metadata', 'warehouse_zone'],
            ['shipping_details', 'carrier'],
            ['shipping_details', 'priority'],
            ['system_flags', 'is_disputed'],
            ['system_flags', 'api_version'],
            ['system_flags', 'ingested_at']
        ],
        sep='_'
    )
    # Rename columns for clarity
    df_flat.rename(columns={
        'order_metadata_order_id': 'order_id',
        'order_metadata_warehouse_origin': 'warehouse_origin',
        'order_metadata_warehouse_zone': 'warehouse_zone',
        'shipping_details_carrier': 'carrier',
        'shipping_details_priority': 'priority',
        'system_flags_is_disputed': 'is_disputed',
        'system_flags_api_version': 'api_version',
        'system_flags_ingested_at': 'ingested_at',
        'event': 'tracking_event',
        'timestamp': 'event_timestamp'
    }, inplace=True)

    #Add ingested_date column for partitioning
    df_flat['ingested_date'] = pd.to_datetime(df_flat['ingested_at']).dt.date


    logger.info(f"Writing Parquet data to {target_path}...")

# Write the DataFrame to the target S3 bucket as a Parquet file
    write_df_to_s3(
        df=df_flat,
        path=target_path,
        index=False,
        partition_cols=['ingested_date', 'warehouse_origin'],
        bucket_name= "new_logistics_bucket",
        folder_name="new_data",
        dataset=True,
        boto3_session="session"
    )    
    logger.info("Successfully converted JSON to Parquet in S3.")