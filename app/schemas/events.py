"""Pydantic schemas for Redis / SSE stream events."""

from typing import Any

from pydantic import BaseModel


class StreamEvent(BaseModel):
    """A single SSE event payload.

    The ``event`` field maps to the SSE ``event:`` line.
    The ``data`` dict is JSON-serialised as the ``data:`` line.
    """

    event: str
    data: dict[str, Any]


# ── Canonical event names ────────────────────────────────────────────────────
# Emitted by the Processor and relayed by the API's SSE hub.

INDEXING_STARTED = "indexing:started"
INDEXING_COMPLETED = "indexing:completed"
INDEXING_FAILED = "indexing:failed"

EXTRACTION_STARTED = "extraction:started"
EXTRACTION_COMPLETED = "extraction:completed"
EXTRACTION_FAILED = "extraction:failed"

MATCHING_STARTED = "matching:started"
MATCHING_COMPLETED = "matching:completed"

JOB_COMPLETED = "job:completed"
JOB_FAILED = "job:failed"
