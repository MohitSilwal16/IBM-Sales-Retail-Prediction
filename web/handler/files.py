import services

from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi import APIRouter, UploadFile, File, Depends, Request, Query

from middleware import middleware
from models.models import User

DATA_FILES_PREFIX = "files"
MODEL_FILES_PREFIX = "models"

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/")
async def upload_data_file(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(middleware.verify_session),
    _=Depends(middleware.verify_csrf_token),
):
    if not file.filename.endswith(".csv"):
        request.session["flash"] = {
            "type": "error",
            "msg": "Only CSV files allowed",
        }
        return RedirectResponse("/", status_code=303)

    s3_key = f"{DATA_FILES_PREFIX}/{user.user_id}/{file.filename}"
    services.s3_service.upload_file_to_s3(file.file, s3_key)

    request.session["flash"] = {
        "type": "success",
        "msg": f"{file.filename} Uploaded Successfully",
    }

    return RedirectResponse("/", status_code=303)


@router.get("/{file_name}")
async def download_data_file(
    file_name: str,
    download: int = Query(0),
    user: User = Depends(middleware.verify_session),
):
    s3_key = f"{DATA_FILES_PREFIX}/{user.user_id}/{file_name}"

    headers = {}
    if download:
        headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}

    return StreamingResponse(
        services.s3_service.get_file_from_s3(s3_key), headers=headers
    )


@router.post("/{file_name}")
def delete_data_file(
    request: Request,
    file_name: str,
    user: User = Depends(middleware.verify_session),
    _=Depends(middleware.verify_csrf_token),
):
    data_s3_key = f"{DATA_FILES_PREFIX}/{user.user_id}/{file_name}"
    services.s3_service.delete_file_from_s3(data_s3_key)

    model_s3_key = f"{MODEL_FILES_PREFIX}/{user.user_id}/{file_name}"
    services.s3_service.delete_file_from_s3(model_s3_key)

    request.session["flash"] = {
        "type": "success",
        "msg": f"{file_name} deleted successfully",
    }

    # TODO: Delete Model File if Exists

    return RedirectResponse("/", status_code=303)
