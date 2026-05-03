from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from config.config import settings
from handler import auth, files, predict, train

web = FastAPI()

web.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
)

web.include_router(auth.router)
web.include_router(files.router)
web.include_router(predict.router)
web.include_router(train.router)
