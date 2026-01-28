from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging


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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Logging
    app.add_middleware(LoggingMiddleware)