from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


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