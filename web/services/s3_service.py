import boto3
from app.core.config import settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def upload_file_to_s3(file_obj, key, content_type):
    s3.upload_fileobj(
        file_obj, settings.S3_BUCKET_NAME, key, ExtraArgs={"ContentType": content_type}
    )


def delete_file_from_s3(key):
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
