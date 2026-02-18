"""Tests for the matching engine (Tier 1, 2, 3)."""

import pytest

from app.processor.matcher import _score
from app.processor.schemas import ExtractedAllocation, ExtractedField


def _make_alloc(**kwargs) -> ExtractedAllocation:
    defaults = {
        "counterparty": ExtractedField(value="Goldman Sachs", confidence=0.99),
        "isin": ExtractedField(value="US0378331005", confidence=0.99),
        "trade_date": ExtractedField(value="2026-02-15", confidence=0.99),
        "settlement_date": ExtractedField(value="2026-02-18", confidence=0.99),
        "quantity": ExtractedField(value=50000, confidence=0.99),
        "price": ExtractedField(value=142.50, confidence=0.99),
        "side": ExtractedField(value="BUY", confidence=0.99),
        "currency": ExtractedField(value="USD", confidence=0.99),
    }
    defaults.update(kwargs)
    return ExtractedAllocation(**defaults)


def _make_booking(**kwargs) -> dict:
    defaults = {
        "booking_id": "BK-001",
        "isin": "US0378331005",
        "trade_date": "2026-02-15",
        "settlement_date": "2026-02-18",
        "quantity": "50000",
        "price": "142.50",
        "side": "BUY",
        "currency": "USD",
        "counterparty": "Goldman Sachs",
    }
    defaults.update(kwargs)
    return defaults


class TestFuzzyScoring:
    def test_perfect_match_scores_one(self):
        alloc = _make_alloc()
        booking = _make_booking()
        result = _score(alloc, booking)
        assert result["score"] == pytest.approx(1.0, abs=0.01)

    def test_wrong_currency_reduces_score(self):
        alloc = _make_alloc()
        booking = _make_booking(currency="EUR")
        result = _score(alloc, booking)
        assert result["score"] < 1.0

    def test_quantity_mismatch_reduces_score(self):
        alloc = _make_alloc()
        booking = _make_booking(quantity="45000")
        result = _score(alloc, booking)
        assert result["score"] < 0.90

    def test_counterparty_similarity(self):
        alloc = _make_alloc(
            counterparty=ExtractedField(value="Goldman Sachs & Co.", confidence=0.95)
        )
        booking = _make_booking(counterparty="Goldman Sachs")
        result = _score(alloc, booking)
        # Should still score high due to Levenshtein similarity
        assert result["score"] > 0.70
