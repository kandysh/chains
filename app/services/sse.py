"""SSE hub — thin wrapper kept for future fanout needs.

Currently the SSE stream is implemented directly in ``routes/process.py`` by
reading the per-job Redis event stream.  This module is the home for any
shared SSE utilities (heartbeat, connection tracking, etc.) as the platform
scales to multiple API instances.
"""

import asyncio
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Heartbeat interval in seconds — keeps the connection alive through proxies
HEARTBEAT_INTERVAL = 15


async def heartbeat_generator() -> AsyncGenerator[str, None]:
    """Yield SSE comment lines as a keepalive heartbeat."""
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        yield ": heartbeat\n\n"
