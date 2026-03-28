from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Request, Form, Depends

from web.models.user import User
from web.db.session import get_db
from web.core.dependencies import (
    require_user,
    is_csrf_token_verified,
    attach_csrf_token,
)
from web.core.security import generate_csrf_token
from web.services.auth_service import (
    create_user,
    authenticate_user,
)
from web.services.metadata_service import list_uploaded_files_by_user_id

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
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
    csrf_token=Depends(attach_csrf_token),
):
    if not user:
        return RedirectResponse("/login", status_code=303)

    uploaded_files = list_uploaded_files_by_user_id(
        db,
        user.user_id,
    )

    flash = request.session.pop("flash", None)

    return templates.TemplateResponse(
        request,
        "home.html",
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