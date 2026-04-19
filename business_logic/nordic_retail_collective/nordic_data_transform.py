import json
import logging

import awswrangler as wr
import pandas as pd
from plugins.utils.aws_utils import new_session

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

source_bucket = "nrc-logistics-raw"
source_path = "shipcloud-api/"
target_bucket = "federated-engineers-production-flux-data-engineers-nordic"
target_path = "nordic_logistics"

def transform_json_to_parquet_s3(source_bucket,
                                 source_path, target_bucket, target_path):

    """
        This function reads data from an S3 bucket as JSON,
        transforming it, and write the output
        back to a new S3 bucket as parquet.

        Parameters:
        source_bucket (str): Name of the source S3 bucket.
        source_path (str): Path/key to the JSON data in the source bucket.
        target_bucket (str): Name of the destination S3 bucket.
        target_path (str): Path/key where the Parquet file will be saved.
    """
    source_path = f's3://{source_bucket}/{source_path}'
    target_path = f's3://{target_bucket}/{target_path}'

    logger.info(f"Reading JSON data from {source_path}...")
    df = wr.s3.read_json(path=source_path, lines=True)
    df['raw_json_payload'] = df['raw_json_payload'].apply(json.loads)
    df_flat_transformed = pd.json_normalize(df['raw_json_payload'])
    df_flat_transformed = pd.DataFrame(df_flat_transformed)

    df_flat_transformed = df_flat_transformed.rename(columns={
        'order_metadata.order_id': 'order_id',
        'order_metadata.warehouse_origin': 'warehouse_origin',
        'order_metadata.warehouse_zone': 'warehouse_zone',
        'shipping_details.carrier': 'carrier',
        'shipping_details.priority': 'priority',
        'shipping_details.tracking_events': 'tracking_events',
        'system_flags.is_disputed': 'is_disputed',
        'system_flags.api_version': 'api_version',
        'system_flags.ingested_at': 'ingested_at'}
    )
    df_flat_transformed = df_flat_transformed.drop(columns=['tracking_events'])
    dt_series = pd.to_datetime(df_flat_transformed['ingested_at'])
    df_flat_transformed['ingested_date'] = dt_series.dt.date
    df_flat_transformed['ingested_year'] = dt_series.dt.year
    df_flat_transformed['ingested_month'] = dt_series.dt.month
    df_flat_transformed['ingested_day'] = dt_series.dt.day
    logger.info(f"Writing Parquet data to {target_path}...")
    
    wr.s3.to_parquet(
        df=df_flat_transformed,
        path=target_path,
        index=False,
        partition_cols=['ingested_year', 'ingested_month', 'ingested_day'],
        dataset=True
        )
    logger.info("Successfully converted JSON to Parquet in S3.")


if __name__ == "__main__":
    transform_json_to_parquet_s3(source_bucket,
                                 source_path, target_bucket, target_path)
