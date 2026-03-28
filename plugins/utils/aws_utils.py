import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def new_session():
    boto3.session.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name='eu-central-1'
    )


