import secrets
import hashlib

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_str(plain: str) -> str:
    sha = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.hash(sha)


def verify_hash(plain: str, hashed: str) -> bool:
    sha = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(sha, hashed)
