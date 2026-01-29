"""
API Routes - SKELETON
IMPLEMENT THE TODOs

FastAPI routes for the trade confirmation system.
"""

import os
from typing import List
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import (
    get_db,
    Confirmation,
    HumanReviewTask,
    PendingAlias,
    ConfirmationStatus,
)
from api.dependencies import get_orchestrator
from orchestrator import AgenticOrchestrator
from utils.helpers import generate_confirmation_id, sanitize_filename
from models.schemas import ConfirmationResponse
from utils.logging_config import get_logger
from queue.config import get_queue
from queue.tasks import process_confirmation
from storage import get_storage

logger = get_logger(__name__)
router = APIRouter()


@router.post("/confirmations/process")
async def process_confirmation_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF and start processing it asynchronously via RQ.

    Returns immediately with a confirmation ID. Processing happens in background
    via Redis Queue worker.

    Args:
        file: PDF file upload
        db: Database session (injected)

    Returns:
        {
            'confirmation_id': str,
            'job_id': str,
            'status': 'queued',
            'message': str
        }
    """
    logger.info(f"Received file upload: {file.filename}")

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    # Generate confirmation ID
    confirmation_id = generate_confirmation_id()

    # Read file data
    file_data = await file.read()

    # Store file using storage backend
    storage = get_storage()
    storage_path = f"confirmations/{confirmation_id}/{sanitize_filename(file.filename)}"

    try:
        storage.put(storage_path, file_data)
        logger.info(f"File stored at: {storage_path}")
    except Exception as e:
        logger.error(f"Failed to store file: {str(e)}")
        raise HTTPException(500, f"Failed to store file: {str(e)}")

    # Create database record
    confirmation = Confirmation(
        id=confirmation_id,
        pdf_filename=file.filename,
        status=ConfirmationStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(confirmation)
    db.commit()
    db.refresh(confirmation)

    # Queue the processing job
    try:
        queue = get_queue("processing")
        job = queue.enqueue(
            process_confirmation,
            confirmation_id=confirmation_id,
            file_path=storage_path,
            metadata={"original_filename": file.filename},
            job_timeout="10h",
        )

        logger.info(f"Queued processing job {job.id} for confirmation {confirmation_id}")

        return {
            "confirmation_id": confirmation_id,
            "job_id": job.id,
            "status": "queued",
            "message": "Processing started. Check status with GET /api/confirmations/{confirmation_id}",
        }

    except Exception as e:
        logger.error(f"Failed to queue processing job: {str(e)}")
        # Update confirmation status to failed
        confirmation.status = ConfirmationStatus.FAILED
        db.commit()
        raise HTTPException(500, f"Failed to queue processing: {str(e)}")


@router.get("/confirmations/{confirmation_id}")
async def get_confirmation(confirmation_id: str, db: Session = Depends(get_db)):
    """
    Get confirmation status and results.

    Args:
        confirmation_id: Confirmation ID to retrieve
        db: Database session (injected)

    Returns:
        ConfirmationResponse with full details

    TODO: Implement this endpoint
    Steps:
    1. Query database:
       - confirmation = db.query(Confirmation).filter(Confirmation.id == confirmation_id).first()
    2. If not found:
       - raise HTTPException(404, "Confirmation not found")
    3. Return confirmation details:
       - Convert to ConfirmationResponse
       - Include all relevant fields

    HINT: Use ConfirmationResponse schema from models.schemas
    """
    logger.info(f"Getting confirmation: {confirmation_id}")

    # TODO: Query database for confirmation
    # TODO: If not found, raise 404
    # TODO: Return confirmation details
    pass


@router.get("/confirmations")
async def list_confirmations(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    List all confirmations with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session (injected)

    Returns:
        List of confirmation summaries

    TODO: Implement this endpoint
    Steps:
    1. Query database:
       - confirmations = db.query(Confirmation).offset(skip).limit(limit).all()
    2. Convert to list of dicts:
       - For each confirmation, create summary dict
    3. Return list

    HINT: Return lightweight summaries, not full details
    """
    logger.info(f"Listing confirmations (skip={skip}, limit={limit})")

    # TODO: Query database with pagination
    # TODO: Convert to list of summary dicts
    # TODO: Return list
    pass


