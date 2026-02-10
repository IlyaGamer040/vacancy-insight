from fastapi import FastAPI
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.middleware import setup_middleware
from app.core.exceptions import setup_exception_handlers
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
import logging


# Логирование
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекст жизненного цикла приложения
    """
    logger.info("Starting app...")

    if settings.DEBUG:
        logger.info("Creating database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database created successfuly")

    yield


    logger.info("Stutting down app...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

setup_middleware(app)
setup_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Главные эндпоинты

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": f"Добро пожаловать в API {settings.PROJECT_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX,
    }

@app.get("/health")
async def health_check():
    """Проверка жизнеспособности"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }


# Запуск через uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )