"""
Validation Models - SKELETON
IMPLEMENT THE TODOs

This module defines the data structures used for validation and the
TradeConfirmation model with Pydantic validators.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator, root_validator


class Severity(str, Enum):
    """
    Severity levels for validation issues.

    ERROR: Critical issue that prevents auto-processing
    WARNING: Issue that should be reviewed but might not block processing
    INFO: Informational note that doesn't require action
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """
    Represents a single validation issue found in the data.

    Attributes:
        severity: How serious this issue is
        field: Which field has the issue (e.g., 'notional', 'counterparty')
        rule: Which validation rule was violated (e.g., 'positive_notional', 'valid_currency')
        message: Human-readable description of the issue
        expected: What value was expected (optional)
        actual: What value was found (optional)
        confidence_impact: How much this issue reduces confidence (0.0 to 1.0)
    """

    severity: Severity
    field: str
    rule: str
    message: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    confidence_impact: float = 0.0  # How much this reduces confidence


class ValidationResult(BaseModel):
    """
    Result of running all validation checks.

    Attributes:
        is_valid: True if no ERROR-level issues found
        issues: List of all validation issues
        confidence_penalty: Total confidence penalty from all issues
    """

    is_valid: bool = True
    issues: List[ValidationIssue] = []
    confidence_penalty: float = 0.0

    def add_issue(self, issue: ValidationIssue) -> None:
        """
        Add a validation issue to the result.

        This also updates is_valid and confidence_penalty automatically.

        Args:
            issue: The validation issue to add

        TODO: Implement this method
        Steps:
        1. Append issue to self.issues
        2. Add issue.confidence_impact to self.confidence_penalty
        3. If issue.severity is Severity.ERROR, set self.is_valid to False
        """
        # TODO: Append issue to self.issues
        # TODO: Update self.confidence_penalty
        # TODO: If severity is ERROR, set self.is_valid to False
        pass

    def has_errors(self) -> bool:
        """Check if there are any ERROR-level issues."""
        return any(issue.severity == Severity.ERROR for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if there are any WARNING-level issues."""
        return any(issue.severity == Severity.WARNING for issue in self.issues)


class TradeConfirmation(BaseModel):
    """
    Pydantic model for trade confirmation with field-level validators.

    This model provides automatic validation when you create an instance.
    If any validation fails, it raises a ValidationError.

    Example:
        try:
            trade = TradeConfirmation(**extracted_data)
        except ValidationError as e:
            # Handle validation errors
            pass
    """

    trade_id: str
    counterparty: str
    notional: Decimal
    rate: str
    currency: str
    product: str
    trade_date: date
    settlement_date: date

    @validator("trade_id")
    def validate_trade_id(cls, v):
        """
        Validate trade ID format.

        Trade IDs should not be empty and should follow expected format.

        TODO: Implement this validator
        Steps:
        1. Check if v is not None and not empty string
        2. Check if length is reasonable (e.g., 3-50 characters)
        3. Raise ValueError with descriptive message if invalid
        4. Return v if valid

        HINT: Use raise ValueError("message") for validation failures
        """
        # TODO: Check trade_id is not empty
        # TODO: Check length is reasonable (3-50 chars)
        # TODO: Raise ValueError if invalid
        return v

    @validator("notional")
    def validate_notional(cls, v):
        """
        Validate notional amount.

        Rules:
        - Must be positive (> 0)
        - Must be less than $1 trillion (reasonable upper limit)

        TODO: Implement this validator
        Steps:
        1. Check if v > 0
        2. Check if v < 1,000,000,000,000 (1 trillion)
        3. Raise ValueError with descriptive message if invalid
        4. Return v if valid
        """
        # TODO: Check notional > 0
        # TODO: Check notional < 1e12 (1 trillion)
        # TODO: Raise ValueError if invalid
        return v

    @validator("currency")
    def validate_currency(cls, v):
        """
        Validate currency code.

        Must be one of the supported currencies: USD, EUR, GBP, JPY, INR

        TODO: Implement this validator
        Steps:
        1. Define list of valid currencies: ['USD', 'EUR', 'GBP', 'JPY', 'INR']
        2. Check if v is in the list (case-insensitive)
        3. Raise ValueError if not valid
        4. Return v.upper() to ensure consistent casing
        """
        # TODO: Check currency is in valid list
        # TODO: Raise ValueError if invalid
        # TODO: Return uppercase version
        return v

    @validator("counterparty")
    def validate_counterparty(cls, v):
        """
        Validate counterparty name.

        Should not be empty and should have reasonable length.

        TODO: Implement this validator
        Steps:
        1. Check v is not None and not empty after stripping whitespace
        2. Check length is at least 2 characters
        3. Raise ValueError if invalid
        4. Return v.strip()
        """
        # TODO: Check counterparty is not empty
        # TODO: Check minimum length
        # TODO: Raise ValueError if invalid
        return v

    @root_validator
    def validate_dates(cls, values):
        """
        Cross-field validation for dates.

        Rules:
        - settlement_date must be after trade_date
        - settlement_date should typically be within 5 business days

        TODO: Implement this root validator
        Steps:
        1. Get trade_date and settlement_date from values dict
        2. Check both are present
        3. Check settlement_date > trade_date
        4. Raise ValueError if invalid
        5. Return values if valid

        HINT: root_validator receives a dict of all field values
        HINT: Use raise ValueError("message") for validation failures
        """
        # TODO: Get trade_date and settlement_date from values
        # TODO: Check settlement_date > trade_date
        # TODO: Raise ValueError if invalid
        return values

    class Config:
        """Pydantic configuration."""

        json_encoders = {Decimal: str, date: lambda v: v.isoformat()}
