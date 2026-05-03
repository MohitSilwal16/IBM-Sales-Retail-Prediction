from fastapi.responses import RedirectResponse
from fastapi import Request, Form, HTTPException

from db import sql
from utils import utils
from models.models import User


def verify_session(request: Request) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=307, headers={"Location": "/login"})

    user = sql.get_user_by_user_id(user_id)
    if not user:
        raise HTTPException(status_code=307, headers={"Location": "/login"})

    return user


def attach_csrf_token(request: Request) -> str:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = utils.generate_random_token()
    return request.session["csrf_token"]


def verify_csrf_token(
    request: Request,
    csrf_token: str = Form(...),
) -> None:
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF Verification Failed")
