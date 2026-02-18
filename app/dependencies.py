"""Shared FastAPI dependency injection — auth, DB session, Redis connection."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.services.db import get_session
from app.services.redis_client import get_redis

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    """Validate JWT and return decoded payload (user_id, etc.)."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


# Convenient type aliases for use in route signatures
CurrentUser = Annotated[dict, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_session)]
RedisConn = Annotated[object, Depends(get_redis)]
AppSettings = Annotated[Settings, Depends(get_settings)]
