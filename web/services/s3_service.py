import boto3

from typing import BinaryIO, Generator

from config.config import settings

CHUNK_SIZE = 1024 * 1024  # 1 MB


# Init
s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]

if settings.S3_BUCKET_NAME not in existing_buckets:
    s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)


# Services
def upload_file_to_s3(file_obj: BinaryIO, key: str) -> None:
    s3.upload_fileobj(file_obj, settings.S3_BUCKET_NAME, key)


def get_file_from_s3(key: str) -> Generator[bytes, None, None]:
    file_obj = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    body = file_obj["Body"]

    while True:
        chunk = body.read(CHUNK_SIZE)
        if not chunk:
            break
        yield chunk


def list_files_by_prefix_from_s3(prefix: str):
    files = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix).get(
        "Contents", []
    )

    return files


def delete_file_from_s3(key: str) -> None:
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
