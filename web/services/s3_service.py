from typing import BinaryIO, Generator
from botocore.client import BaseClient

from web.core.config import settings

CHUNK_SIZE = 1024 * 1024  # 1 MB


def upload_file_to_s3(s3: BaseClient, file_obj: BinaryIO, key: str) -> None:
    s3.upload_fileobj(file_obj, settings.S3_BUCKET_NAME, key)


def get_file_from_s3(s3: BaseClient, key: str) -> Generator[bytes, None, None]:
    file_obj = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    body = file_obj["Body"]

    while True:
        chunk = body.read(CHUNK_SIZE)
        if not chunk:
            break
        yield chunk


def list_files_by_prefix_from_s3(s3: BaseClient, prefix: str) -> list[dict]:
    files = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, Prefix=prefix)

    return files.get("Contents", [])


def delete_file_from_s3(s3: BaseClient, key: str) -> None:
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)