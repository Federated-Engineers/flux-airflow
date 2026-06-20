import logging

import boto3

logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_ssm_parameter(FILE_PATH):
    """Get credentials from AWS ssm
    - param_name: the name of the parameter in ssm to retrieve
    the credentials for google service account
    Args:
    Returns:
    The parameter value as a string
    Raise:
    connectionError: if there is an issue connecting to AWS SSM
    """
    try:
        ssm = boto3.client("ssm")
        response = ssm.get_parameter(Name=FILE_PATH, WithDecryption=True)
        return response["Parameter"]["Value"]
    except Exception as e:
        logger.error(f"failed to get credentials for {FILE_PATH}: {e}")
        raise ConnectionError(
            f"failed to get credentials for {FILE_PATH}: {e}"
        )
