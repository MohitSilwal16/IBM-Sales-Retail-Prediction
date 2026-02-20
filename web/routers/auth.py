from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from web.core.security import generate_csrf_token
from web.db.session import get_db
from web.services.auth_service import (
    create_user,
    authenticate_user,
    get_user_by_user_id,
)

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    create_user(db, username, password)
    return RedirectResponse("/", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = generate_csrf_token()

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "csrf_token": request.session["csrf_token"],
        },
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    user = authenticate_user(db, username, password)
    if not user:
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.user_id
    return RedirectResponse("/", status_code=303)


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse("/login", status_code=303)

    if "csrf_token" not in request.session:
        request.session["csrf_token"] = generate_csrf_token()

    user = get_user_by_user_id(db, request.session["user_id"])

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user.username,
            "csrf_token": request.session["csrf_token"],
        },
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
