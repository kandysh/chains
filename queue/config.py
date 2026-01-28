"""Redis and RQ configuration."""

import os
from redis import Redis
from rq import Queue
from functools import lru_cache


class RedisConfig:
    """Redis configuration."""

    @staticmethod
    def get_redis_connection() -> Redis:
        """Get or create Redis connection."""
        return Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True,
            password=os.getenv("REDIS_PASSWORD"),
        )


@lru_cache()
def get_queue(queue_name: str = "default") -> Queue:
    """
    Get or create RQ queue.

    Args:
        queue_name: Name of the queue

    Returns:
        RQ Queue instance
    """
    redis_conn = RedisConfig.get_redis_connection()
    return Queue(queue_name, connection=redis_conn)


def get_all_queues() -> dict:
    """Get all queue instances."""
    return {
        "default": get_queue("default"),
        "processing": get_queue("processing"),
        "extraction": get_queue("extraction"),
        "reconciliation": get_queue("reconciliation"),
        "resolution": get_queue("resolution"),
    }
