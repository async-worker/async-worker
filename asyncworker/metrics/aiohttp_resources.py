from aiohttp import web

from asyncworker.metrics.registry import REGISTRY
from prometheus_client import generate_latest


async def metrics_route_handler() -> web.Response:
    response = web.Response(
        body=generate_latest(registry=REGISTRY), content_type="text/plain"
    )
    return response
