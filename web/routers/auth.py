from sqlalchemy.orm import Session
from botocore.client import BaseClient

from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from web.models.user import User
from web.db.session import get_db, get_s3_client
from web.services.s3_service import list_files_by_prefix_from_s3
from web.services.auth_service import create_user, authenticate_user
from web.core.dependencies import (
    require_user,
    is_csrf_token_verified,
    attach_csrf_token,
)

router = APIRouter(default_response_class=HTMLResponse)
templates = Jinja2Templates(directory="web/templates")


@router.get("/register")
def register_page(
    request: Request,
    csrf_token=Depends(attach_csrf_token),
):
    flash = request.session.pop("flash", None)

    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "csrf_token": csrf_token,
            "flash": flash,
        },
    )


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    csrf_token_verified=Depends(is_csrf_token_verified),
):
    if not csrf_token_verified:
        request.session["flash"] = {"type": "error", "msg": "Invalid CSRF"}
        return RedirectResponse("/register", status_code=303)

    user = create_user(db, username, password)
    request.session["user_id"] = user.user_id

    return RedirectResponse("/", status_code=303)


@router.get("/login")
def login_page(
    request: Request,
    csrf_token=Depends(attach_csrf_token),
):
    flash = request.session.pop("flash", None)

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "csrf_token": csrf_token,
            "flash": flash,
        },
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    csrf_token_verified=Depends(is_csrf_token_verified),
):
    if not csrf_token_verified:
        request.session["flash"] = {"type": "error", "msg": "Invalid CSRF"}
        return RedirectResponse("/login", status_code=303)

    user = authenticate_user(db, username, password)
    if not user:
        request.session["flash"] = {"type": "error", "msg": "Incorrect Credentials"}
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.user_id
    return RedirectResponse("/", status_code=303)


@router.get("/")
def home_page(
    request: Request,
    s3: BaseClient = Depends(get_s3_client),
    user: User = Depends(require_user),
    csrf_token=Depends(attach_csrf_token),
):
    if not user:
        return RedirectResponse("/login", status_code=303)

    prefix = f"files/{user.user_id}"
    uploaded_files = list_files_by_prefix_from_s3(s3, prefix)

    flash = request.session.pop("flash", None)

    return templates.TemplateResponse(
        request,
        "file.html",
        {
            "user": user.username,
            "files": uploaded_files,
            "csrf_token": csrf_token,
            "flash": flash,
        },
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# TODO: TEMP
@router.get("/analytics")
def analytics(request: Request):
    return templates.TemplateResponse(request, "analytics.html")