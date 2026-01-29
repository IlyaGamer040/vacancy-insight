from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from app.core.config import settings


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s"
        )

        response.headers["X-Process-Time"] = str(process_time)
        return response
    
def setup_middleware(app):
    # CORS
    allow_origins = settings.CORS_ORIGINS
    if isinstance(allow_origins, str):
        parsed = None
        try:
            parsed = json.loads(allow_origins)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            allow_origins = parsed
        else:
            allow_origins = [
                origin.strip() for origin in allow_origins.split(",") if origin.strip()
            ]
    if not allow_origins:
        allow_origins = ["*"]

    allow_credentials = True
    if "*" in allow_origins:
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Logging
    app.add_middleware(LoggingMiddleware)