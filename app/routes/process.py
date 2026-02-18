"""Process routes: job submission, SSE streaming, results, confirmations."""

import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.dependencies import AppSettings, CurrentUser, DBSession
from app.schemas.process import (
    ConfirmRequest,
    ProcessRequest,
    ProcessResponse,
    ValidationResult,
)
from app.services import db as db_service
from app.services import redis_client
from app.services.s3 import validate_s3_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/process", tags=["process"])


@router.post("", response_model=ProcessResponse, status_code=status.HTTP_200_OK)
async def submit_job(
    request: ProcessRequest,
    current_user: CurrentUser,
    session: DBSession,
    settings: AppSettings,
) -> ProcessResponse:
    """Queue a reconciliation job.

    Returns 409 if a job with the same ``dedup_key`` already exists.
    """
    user_id: str = current_user["sub"]

    # Idempotency check
    if request.dedup_key:
        existing = await db_service.get_job_by_dedup_key(session, request.dedup_key)
        if existing:
            return ProcessResponse(job_id=existing.id, status=existing.status)

    # Validate that the S3 keys actually exist in our bucket
    await validate_s3_key(request.booking_excel_s3_key, settings)
    await validate_s3_key(request.confirmation_pdf_s3_key, settings)

    job = await db_service.create_job(
        session,
        user_id=user_id,
        booking_s3_key=request.booking_excel_s3_key,
        confirm_s3_key=request.confirmation_pdf_s3_key,
        dedup_key=request.dedup_key,
    )

    # Enqueue to Redis Stream
    await redis_client.enqueue_job(
        job_id=str(job.id),
        booking_s3_key=request.booking_excel_s3_key,
        confirm_s3_key=request.confirmation_pdf_s3_key,
        settings=settings,
    )

    logger.info("Job %s queued for user %s", job.id, user_id)
    return ProcessResponse(job_id=job.id, status="queued")


@router.get("/{job_id}/stream")
async def stream_job_events(
    job_id: uuid.UUID,
    current_user: CurrentUser,
    session: DBSession,
    settings: AppSettings,
) -> StreamingResponse:
    """Server-Sent Events stream for real-time job progress.

    Clients should connect with the ``EventSource`` API.  The connection is
    held open until a ``job:completed`` or ``job:failed`` event is received.
    """
    job = await db_service.get_job(session, job_id)
    if not job or job.user_id != current_user["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    async def event_generator() -> AsyncGenerator[str, None]:
        # Read from per-job Redis event stream
        last_id = "0"
        terminal_events = {"job:completed", "job:failed"}
        while True:
            messages = await redis_client.read_job_events(
                job_id=str(job_id), last_id=last_id, settings=settings
            )
            for msg_id, fields in messages:
                last_id = msg_id
                event_name = fields.get("event", "message")
                data = fields.get("data", "{}")
                yield f"event: {event_name}\ndata: {data}\n\n"
                if event_name in terminal_events:
                    return
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{job_id}", response_model=ValidationResult)
async def get_job_results(
    job_id: uuid.UUID,
    current_user: CurrentUser,
    session: DBSession,
) -> ValidationResult:
    """Return the completed reconciliation results for a job."""
    job = await db_service.get_job(session, job_id)
    if not job or job.user_id != current_user["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.status not in ("completed", "failed"):
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED, detail="Job still processing"
        )

    return await db_service.get_validation_result(session, job_id)


@router.post("/{job_id}/confirm", status_code=status.HTTP_200_OK)
async def confirm_match(
    job_id: uuid.UUID,
    body: ConfirmRequest,
    current_user: CurrentUser,
    session: DBSession,
) -> dict:
    """Human review: confirm or reject a match decision.

    Required for all Tier 3 (LLM-assisted) matches and any ambiguous results.
    """
    job = await db_service.get_job(session, job_id)
    if not job or job.user_id != current_user["sub"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    await db_service.record_review_decision(
        session,
        result_id=body.result_id,
        decision=body.decision,
        booking_id=body.booking_id,
        reviewed_by=current_user["sub"],
    )
    return {"status": "ok"}
