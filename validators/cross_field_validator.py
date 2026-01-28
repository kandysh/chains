"""
Cross-Field Validator - SKELETON
IMPLEMENT THE TODOs

This module validates relationships between different fields in the trade data.
These are validations that require looking at multiple fields together.
"""

from typing import Dict, Any
from datetime import date
from validators.validation_models import ValidationResult, ValidationIssue, Severity
from utils.helpers import calculate_settlement_days


class CrossFieldValidator:
    """
    Validates relationships between fields in trade confirmations.

    Examples of cross-field validation:
    - Settlement date must be after trade date
    - Currency must be consistent across all fields
    - Rate type should match product type (SOFR for USD swaps, etc.)
    - Notional amount should be reasonable for the product type
    """

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Run all cross-field validations.

        Args:
            data: Trade data dictionary

        Returns:
            ValidationResult with all issues found

        TODO: Implement this method
        Steps:
        1. Create a new ValidationResult instance
        2. Call each validation method:
           - self._validate_settlement_after_trade(data, result)
           - self._validate_currency_consistency(data, result)
           - self._validate_rate_product_match(data, result)
           - self._validate_notional_product_reasonableness(data, result)
        3. Return the result
        """
        # TODO: Create ValidationResult
        # TODO: Call all validation methods
        # TODO: Return result
        pass

    def _validate_settlement_after_trade(
        self, data: Dict[str, Any], result: ValidationResult
    ) -> None:
        """
        Validate that settlement_date is after trade_date.

        Also check that settlement is within a reasonable timeframe (typically 1-5 business days).

        Args:
            data: Trade data dictionary
            result: ValidationResult to add issues to

        TODO: Implement this method
        Steps:
        1. Get trade_date and settlement_date from data
        2. If either is missing, skip validation
        3. If settlement_date <= trade_date:
           - Create ERROR level ValidationIssue
           - message: "Settlement date must be after trade date"
        4. Calculate business days between dates using calculate_settlement_days helper
        5. If days > 10:
           - Create WARNING level ValidationIssue
           - message: f"Unusual settlement period: {days} business days"
           - confidence_impact=0.1
        6. Add issues to result

        HINT: Use calculate_settlement_days from utils.helpers
        """
        # TODO: Get dates from data
        # TODO: Check settlement > trade date
        # TODO: Check settlement period is reasonable
        # TODO: Create and add ValidationIssues as needed
        pass

    def _validate_currency_consistency(
        self, data: Dict[str, Any], result: ValidationResult
    ) -> None:
        """
        Validate that currency is consistent across all currency-related fields.

        For this validation, we mainly check that the currency field is populated.
        More complex trades might have multiple currencies, but for now we keep it simple.

        Args:
            data: Trade data dictionary
            result: ValidationResult to add issues to

        TODO: Implement this method
        Steps:
        1. Get currency from data
        2. If currency is missing or empty:
           - Create ERROR level ValidationIssue
           - field='currency'
           - rule='currency_required'
           - message="Currency is required"
           - confidence_impact=0.2
        3. Add issue to result if needed
        """
        # TODO: Get currency from data
        # TODO: Check if present
        # TODO: If missing, create and add ValidationIssue
        pass

    def _validate_rate_product_match(
        self, data: Dict[str, Any], result: ValidationResult
    ) -> None:
        """
        Validate that rate type matches product type.

        Expected combinations:
        - SOFR rates -> USD Interest Rate Swaps
        - LIBOR rates -> GBP Interest Rate Swaps
        - Fixed rates -> Any swap product

        Args:
            data: Trade data dictionary
            result: ValidationResult to add issues to

        TODO: Implement this method
        Steps:
        1. Get rate and product from data
        2. Get currency from data
        3. If product contains "Interest Rate Swap" or "IRS":
           a. If currency == 'USD' and rate doesn't contain 'SOFR':
              - Create WARNING ValidationIssue
              - message="Expected SOFR rate for USD swaps"
              - confidence_impact=0.1
           b. If currency == 'GBP' and rate doesn't contain 'LIBOR':
              - Create WARNING ValidationIssue
              - message="Expected LIBOR rate for GBP swaps"
              - confidence_impact=0.1
        4. Add issues to result

        HINT: Use 'in' operator: 'SOFR' in rate.upper()
        HINT: This is just a simple example - real validation would be more complex
        """
        # TODO: Get rate, product, and currency from data
        # TODO: Check rate/product/currency combinations
        # TODO: Create and add ValidationIssues for suspicious combinations
        pass

    def _validate_notional_product_reasonableness(
        self, data: Dict[str, Any], result: ValidationResult
    ) -> None:
        """
        Validate that notional amount is reasonable for the product type.

        Different products have different typical notional ranges:
        - Interest Rate Swaps: Typically $1M - $1B
        - Credit Default Swaps: Typically $1M - $500M
        - FX trades: Can vary widely

        Args:
            data: Trade data dictionary
            result: ValidationResult to add issues to

        TODO: Implement this method
        Steps:
        1. Get notional and product from data
        2. Convert notional to float if needed
        3. Define expected ranges for each product type:
           - 'Interest Rate Swap' or 'IRS': min=1_000_000, max=1_000_000_000
           - 'Credit Default Swap' or 'CDS': min=1_000_000, max=500_000_000
        4. Check if notional is outside expected range:
           - If notional < min or notional > max:
             - Create WARNING ValidationIssue
             - message=f"Notional {notional} is outside typical range for {product}"
             - confidence_impact=0.05
        5. Add issue to result

        HINT: This is just a guideline, not a hard rule (hence WARNING not ERROR)
        """
        # TODO: Get notional and product from data
        # TODO: Define typical ranges for products
        # TODO: Check if notional is in reasonable range
        # TODO: Create and add ValidationIssue if outside range
        pass
