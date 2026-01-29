"""
RQ Worker - Background Job Processor

Run this with: python worker.py
Or with multiple workers: rq worker default processing extraction reconciliation resolution

This worker processes background jobs from Redis queues for:
- File processing
- PDF extraction
- Trade reconciliation
- Discrepancy resolution
"""

import os
import sys
import logging
from dotenv import load_dotenv
from rq import Worker, Queue
from queue.config import RedisConfig

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_worker(queue_names: list = None):
    """
    Start RQ worker listening to specified queues.

    Args:
        queue_names: List of queue names to listen to.
                    Defaults to all queues.
    """
    if queue_names is None:
        queue_names = [
            "default",
            "processing",
            "extraction",
            "reconciliation",
            "resolution",
        ]

    logger.info(f"🚀 Starting RQ Worker")
    logger.info(f"Listening to queues: {', '.join(queue_names)}")

    # Get Redis connection
    redis_conn = RedisConfig.get_redis_connection()

    # Create worker
    worker = Worker(
        queues=[Queue(name, connection=redis_conn) for name in queue_names],
        connection=redis_conn,
        name=f"worker-{os.getenv('HOSTNAME', 'default')}",
    )

    # Start worker
    try:
        logger.info("Worker started and listening for jobs...")
        worker.work()
    except KeyboardInterrupt:
        logger.info("👋 Worker shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Allow queue names as command-line arguments
    queue_names = sys.argv[1:] if len(sys.argv) > 1 else None
    run_worker(queue_names)
