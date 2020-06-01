from aiohttp import web
from prometheus_client import generate_latest

from asyncworker.metrics.registry import REGISTRY


async def metrics_route_handler(r: web.Request) -> web.Response:
    response = web.Response(
        body=generate_latest(registry=REGISTRY), content_type="text/plain"
    )
    return response
