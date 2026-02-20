from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import uuid

from web.db.session import get_db
from web.models.file import FileMetadata
from web.services.s3_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/")
async def upload_csv(
    request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401)

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    unique_key = f"{request.session['user_id']}/{uuid.uuid4()}_{file.filename}"

    upload_file_to_s3(file.file, unique_key, file.content_type)

    metadata = FileMetadata(
        user_id=request.session["user_id"],
        original_filename=file.filename,
        s3_key=unique_key,
        content_type=file.content_type,
        size=0,  # optionally compute
    )

    db.add(metadata)
    db.commit()
    db.refresh(metadata)

    return {"message": "Uploaded", "file_id": metadata.file_id}


@router.get("/")
def list_files(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        raise HTTPException(status_code=401)

    files = (
        db.query(FileMetadata)
        .filter(FileMetadata.user_id == request.session["user_id"])
        .all()
    )

    return files


@router.put("/{file_id}")
async def overwrite_file(
    file_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    metadata = (
        db.query(FileMetadata)
        .filter_by(file_id=file_id, user_id=request.session["user_id"])
        .first()
    )

    if not metadata:
        raise HTTPException(status_code=404)

    upload_file_to_s3(file.file, metadata.s3_key, file.content_type)

    return {"message": "File overwritten"}


@router.delete("/{file_id}")
def delete_file(file_id: int, request: Request, db: Session = Depends(get_db)):
    metadata = (
        db.query(FileMetadata)
        .filter_by(file_id=file_id, user_id=request.session["user_id"])
        .first()
    )

    if not metadata:
        raise HTTPException(status_code=404)

    delete_file_from_s3(metadata.s3_key)

    db.delete(metadata)
    db.commit()

    return {"message": "Deleted"}
