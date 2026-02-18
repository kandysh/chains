"""Phase 3 — Three-Tier Matching Engine.

Tier 1 — Exact Match     : ISIN + trade_date + quantity + side all identical.
                           Auto-confirmed; confidence = 1.0.
Tier 2 — Fuzzy Match     : Weighted field scoring with configurable tolerances.
                           Score ≥ 0.90 → high-confidence fuzzy match.
                           Score 0.70–0.90 → ambiguous, pending human review.
Tier 3 — LLM-Assisted    : Top-3 candidates presented to LLM for reasoning.
                           Always requires human confirmation (never auto-confirmed).
Unmatched                : No viable candidate found across all tiers.

Every match decision is fully logged for compliance auditability.
"""

import json
import logging
from dataclasses import dataclass, field

from Levenshtein import ratio as levenshtein_ratio
from openai import AsyncOpenAI

from app.config import Settings
from app.processor.schemas import ExtractedAllocation
from app.services.redis_client import get_redis

logger = logging.getLogger(__name__)

# ── Tier 2 field weights ─────────────────────────────────────────────────────
WEIGHTS = {
    "isin": 0.30,
    "trade_date": 0.20,
    "quantity": 0.20,
    "counterparty": 0.15,
    "price": 0.10,
    "currency": 0.05,
}

QUANTITY_TOLERANCE = 0.0001   # ±0.01 %
PRICE_TOLERANCE = 0.001       # ±0.1 %
DATE_TOLERANCE_DAYS = 1       # ±1 business day
COUNTERPARTY_MIN_SIMILARITY = 0.85


@dataclass
class MatchDecision:
    allocation_id: str
    match_tier: str  # 'exact' | 'fuzzy' | 'llm_assisted' | 'unmatched'
    booking_id: str | None
    booking_data: dict | None
    confidence: float | None
    match_reasons: list[dict]  # field-level audit trail
    llm_reasoning: str | None = None
    status: str = "pending_review"


async def match_allocations(
    job_id: str,
    allocations: list[ExtractedAllocation],
    settings: Settings,
) -> list[MatchDecision]:
    """Run the three-tier matching engine over all extracted allocations."""
    decisions: list[MatchDecision] = []
    for alloc in allocations:
        alloc_id = _allocation_id(alloc)
        decision = await _match_single(job_id, alloc_id, alloc, settings)
        decisions.append(decision)
        logger.debug(
            "[%s] %s → tier=%s booking=%s confidence=%s",
            job_id,
            alloc_id,
            decision.match_tier,
            decision.booking_id,
            decision.confidence,
        )
    return decisions


async def _match_single(
    job_id: str,
    alloc_id: str,
    alloc: ExtractedAllocation,
    settings: Settings,
) -> MatchDecision:
    # ── Tier 1: Exact ────────────────────────────────────────────────────────
    exact = await _exact_match(job_id, alloc)
    if exact:
        booking_id, booking_data = exact
        return MatchDecision(
            allocation_id=alloc_id,
            match_tier="exact",
            booking_id=booking_id,
            booking_data=booking_data,
            confidence=1.0,
            match_reasons=[{"tier": "exact", "fields": ["isin", "trade_date", "quantity", "side"]}],
            status="auto_confirmed",
        )

    # ── Tier 2: Fuzzy ────────────────────────────────────────────────────────
    candidates = await _fuzzy_candidates(job_id, alloc, settings)
    if candidates:
        top = candidates[0]
        if top["score"] >= settings.fuzzy_high_confidence:
            return MatchDecision(
                allocation_id=alloc_id,
                match_tier="fuzzy",
                booking_id=top["booking_id"],
                booking_data=top["booking_data"],
                confidence=top["score"],
                match_reasons=top["reasons"],
                status="auto_confirmed",
            )
        if top["score"] >= settings.fuzzy_ambiguous_min:
            return MatchDecision(
                allocation_id=alloc_id,
                match_tier="fuzzy",
                booking_id=top["booking_id"],
                booking_data=top["booking_data"],
                confidence=top["score"],
                match_reasons=top["reasons"],
                status="pending_review",
            )

    # ── Tier 3: LLM-Assisted ─────────────────────────────────────────────────
    top3 = candidates[:3] if candidates else []
    if top3:
        reasoning = await _llm_reasoning(alloc, top3, settings)
        return MatchDecision(
            allocation_id=alloc_id,
            match_tier="llm_assisted",
            booking_id=top3[0]["booking_id"],
            booking_data=top3[0]["booking_data"],
            confidence=top3[0]["score"],
            match_reasons=top3[0]["reasons"],
            llm_reasoning=reasoning,
            status="pending_review",  # Always requires human confirmation
        )

    # ── Unmatched ─────────────────────────────────────────────────────────────
    return MatchDecision(
        allocation_id=alloc_id,
        match_tier="unmatched",
        booking_id=None,
        booking_data=None,
        confidence=None,
        match_reasons=[],
        status="pending_review",
    )


