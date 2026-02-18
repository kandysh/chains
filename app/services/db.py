"""PostgreSQL async CRUD operations via SQLAlchemy 2.0."""

import logging
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.match_result import MatchResult
from app.models.validation_job import ValidationJob
from app.schemas.process import (
    AmbiguousItem,
    MatchCandidate,
    MatchItem,
    ReconciliationSummary,
    ValidationResult,
)

logger = logging.getLogger(__name__)

_engine = None
_session_factory: async_sessionmaker | None = None


async def init_db() -> None:
    global _engine, _session_factory
    settings = get_settings()
    _engine = create_async_engine(settings.database_url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialised")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a scoped async DB session."""
    async with _session_factory() as session:
        yield session


# ── ValidationJob CRUD ────────────────────────────────────────────────────────


async def create_job(
    session: AsyncSession,
    *,
    user_id: str,
    booking_s3_key: str,
    confirm_s3_key: str,
    dedup_key: str | None,
) -> ValidationJob:
    job = ValidationJob(
        user_id=user_id,
        booking_s3_key=booking_s3_key,
        confirm_s3_key=confirm_s3_key,
        dedup_key=dedup_key,
        status="queued",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> ValidationJob | None:
    result = await session.execute(select(ValidationJob).where(ValidationJob.id == job_id))
    return result.scalar_one_or_none()


async def get_job_by_dedup_key(
    session: AsyncSession, dedup_key: str
) -> ValidationJob | None:
    result = await session.execute(
        select(ValidationJob).where(ValidationJob.dedup_key == dedup_key)
    )
    return result.scalar_one_or_none()


async def update_job_status(
    session: AsyncSession,
    job_id: uuid.UUID,
    status: str,
    **kwargs,
) -> None:
    values = {"status": status, **kwargs}
    if status in ("completed", "failed"):
        values["completed_at"] = datetime.now(tz=timezone.utc)
    await session.execute(
        update(ValidationJob).where(ValidationJob.id == job_id).values(**values)
    )
    await session.commit()


# ── MatchResult CRUD ──────────────────────────────────────────────────────────


async def upsert_match_result(session: AsyncSession, result: MatchResult) -> MatchResult:
    """INSERT or UPDATE a match result by (job_id, allocation_id)."""
    existing = await session.execute(
        select(MatchResult).where(
            MatchResult.job_id == result.job_id,
            MatchResult.allocation_id == result.allocation_id,
        )
    )
    row = existing.scalar_one_or_none()
    if row:
        row.booking_id = result.booking_id
        row.booking_data = result.booking_data
        row.match_tier = result.match_tier
        row.confidence = result.confidence
        row.match_reasons = result.match_reasons
        row.llm_reasoning = result.llm_reasoning
        row.status = result.status
    else:
        session.add(result)
    await session.commit()
    return row or result


async def get_validation_result(
    session: AsyncSession, job_id: uuid.UUID
) -> ValidationResult:
    """Assemble the full ValidationResult response from match_results rows."""
    rows_result = await session.execute(
        select(MatchResult).where(MatchResult.job_id == job_id)
    )
    rows = rows_result.scalars().all()

    matches: list[MatchItem] = []
    ambiguous: list[AmbiguousItem] = []

    for row in rows:
        if row.match_tier in ("exact", "fuzzy") and row.status != "pending_review":
            matches.append(
                MatchItem(
                    allocation_id=row.allocation_id,
                    booking_id=row.booking_id,
                    match_tier=row.match_tier,
                    confidence=float(row.confidence) if row.confidence else None,
                    match_reasons=row.match_reasons or [],
                    llm_reasoning=row.llm_reasoning,
                    status=row.status,
                )
            )
        elif row.match_tier == "llm_assisted" or row.status == "pending_review":
            candidates = [
                MatchCandidate(**c) for c in (row.match_reasons or []) if isinstance(c, dict)
            ]
            ambiguous.append(
                AmbiguousItem(
                    allocation_id=row.allocation_id,
                    candidates=candidates,
                    status=row.status,
                )
            )
        else:
            matches.append(
                MatchItem(
                    allocation_id=row.allocation_id,
                    booking_id=None,
                    match_tier="unmatched",
                    confidence=None,
                    match_reasons=[],
                    status=row.status,
                )
            )

    summary = ReconciliationSummary(
        total_allocations=len(rows),
        matched=len(matches),
        ambiguous=len(ambiguous),
        unmatched=sum(1 for m in matches if m.match_tier == "unmatched"),
    )
    return ValidationResult(summary=summary, matches=matches, ambiguous=ambiguous)


# ── Review decisions ──────────────────────────────────────────────────────────


async def record_review_decision(
    session: AsyncSession,
    *,
    result_id: str,
    decision: str,
    booking_id: str | None,
    reviewed_by: str,
) -> None:
    result_uuid = uuid.UUID(result_id)
    now = datetime.now(tz=timezone.utc)
    await session.execute(
        update(MatchResult)
        .where(MatchResult.id == result_uuid)
        .values(
            status=decision,
            booking_id=booking_id or MatchResult.booking_id,
            reviewed_by=reviewed_by,
            reviewed_at=now,
        )
    )
    log = AuditLog(
        result_id=result_uuid,
        action=f"review:{decision}",
        actor=reviewed_by,
        details={"booking_id": booking_id},
    )
    session.add(log)
    await session.commit()
