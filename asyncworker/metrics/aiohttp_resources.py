from http import HTTPStatus
from typing import Callable, Awaitable

from aiohttp import web
from aiohttp.web_middlewares import middleware
from prometheus_client import generate_latest

from asyncworker import metrics
from asyncworker.metrics.registry import REGISTRY
from asyncworker.time import perf_counter_ms as now

_Handler = Callable[[web.Request], Awaitable[web.Response]]


@middleware
async def http_metrics_middleware(request: web.Request, handler: _Handler):
    start = now()
    try:
        metrics.requests_in_progress.labels(
            method=request.method, path=request.path
        ).inc()
        response = await handler(request)
        metrics.response_size.labels(
            method=request.method, path=request.path
        ).observe(response.content_length)
        metrics.request_duration.labels(
            method=request.method, path=request.path, status=response.status
        ).observe(now() - start)

        return response
    except web.HTTPException as e:
        metrics.request_duration.labels(
            method=request.method, path=request.path, status=e.status
        ).observe(now() - start)
        metrics.response_size.labels(
            method=request.method, path=request.path
        ).observe(e.content_length)
        raise e
    except Exception as e:
        metrics.request_duration.labels(
            method=request.method,
            path=request.path,
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        ).observe(now() - start)
        raise e
    finally:
        metrics.requests_in_progress.labels(
            method=request.method, path=request.path
        ).dec()


async def metrics_route_handler(request: web.Request) -> web.Response:
    response = web.Response(
        body=generate_latest(registry=REGISTRY), content_type="text/plain"
    )
    return response
