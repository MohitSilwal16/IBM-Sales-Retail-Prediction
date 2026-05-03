import services

from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request, Form, Depends

from . import templates
from db import sql
from models.models import User
from middleware import middleware

router = APIRouter()


@router.get("/register")
def register_page(
    request: Request,
    csrf_token: str = Depends(middleware.attach_csrf_token),
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
    _=Depends(middleware.verify_csrf_token),
):
    user = services.auth.register_user(username, password)
    request.session["user_id"] = user.user_id

    return RedirectResponse("/", status_code=303)


@router.get("/login")
def login_page(
    request: Request,
    csrf_token: str = Depends(middleware.attach_csrf_token),
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
    _=Depends(middleware.verify_csrf_token),
):
    user = services.auth.authenticate_user(username, password)
    if not user:
        request.session["flash"] = {"type": "error", "msg": "Incorrect Credentials"}
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.user_id
    return RedirectResponse("/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/")
def home_page(
    request: Request,
    user: User = Depends(middleware.verify_session),
    csrf_token: str = Depends(middleware.attach_csrf_token),
):
    file_prefix = f"files/{user.user_id}/"
    uploaded_files = services.s3_service.list_files_by_prefix_from_s3(file_prefix)

    for f in uploaded_files:
        file_name = f["Key"].removeprefix(f"files/{user.user_id}/")
        f["is_model_trained"] = False

        model_meta_data = sql.get_model_by_user_and_file(user.user_id, file_name)
        if model_meta_data:
            f["is_model_trained"] = True

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
