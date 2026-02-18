"""Processor service entry point — Port 8001.

Runs an XREADGROUP consumer loop on the ``processing:queue`` Redis Stream.
Each consumed message triggers the full four-phase pipeline:
  1. Index  — parse booking Excel → Redis
  2. Extract — LLM extraction of confirmation PDF
  3. Match   — three-tier matching engine
  4. Store   — persist results to PostgreSQL, emit completion event

The worker is stateless.  Multiple instances can run in parallel; Redis
consumer groups distribute jobs automatically.
"""

import asyncio
import json
import logging
import uuid

import redis.asyncio as aioredis

from app.config import Settings, get_settings
from app.models.match_result import MatchResult
from app.processor import extractor, indexer, matcher
from app.processor.health import start_health_server
from app.schemas.events import (
    EXTRACTION_COMPLETED,
    EXTRACTION_FAILED,
    INDEXING_COMPLETED,
    INDEXING_FAILED,
    JOB_COMPLETED,
    JOB_FAILED,
    MATCHING_COMPLETED,
)
from app.services import db as db_service
from app.services import redis_client

logger = logging.getLogger(__name__)


async def run_worker(settings: Settings) -> None:
    """Main consumer loop.  Runs until cancelled."""
    await redis_client.init_redis()
    await db_service.init_db()
    await redis_client.ensure_consumer_group(settings)

    redis = await redis_client.get_redis()
    logger.info(
        "Processor worker started — consuming from '%s' as '%s'",
        settings.processing_stream,
        settings.consumer_name,
    )

    while True:
        try:
            messages = await redis.xreadgroup(
                groupname=settings.consumer_group,
                consumername=settings.consumer_name,
                streams={settings.processing_stream: ">"},
                count=settings.stream_read_count,
                block=settings.stream_block_ms,
            )
            if not messages:
                continue
            for _stream, entries in messages:
                for entry_id, fields in entries:
                    await _process_message(entry_id, fields, settings, redis)
        except aioredis.RedisError as exc:
            logger.error("Redis error in consumer loop: %s", exc)
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            break


async def _process_message(
    entry_id: str,
    fields: dict,
    settings: Settings,
    redis: aioredis.Redis,
) -> None:
    job_id = fields.get("job_id", "unknown")
    booking_key = fields.get("booking_s3_key", "")
    confirm_key = fields.get("confirm_s3_key", "")

    logger.info("[%s] Processing started", job_id)

    async with db_service._session_factory() as session:
        try:
            # ── Phase 1: Index ───────────────────────────────────────────────
            await redis_client.publish_event(
                job_id, "indexing:started", {"phase": "indexing", "message": "Parsing booking file..."}
            )
            try:
                total_bookings = await indexer.index_bookings(job_id, booking_key, settings)
                await db_service.update_job_status(
                    session, uuid.UUID(job_id), "indexing_complete",
                    total_bookings=total_bookings,
                )
                await redis_client.publish_event(
                    job_id, INDEXING_COMPLETED, {"total_bookings": total_bookings}
                )
            except Exception as exc:
                await redis_client.publish_event(job_id, INDEXING_FAILED, {"error": str(exc)})
                raise

            # ── Phase 2: Extract ─────────────────────────────────────────────
            await redis_client.publish_event(
                job_id, "extraction:started", {"phase": "extraction", "message": "Extracting allocations from PDF..."}
            )
            try:
                allocations = await extractor.extract_allocations(job_id, confirm_key, settings)
                avg_conf = (
                    sum(
                        sum(
                            getattr(alloc, f).confidence
                            for f in ("isin", "trade_date", "quantity", "side")
                        ) / 4
                        for alloc in allocations
                    ) / len(allocations)
                    if allocations else 0.0
                )
                await db_service.update_job_status(
                    session, uuid.UUID(job_id), "extraction_complete",
                    total_allocs=len(allocations),
                )
                await redis_client.publish_event(
                    job_id,
                    EXTRACTION_COMPLETED,
                    {"total_allocations": len(allocations), "confidence_avg": round(avg_conf, 3)},
                )
            except Exception as exc:
                await redis_client.publish_event(job_id, EXTRACTION_FAILED, {"error": str(exc)})
                raise

            # ── Phase 3: Match ───────────────────────────────────────────────
            await redis_client.publish_event(
                job_id, "matching:started", {"phase": "matching", "message": "Matching allocations..."}
            )
            decisions = await matcher.match_allocations(job_id, allocations, settings)

            # ── Phase 4: Store ───────────────────────────────────────────────
            matched = sum(1 for d in decisions if d.match_tier in ("exact", "fuzzy") and d.status == "auto_confirmed")
            ambiguous = sum(1 for d in decisions if d.status == "pending_review")
            unmatched = sum(1 for d in decisions if d.match_tier == "unmatched")

            for decision in decisions:
                alloc_data = next(
                    (a for a in allocations if matcher._allocation_id(a) == decision.allocation_id),
                    None,
                )
                row = MatchResult(
                    job_id=uuid.UUID(job_id),
                    allocation_id=decision.allocation_id,
                    allocation_data=alloc_data.model_dump() if alloc_data else {},
                    booking_id=decision.booking_id,
                    booking_data=decision.booking_data,
                    match_tier=decision.match_tier,
                    confidence=decision.confidence,
                    match_reasons=decision.match_reasons,
                    llm_reasoning=decision.llm_reasoning,
                    status=decision.status,
                )
                await db_service.upsert_match_result(session, row)

            await db_service.update_job_status(
                session,
                uuid.UUID(job_id),
                "completed",
                matched_count=matched,
                ambiguous_count=ambiguous,
                unmatched_count=unmatched,
            )
            await redis_client.publish_event(
                job_id,
                MATCHING_COMPLETED,
                {"matched": matched, "ambiguous": ambiguous, "unmatched": unmatched},
            )
            await redis_client.publish_event(
                job_id,
                JOB_COMPLETED,
                {"status": "success", "results_url": f"/process/{job_id}"},
            )
            logger.info("[%s] Processing complete", job_id)

        except Exception as exc:
            logger.exception("[%s] Pipeline failed: %s", job_id, exc)
            await db_service.update_job_status(
                session, uuid.UUID(job_id), "failed", error_message=str(exc)
            )
            await redis_client.publish_event(job_id, JOB_FAILED, {"error": str(exc)})

    # Acknowledge the stream message so it won't be redelivered
    await redis.xack(settings.processing_stream, settings.consumer_group, entry_id)


async def main() -> None:
    import logging as _logging
    _logging.basicConfig(level="INFO")
    settings = get_settings()
    await asyncio.gather(
        run_worker(settings),
        start_health_server(settings),
    )


if __name__ == "__main__":
    asyncio.run(main())
