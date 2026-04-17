from fastapi import FastAPI
from typing import AsyncIterator
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware

from web.db.base import Base
from web.db.session import engine
from web.core.config import settings
from web.core.startup import init_s3
from web.routers import auth, files, predict


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_s3()
    yield


web = FastAPI(lifespan=lifespan)

web.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
)


Base.metadata.create_all(bind=engine)

web.include_router(auth.router)
web.include_router(files.router)
web.include_router(predict.router)