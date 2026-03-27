import logging

import awswrangler as wr
import boto3

# from datetime import datetime, timezone


logger = logging.getLogger(__name__)


# def get_latest_s3_file(bucket: str, prefix: str):
#     """
#     A function that returns the path of the last modified data
#     in an S3 bucket.

#     Args:
#         bucket: S3 bucket name.
#         prefix: Prefix/Folder name to search in.
#     Returns:
#         The S3 path of the latest file.
#     """

#     s3 = boto3.client("s3")
#     response = s3.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/")
#     files = response.get("Contents", [])

#     if not files:
#         raise ValueError(f"No files found in s3://{bucket}/{prefix}")

#     logger.info(f"{len(files)} file(s) found in s3://{bucket}/{prefix}")

#     latest_object = max(files, key=lambda x: x["LastModified"])

#     # last_modified = latest_object["LastModified"]
#     # today = datetime.now(timezone.utc)
#     # date_difference = (today.date() - last_modified.date()).days

#     # if date_difference > last_date:
#     #     logger.info("No new file to process today.")
#     #     return None

#     latest_file_path = f"s3://{bucket}/{latest_object['Key']}"
#     logger.info(f"Latest file: {latest_file_path}")
#     return latest_file_path


def write_df_to_s3(df, bucket_name, folder_name, file_name, dataset=False):
    """
    Write a pandas DataFrame to S3 as a Parquet file.

    Args:
        df (pd.DataFrame): DataFrame to write.
        bucket_name (str): S3 bucket name.
        folder_name (str): Folder/prefix in S3.
        file_name (str): Name of the file (including .parquet).
        dataset (bool): Whether to write as a partitioned dataset.

    Returns:
        str: Full S3 path of the uploaded file.
    """
    s3_path = f"s3://{bucket_name}/{folder_name}/{file_name}"

    wr.s3.to_parquet(
        df=df,
        path=s3_path,
        dataset=dataset
    )

    return f"Data successfully written to {s3_path}"