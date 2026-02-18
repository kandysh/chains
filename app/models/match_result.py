"""SQLAlchemy model for the match_results table."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MatchResult(Base):
    __tablename__ = "match_results"
    __table_args__ = (
        UniqueConstraint("job_id", "allocation_id", name="uq_match_result_job_alloc"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("validation_jobs.id"), nullable=False, index=True
    )
    allocation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    allocation_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Populated when a match is found; NULL for unmatched allocations
    booking_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    booking_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Match metadata
    match_tier: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # 'exact' | 'fuzzy' | 'llm_assisted' | 'unmatched'
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    match_reasons: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    llm_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)  # Tier 3 only

    # Review workflow
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending_review", index=True
    )  # 'pending_review' | 'auto_confirmed' | 'confirmed' | 'rejected'
    reviewed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
