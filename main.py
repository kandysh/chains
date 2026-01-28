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

    print("=" * 60)
    print("✓ System ready!")
    print(f"📝 API docs available at: http://{os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', 8000)}/docs")
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
    """Health check endpoint."""
    return {"status": "healthy"}


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
