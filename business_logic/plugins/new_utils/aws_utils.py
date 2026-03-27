import os

import boto3
from airflow.models import Variable
from dotenv import load_dotenv

load_dotenv()


# def new_session():
#     boto3.session.Session(
#             aws_access_key_id=Variable.get("AWS_ACCESS_KEY_ID"),
#             aws_secret_access_key=Variable.get("AWS_SECRET_ACCESS_KEY"),
#             region_name='eu-central-1'
#     )

def new_session():
    boto3.session.Session(
            aws_access_key_id=os.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.get("AWS_SECRET_ACCESS_KEY"),
            region_name='eu-central-1'
    )