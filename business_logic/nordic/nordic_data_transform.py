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
target_bucket = "federated-flux-staging-bucket" 
target_path = "nordic_logistics"

session = new_session()
     
source_path = f's3://{source_bucket}/{source_path}'
target_path = f's3://{target_bucket}/{target_path}'

logger.info(f"Reading JSON data from {source_path}...")

df = wr.s3.read_json(path=source_path, lines=True)    
df['raw_json_payload'] = df['raw_json_payload'].apply(json.loads)
df_flat_transformed= pd.json_normalize(df['raw_json_payload'])
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
    'system_flags.ingested_at': 'ingested_at',
},    )
df_flat_transformed= df_flat_transformed.drop(columns=['tracking_events'])

df_flat_transformed['ingested_date'] = pd.to_datetime(df_flat_transformed['ingested_at']).dt.date
df_flat_transformed['ingested_year'] = pd.to_datetime(df_flat_transformed['ingested_date']).dt.year
df_flat_transformed['ingested_month'] = pd.to_datetime(df_flat_transformed['ingested_date']).dt.month
df_flat_transformed['ingested_day'] = pd.to_datetime(df_flat_transformed['ingested_date']).dt.day

logger.info(f"Writing Parquet data to {target_path}...")

wr.s3.to_parquet(
        df=df_flat_transformed,
        path=target_path,
        index=False,
        partition_cols=['ingested_year', 'ingested_month', 'ingested_day', 'warehouse_origin'],
        dataset=True,
        boto3_session=session
    )
logger.info("Successfully converted JSON to Parquet in S3.")