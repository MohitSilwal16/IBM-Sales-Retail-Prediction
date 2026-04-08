import boto3

from botocore.client import Config
from web.core.config import settings


def init_s3() -> None:
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name=settings.AWS_REGION,
    )

    existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]

    if settings.S3_BUCKET_NAME not in existing_buckets:
        s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)