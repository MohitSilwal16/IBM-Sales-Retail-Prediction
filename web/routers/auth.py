from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

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
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, username, password)
    if not user:
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.user_id
    return RedirectResponse("/", status_code=303)


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    if "user_id" not in request.session:
        return RedirectResponse("/login", status_code=303)

    user = get_user_by_user_id(db, user_id=request.session["user_id"])
    if not user:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user.username}
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
