"""Redis connection pool and Redis Streams helpers.

The Redis Stream ``processing:queue`` is the sole contract between the API
service and the Processor service.  The API enqueues jobs and reads per-job
event streams; the Processor consumes jobs and writes events.
"""

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def init_redis() -> None:
    global _redis
    settings = get_settings()
    _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await _redis.ping()
    logger.info("Redis connection established")


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency — yields the shared Redis connection."""
    if _redis is None:
        raise RuntimeError("Redis not initialised — call init_redis() at startup")
    return _redis


# ── Stream helpers ───────────────────────────────────────────────────────────


async def enqueue_job(
    job_id: str,
    booking_s3_key: str,
    confirm_s3_key: str,
    settings: Settings,
) -> str:
    """XADD a job to the processing queue stream.  Returns the stream entry ID."""
    redis = await get_redis()
    entry_id = await redis.xadd(
        settings.processing_stream,
        {
            "job_id": job_id,
            "booking_s3_key": booking_s3_key,
            "confirm_s3_key": confirm_s3_key,
        },
    )
    logger.debug("Enqueued job %s → stream entry %s", job_id, entry_id)
    return entry_id


async def publish_event(job_id: str, event: str, data: dict[str, Any]) -> None:
    """XADD an event to the per-job event stream (read by the SSE hub)."""
    redis = await get_redis()
    stream_key = f"job:{job_id}:events"
    await redis.xadd(
        stream_key,
        {"event": event, "data": json.dumps(data)},
    )
    # Expire the event stream 24 h after last write
    await redis.expire(stream_key, 86400)


async def read_job_events(
    job_id: str,
    last_id: str,
    settings: Settings,
) -> list[tuple[str, dict]]:
    """XREAD new entries from a per-job event stream since ``last_id``."""
    redis = await get_redis()
    stream_key = f"job:{job_id}:events"
    result = await redis.xread({stream_key: last_id}, block=500, count=100)
    if not result:
        return []
    _, entries = result[0]
    return [(entry_id, fields) for entry_id, fields in entries]


async def set_job_status(job_id: str, status: str) -> None:
    redis = await get_redis()
    await redis.setex(f"job:{job_id}:status", 86400, status)


async def get_job_status(job_id: str) -> str | None:
    redis = await get_redis()
    return await redis.get(f"job:{job_id}:status")


async def ensure_consumer_group(settings: Settings) -> None:
    """Create the consumer group on the processing stream if it doesn't exist."""
    redis = await get_redis()
    try:
        await redis.xgroup_create(
            settings.processing_stream,
            settings.consumer_group,
            id="0",
            mkstream=True,
        )
        logger.info("Consumer group '%s' created", settings.consumer_group)
    except aioredis.ResponseError as exc:
        if "BUSYGROUP" in str(exc):
            logger.debug("Consumer group '%s' already exists", settings.consumer_group)
        else:
            raise