# ── Tier 1 helpers ────────────────────────────────────────────────────────────


async def _exact_match(
    job_id: str, alloc: ExtractedAllocation
) -> tuple[str, dict] | None:
    """Look up exact ISIN+date key in Redis booking index."""
    redis = await get_redis()
    isin = str(alloc.isin.value or "").upper()
    trade_date = str(alloc.trade_date.value or "")
    key = f"booking:{job_id}:idx:{isin}:{trade_date}"
    raw = await redis.hget(key, "data")
    if not raw:
        return None
    booking = json.loads(raw)
    alloc_qty = float(alloc.quantity.value or 0)
    booking_qty = float(booking.get("quantity", -1))
    alloc_side = str(alloc.side.value or "").upper()
    booking_side = str(booking.get("side", "")).upper()
    if abs(alloc_qty - booking_qty) < 1e-9 and alloc_side == booking_side:
        return booking["booking_id"], booking
    return None


# ── Tier 2 helpers ────────────────────────────────────────────────────────────


async def _fuzzy_candidates(
    job_id: str, alloc: ExtractedAllocation, settings: Settings
) -> list[dict]:
    """Score all bookings with matching ISIN and return ranked candidates."""
    redis = await get_redis()
    isin = str(alloc.isin.value or "").upper()
    # Scan for all date keys for this ISIN
    pattern = f"booking:{job_id}:idx:{isin}:*"
    keys = [k async for k in redis.scan_iter(pattern)]
    if not keys:
        return []

    candidates = []
    for key in keys:
        raw = await redis.hget(key, "data")
        if not raw:
            continue
        booking = json.loads(raw)
        scored = _score(alloc, booking)
        candidates.append(scored)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


