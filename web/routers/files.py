from sqlalchemy.orm import Session
from botocore.client import BaseClient

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import APIRouter, UploadFile, File, Depends, Request

from web.models.user import User
from web.db.session import get_s3_client
from web.core.dependencies import require_user, is_csrf_token_verified
from web.services.s3_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    default_response_class=HTMLResponse,
    dependencies=[Depends(require_user), Depends(is_csrf_token_verified)],
)


@router.post("/")
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    s3: BaseClient = Depends(get_s3_client),
    user: User = Depends(require_user),
    csrf_token_verified=Depends(is_csrf_token_verified),
):
    if not user:
        return RedirectResponse("/login", status_code=303)

    if not csrf_token_verified:
        request.session["flash"] = {"type": "error", "msg": "Invalid CSRF"}
        return RedirectResponse("/", status_code=303)

    if not file.filename.endswith(".csv"):
        request.session["flash"] = {
            "type": "error",
            "msg": "Only CSV files allowed",
        }
        return RedirectResponse("/", status_code=303)

    s3_key = f"files/{user.user_id}/{file.filename}"
    upload_file_to_s3(s3, file.file, s3_key, file.content_type)

    request.session["flash"] = {
        "type": "success",
        "msg": f"{file.filename} Uploaded Successfully",
    }

    return RedirectResponse("/", status_code=303)


@router.post("/{file_name}")
def delete_file(
    request: Request,
    file_name: str,
    s3: BaseClient = Depends(get_s3_client),
    user: User = Depends(require_user),
    csrf_token_verified=Depends(is_csrf_token_verified),
):
    if not user:
        return RedirectResponse("/login", status_code=303)

    if not csrf_token_verified:
        request.session["flash"] = {"type": "error", "msg": "Invalid CSRF"}
        return RedirectResponse("/", status_code=303)

    s3_key = f"files/{user.user_id}/{file_name}"
    delete_file_from_s3(s3, s3_key)

    request.session["flash"] = {
        "type": "success",
        "msg": f"{file_name} deleted successfully",
    }

    return RedirectResponse("/", status_code=303)