import boto3
import os
from botocore.exceptions import ClientError

s3_client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def upload_file_to_s3(file_obj, s3_key: str):
    s3_client.upload_fileobj(file_obj, BUCKET_NAME, s3_key)
    return s3_key

def generate_presigned_url(s3_key: str, expires_in: int = 3600):
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expires_in,
        )
    except ClientError:
        return None