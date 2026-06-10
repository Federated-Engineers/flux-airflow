import boto3


def get_ssm_parameter(ssm_paramter_name: str):
    """Fetch the value of a parameter from AWS Systems Manager Parameter Store
    Args:
        ssm_parameter_name (str): The name of the parameter to fetch.
    Returns:
        str: The value of the specified parameter.
    """
    client = boto3.client(
                'ssm',
                region_name='eu-central-1',
        )
    response = client.get_parameter(Name=ssm_paramter_name,
                                    WithDecryption=True)
    ssm_params_value = response['Parameter']['Value']
    return ssm_params_value
