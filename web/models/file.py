from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from web.db.base import Base


class FileMetadata(Base):
    __tablename__ = "files"

    file_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    original_filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False, unique=True)

    content_type = Column(String)
    size = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
