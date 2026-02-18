"""Minimal health-check HTTP server for the Processor service (Port 8001).

Exposed only to internal orchestration tooling (load balancers, k8s probes).
Not reachable from the client network.
"""

import asyncio
import logging

from aiohttp import web

logger = logging.getLogger(__name__)


async def _handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "processor"})


async def start_health_server(settings) -> None:
    """Start a lightweight aiohttp server on ``processor_port``."""
    app = web.Application()
    app.router.add_get("/health", _handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.processor_port)
    await site.start()
    logger.info("Processor health check listening on port %d", settings.processor_port)
    # Keep running forever alongside the consumer loop
    await asyncio.Event().wait()
