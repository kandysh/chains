"""FastAPI API service — Port 8000.

Responsibilities: presigned URL generation, job submission, SSE streaming,
result serving, user confirmations. No file I/O, no LLM calls.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import process, upload
from app.services import db, redis_client

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.basicConfig(level=settings.log_level)
    logger.info("API service starting up")
    await db.init_db()
    await redis_client.init_redis()
    yield
    # Shutdown
    logger.info("API service shutting down")
    await redis_client.close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Trade Reconciliation Platform — API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(upload.router)
    app.include_router(process.router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "service": "api"}

    return app


app = create_app()
