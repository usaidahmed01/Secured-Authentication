from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.core.config import settings
from app.db.redis import close_redis, connect_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
async def root():
    return {
        "message": "Secured Auth API is running",
        "environment": settings.app_env,
    }


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
    }