from db import sql
from utils import utils
from models.models import User


def register_user(username: str, password: str) -> User:
    hashed_password = utils.hash_str(password)

    user = User(username=username, hashed_password=hashed_password)
    return sql.create_user(user)


def authenticate_user(username: str, password: str) -> User | None:
    user = sql.get_user_by_user_name(username)
    if not user:
        return None

    hash_verified = utils.verify_hash(password, user.hashed_password)
    if hash_verified:
        return user

    return None
