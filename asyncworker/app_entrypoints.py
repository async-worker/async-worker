from abc import ABC
from asyncio import iscoroutinefunction
from typing import Generic, TypeVar, List, Optional

import asyncworker
from asyncworker.routes import (
    RoutesRegistry,
    HTTPRoute,
    RouteHandler,
    AMQPRoute,
    _AMQPRouteOptions,
)

T = TypeVar("T")


def _extract_async_callable(handler) -> RouteHandler:

    cb = handler

    if not iscoroutinefunction(cb):
        try:
            cb = handler.__call__
            if not iscoroutinefunction(cb):
                raise TypeError(f"handler must be async: {cb}")
        except AttributeError as e:
            raise TypeError(f"Object passed as handler is not callable: {cb}")

    return cb


def _register_http_handler(
    registry: RoutesRegistry, routes: List[str], method: str
):
    def _wrap(f):

        cb = _extract_async_callable(f)
        route = HTTPRoute(handler=cb, routes=routes, methods=[method])
        registry.add_http_route(route)

        return f

    return _wrap


def _register_amqp_handler(
    registry: RoutesRegistry,
    routes: List[str],
    options: Optional[_AMQPRouteOptions],
):
    def _wrap(f):

        cb = _extract_async_callable(f)
        route = AMQPRoute(handler=cb, routes=routes, options=options)
        registry.add_amqp_route(route)

        return f

    return _wrap


class EntrypointInterface(ABC, Generic[T]):
    def __init__(self, app: "asyncworker.App") -> None:
        self.app = app


class HTTPEntryPointImpl(EntrypointInterface):
    def route(self, routes: List[str], method: str):
        return _register_http_handler(self.app.routes_registry, routes, method)

    def get(self, routes: List[str]):
        return self.route(routes=routes, method="GET")


class AMQPRouteEntryPointImpl(EntrypointInterface):
    def consume(
        self,
        routes: List[str],
        options: Optional[_AMQPRouteOptions] = _AMQPRouteOptions(),
    ):
        return _register_amqp_handler(self.app.routes_registry, routes, options)
