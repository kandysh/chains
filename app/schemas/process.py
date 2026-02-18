"""Pydantic schemas for the /process endpoint family."""

from uuid import UUID

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    booking_excel_s3_key: str = Field(
        description="S3 object key for the booking Excel file"
    )
    confirmation_pdf_s3_key: str = Field(
        description="S3 object key for the confirmation PDF"
    )
    dedup_key: str | None = Field(
        default=None,
        description="sha256(s3_keys + user_id) — used for idempotent submission",
    )


class ProcessResponse(BaseModel):
    job_id: UUID
    status: str  # 'queued' | 'processing' | 'completed' | 'failed'


class MatchCandidate(BaseModel):
    booking_id: str
    score: float
    reasons: list[str]


class MatchItem(BaseModel):
    allocation_id: str
    booking_id: str | None
    match_tier: str  # 'exact' | 'fuzzy' | 'llm_assisted' | 'unmatched'
    confidence: float | None
    match_reasons: list[str]
    llm_reasoning: str | None = None
    status: str  # 'auto_confirmed' | 'pending_review' | 'confirmed' | 'rejected'


class AmbiguousItem(BaseModel):
    allocation_id: str
    candidates: list[MatchCandidate]
    status: str = "pending_review"


class ReconciliationSummary(BaseModel):
    total_allocations: int
    matched: int
    ambiguous: int
    unmatched: int


class ValidationResult(BaseModel):
    summary: ReconciliationSummary
    matches: list[MatchItem]
    ambiguous: list[AmbiguousItem]


class ConfirmRequest(BaseModel):
    result_id: str
    decision: str = Field(description="'confirmed' or 'rejected'")
    booking_id: str | None = Field(
        default=None,
        description="Required when decision='confirmed' and result was ambiguous",
    )