def _score(alloc: ExtractedAllocation, booking: dict) -> dict:
    reasons: list[dict] = []
    total = 0.0

    # ISIN (binary)
    isin_match = str(alloc.isin.value or "").upper() == str(booking.get("isin", "")).upper()
    isin_score = 1.0 if isin_match else 0.0
    total += WEIGHTS["isin"] * isin_score
    reasons.append({"field": "isin", "score": isin_score, "weight": WEIGHTS["isin"]})

    # Trade date (±1 day tolerance)
    from datetime import date
    try:
        alloc_date = date.fromisoformat(str(alloc.trade_date.value or ""))
        book_date = date.fromisoformat(str(booking.get("trade_date", "")))
        diff = abs((alloc_date - book_date).days)
        date_score = max(0.0, 1.0 - diff / (DATE_TOLERANCE_DAYS + 1))
    except ValueError:
        date_score = 0.0
    total += WEIGHTS["trade_date"] * date_score
    reasons.append({"field": "trade_date", "score": date_score, "weight": WEIGHTS["trade_date"]})

    # Quantity (±0.01 % tolerance)
    try:
        alloc_qty = float(alloc.quantity.value or 0)
        book_qty = float(booking.get("quantity", 0))
        qty_diff = abs(alloc_qty - book_qty) / max(abs(book_qty), 1)
        qty_score = 1.0 if qty_diff <= QUANTITY_TOLERANCE else max(0.0, 1.0 - qty_diff * 100)
    except (TypeError, ValueError):
        qty_score = 0.0
    total += WEIGHTS["quantity"] * qty_score
    reasons.append({"field": "quantity", "score": qty_score, "weight": WEIGHTS["quantity"]})

    # Counterparty (Levenshtein + alias lookup)
    cpty_alloc = str(alloc.counterparty.value or "").lower().strip()
    cpty_book = str(booking.get("counterparty", "")).lower().strip()
    cpty_score = levenshtein_ratio(cpty_alloc, cpty_book)
    if cpty_score < COUNTERPARTY_MIN_SIMILARITY:
        cpty_score *= 0.5  # penalise but don't zero — may be an alias
    total += WEIGHTS["counterparty"] * cpty_score
    reasons.append({"field": "counterparty", "score": cpty_score, "weight": WEIGHTS["counterparty"]})

    # Price (±0.1 % tolerance)
    try:
        alloc_px = float(alloc.price.value or 0)
        book_px = float(booking.get("price", 0))
        px_diff = abs(alloc_px - book_px) / max(abs(book_px), 1)
        px_score = 1.0 if px_diff <= PRICE_TOLERANCE else max(0.0, 1.0 - px_diff * 10)
    except (TypeError, ValueError):
        px_score = 0.0
    total += WEIGHTS["price"] * px_score
    reasons.append({"field": "price", "score": px_score, "weight": WEIGHTS["price"]})

    # Currency (binary)
    curr_match = str(alloc.currency.value or "").upper() == str(booking.get("currency", "")).upper()
    curr_score = 1.0 if curr_match else 0.0
    total += WEIGHTS["currency"] * curr_score
    reasons.append({"field": "currency", "score": curr_score, "weight": WEIGHTS["currency"]})

    return {
        "booking_id": booking["booking_id"],
        "booking_data": booking,
        "score": round(total, 4),
        "reasons": reasons,
    }


# ── Tier 3 helpers ────────────────────────────────────────────────────────────


async def _llm_reasoning(
    alloc: ExtractedAllocation,
    candidates: list[dict],
    settings: Settings,
) -> str:
    """Ask the LLM to explain which candidate best matches the allocation.

    The LLM's output is advisory only; the final decision requires human
    confirmation (status = 'pending_review').
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    prompt = (
        "You are a trade reconciliation assistant.\n\n"
        f"Allocation:\n{json.dumps(_alloc_summary(alloc), indent=2)}\n\n"
        f"Booking candidates:\n{json.dumps([c['booking_data'] for c in candidates], indent=2)}\n\n"
        "Which booking best matches the allocation?  Explain your reasoning in 2–3 sentences, "
        "noting specific field agreements and discrepancies.  End with: "
        "\"Best match: <booking_id>\"."
    )
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content or ""


def _alloc_summary(alloc: ExtractedAllocation) -> dict:
    return {
        "counterparty": alloc.counterparty.value,
        "isin": alloc.isin.value,
        "trade_date": alloc.trade_date.value,
        "quantity": alloc.quantity.value,
        "price": alloc.price.value,
        "side": alloc.side.value,
        "currency": alloc.currency.value,
    }


def _allocation_id(alloc: ExtractedAllocation) -> str:
    """Derive a stable allocation identifier from its key fields."""
    parts = [
        str(alloc.isin.value or ""),
        str(alloc.trade_date.value or ""),
        str(alloc.quantity.value or ""),
        str(alloc.side.value or ""),
        str(alloc.counterparty.value or ""),
    ]
    return "alloc-" + "-".join(p[:8] for p in parts if p)
