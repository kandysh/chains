"""
FastAPI Application Entry Point - COMPLETE IMPLEMENTATION
No TODOs - This file is fully implemented.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.routes import router
from database.db import init_db
from utils.logging_config import setup_logging
from queue.config import RedisConfig, get_all_queues

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    print("🚀 Starting Trade Confirmation Agent System")
    print("=" * 60)

    # Initialize database
    init_db()
    print("✓ Database initialized")

    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    print("✓ Uploads directory ready")

    # Initialize Redis connection
    try:
        redis_conn = RedisConfig.get_redis_connection()
        redis_conn.ping()
        print("✓ Redis connected")
    except Exception as e:
        print(f"⚠ Redis unavailable: {str(e)}")
        print("  Jobs will be queued but may not process without a running worker")

    # Initialize RQ queues
    try:
        queues = get_all_queues()
        print(f"✓ RQ queues initialized ({len(queues)} queues)")
    except Exception as e:
        print(f"⚠ Failed to initialize RQ queues: {str(e)}")

    # Storage initialization
    try:
        from storage import get_storage
        storage = get_storage()
        storage_type = os.getenv("STORAGE_TYPE", "local")
        print(f"✓ Storage initialized ({storage_type})")
    except Exception as e:
        print(f"⚠ Storage initialization warning: {str(e)}")

    print("=" * 60)
    print("✓ System ready!")
    print(f"📝 API docs available at: http://{os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', 8000)}/docs")
    print("📊 RQ Dashboard (if installed): http://localhost:9181")
    print("=" * 60)

    yield

    # Shutdown
    print("👋 Shutting down Trade Confirmation Agent System")


# Create FastAPI app
app = FastAPI(
    title="Trade Confirmation Agent System",
    description="Agentic system for processing and reconciling trade confirmations",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["confirmations"])


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "name": "Trade Confirmation Agent System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with system status."""
    status = {"status": "healthy", "components": {}}

    # Check database
    try:
        from database.db import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        status["components"]["database"] = "ok"
        db.close()
    except Exception as e:
        status["components"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Redis
    try:
        redis_conn = RedisConfig.get_redis_connection()
        redis_conn.ping()
        status["components"]["redis"] = "ok"
    except Exception as e:
        status["components"]["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check storage
    try:
        from storage import get_storage
        storage = get_storage()
        status["components"]["storage"] = "ok"
    except Exception as e:
        status["components"]["storage"] = f"error: {str(e)}"
        status["status"] = "degraded"

    return status


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info",
    )
