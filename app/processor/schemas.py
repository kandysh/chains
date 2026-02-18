"""Pydantic schemas enforced as LLM structured output during extraction."""

from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    """A single extracted value with an associated confidence score (0–1)."""

    value: str | float | int | None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedAllocation(BaseModel):
    """One allocation record parsed from a confirmation PDF."""

    counterparty: ExtractedField
    isin: ExtractedField
    cusip: ExtractedField | None = None
    trade_date: ExtractedField        # ISO-8601 date string
    settlement_date: ExtractedField   # ISO-8601 date string
    quantity: ExtractedField          # numeric
    price: ExtractedField             # numeric
    side: ExtractedField              # 'BUY' or 'SELL'
    currency: ExtractedField


class ExtractionResult(BaseModel):
    """Top-level extraction output returned by the LLM."""

    allocations: list[ExtractedAllocation]