@router.get("/human-review")
async def get_review_queue(
    status: str = "pending", db: Session = Depends(get_db)
):
    """
    Get human review tasks queue.

    Args:
        status: Filter by status (pending, in_review, approved, rejected)
        db: Database session (injected)

    Returns:
        List of review tasks

    TODO: Implement this endpoint
    Steps:
    1. Query HumanReviewTask table:
       - Filter by status if provided
       - Order by created_at (oldest first)
    2. Convert to list of dicts
    3. Return list

    HINT: Join with Confirmation to include context
    """
    logger.info(f"Getting review queue (status={status})")

    # TODO: Query HumanReviewTask table
    # TODO: Filter by status
    # TODO: Convert to list of dicts
    # TODO: Return list
    pass


@router.post("/aliases")
async def add_alias(
    field: str,
    from_value: str,
    to_value: str,
    counterparty_id: str = None,
    db: Session = Depends(get_db),
):
    """
    Manually add an alias.

    Args:
        field: Field name (e.g., 'counterparty', 'rate')
        from_value: Value to alias from
        to_value: Canonical value to alias to
        counterparty_id: Optional counterparty ID for counterparty-specific alias
        db: Database session (injected)

    Returns:
        Success message

    TODO: Implement this endpoint
    Steps:
    1. Get alias_db from dependencies
    2. Add alias:
       - alias_db.add_alias(field, from_value, to_value, counterparty_id)
    3. Also create PendingAlias record for audit:
       - Create with status='APPROVED'
    4. Commit to database
    5. Return success message

    HINT: Use get_alias_db() from dependencies
    """
    logger.info(f"Adding alias: {field} {from_value} -> {to_value}")

    # TODO: Get alias_db
    # TODO: Add alias
    # TODO: Create PendingAlias record
    # TODO: Return success
    pass


@router.get("/aliases/{field}")
async def get_aliases(field: str):
    """
    Get all aliases for a specific field.

    Args:
        field: Field name (e.g., 'counterparty', 'rate')

    Returns:
        Dictionary of aliases for that field

    TODO: Implement this endpoint
    Steps:
    1. Get alias_db from dependencies
    2. Get aliases:
       - aliases = alias_db.get_all_aliases(field)
    3. Return aliases

    HINT: Use get_alias_db() from dependencies
    """
    logger.info(f"Getting aliases for field: {field}")

    # TODO: Get alias_db
    # TODO: Get aliases for field
    # TODO: Return aliases
    pass


@router.get("/aliases")
async def get_all_aliases():
    """
    Get all aliases (all fields).

    Returns:
        Dictionary of all aliases

    TODO: Implement this endpoint
    Steps:
    1. Get alias_db from dependencies
    2. Get all aliases:
       - aliases = alias_db.get_all_aliases()
    3. Return aliases
    """
    logger.info("Getting all aliases")

    # TODO: Get alias_db
    # TODO: Get all aliases
    # TODO: Return aliases
    pass


# Queue/Job Monitoring Endpoints


@router.get("/queue/status")
async def get_queue_status():
    """
    Get status of all RQ queues.

    Returns:
        Queue status with job counts
    """
    try:
        from queue.config import get_all_queues

        queues = get_all_queues()
        status = {}

        for queue_name, queue in queues.items():
            status[queue_name] = {
                "count": len(queue),
                "started": len(queue.started_job_registry),
                "finished": len(queue.finished_job_registry),
                "failed": len(queue.failed_job_registry),
            }

        return {
            "status": "ok",
            "queues": status,
        }
    except Exception as e:
        logger.error(f"Failed to get queue status: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get status of a specific job.

    Args:
        job_id: RQ job ID

    Returns:
        Job status and metadata
    """
    try:
        from queue.config import RedisConfig
        from rq.job import Job

        redis_conn = RedisConfig.get_redis_connection()
        job = Job.fetch(job_id, connection=redis_conn)

        return {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result,
            "exc_info": job.exc_info,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "ended_at": job.ended_at,
        }
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(404, f"Job not found: {job_id}")
