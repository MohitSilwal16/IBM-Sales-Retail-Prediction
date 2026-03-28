from sqlalchemy.orm import Session

from web.models.user import User
from web.models.file import FileMetadata


def create_file_metadata(
    db: Session,
    user_id: str,
    original_filename: str,
    s3_key: str,
    content_type: str,
    size: int,
) -> None:
    metadata = FileMetadata(
        user_id=user_id,
        original_filename=original_filename,
        s3_key=s3_key,
        content_type=content_type,
        size=size,
    )
    db.add(metadata)
    db.commit()


def list_uploaded_files_by_user_id(db: Session, user_id: str) -> list[FileMetadata]:
    return db.query(FileMetadata).filter(FileMetadata.user_id == user_id).all()


def delete_file_by_user_id(db: Session, user_id: str, file_name: str) -> None:
    metadata_entry = (
        db.query(FileMetadata)
        .filter(
            User.user_id == user_id,
            FileMetadata.original_filename == file_name,
        )
        .first()
    )

    if metadata_entry:
        db.delete(metadata_entry)
        db.commit()