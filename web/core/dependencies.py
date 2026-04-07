from sqlalchemy.orm import Session

from fastapi import Request, Depends, Form

from web.models.user import User
from web.db.session import get_db
from web.core.security import generate_csrf_token
from web.services.auth_service import get_user_by_user_id


def require_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = get_user_by_user_id(db, user_id)
    if not user:
        return None

    return user


def attach_csrf_token(request: Request) -> str:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = generate_csrf_token()
    return request.session["csrf_token"]


def is_csrf_token_verified(
    request: Request,
    csrf_token: str = Form(...),
) -> bool:
    if csrf_token != request.session.get("csrf_token"):
        print("CSRF Verification Failed")
        return False
    return True