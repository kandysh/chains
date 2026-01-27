"""API router configuration."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")


# Example endpoint structure - replace with your chains
@api_router.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to Chains API"}
