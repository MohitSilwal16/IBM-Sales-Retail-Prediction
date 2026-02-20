import secrets
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_csrf_token():
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    sha = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha)


def verify_password(password: str, hashed: str) -> bool:
    sha = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.verify(sha, hashed)
