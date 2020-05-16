from typing import Callable, Awaitable

from aiohttp import web
from aiohttp.web_middlewares import middleware

from asyncworker import metrics
from asyncworker.conf import default_timer
from asyncworker.metrics.registry import generate_latest, REGISTRY

_Handler = Callable[[web.Request], Awaitable[web.Response]]


async def metrics_route_handler(request: web.Request) -> web.Response:
    response = web.Response(
        body=generate_latest(registry=REGISTRY), content_type="text/plain"
    )
    return response
