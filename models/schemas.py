"""
Pydantic Schemas - SKELETON
Common data models used across the application.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal


class TradeData(BaseModel):
    """
    Represents extracted trade data.

    This is the structure that agents work with after extraction.
    """

    trade_id: str
    counterparty: str
    notional: Decimal
    rate: str
    currency: str
    product: str
    trade_date: date
    settlement_date: date

    class Config:
        json_encoders = {Decimal: str, date: lambda v: v.isoformat()}


class Discrepancy(BaseModel):
    """
    Represents a discrepancy found between extracted data and trade suite.
    """

    field: str
    extracted_value: Any
    expected_value: Any
    suggested_action: str  # e.g., 'suggest_new_alias', 'recheck_pdf', 'flag_for_human'
    reasoning: str
    confidence: float = 0.0
    suggested_alias: Optional[Dict[str, str]] = None


class ConfirmationResponse(BaseModel):
    """
    API response for confirmation status.
    """

    confirmation_id: str
    status: str
    confidence: float
    created_at: str
    completed_at: Optional[str]
    final_data: Optional[Dict[str, Any]]
    validation_issues: List[Dict[str, Any]]
    agent_history: List[Dict[str, Any]]
