from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from web.db.base import Base
from web.db.session import engine
from web.core.config import settings
from web.routers import auth

web = FastAPI()

web.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)

Base.metadata.create_all(bind=engine)

web.include_router(auth.router)
