from typing import BinaryIO
from botocore.client import BaseClient

from web.core.config import settings


def upload_file_to_s3(
    s3: BaseClient, file_obj: BinaryIO, key: str, content_type: str
) -> None:
    s3.upload_fileobj(
        file_obj, settings.S3_BUCKET_NAME, key, ExtraArgs={"ContentType": content_type}
    )


def delete_file_from_s3(s3: BaseClient, key: str) -> None:
    s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
