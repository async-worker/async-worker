import abc
from collections import UserDict
from typing import Callable, Coroutine, Dict, List, Any, Union, Iterable

from aiohttp.web_routedef import RouteDef
from cached_property import cached_property
from pydantic import BaseModel, validator

from asyncworker.conf import settings
from asyncworker.options import DefaultValues, RouteTypes, Actions

RouteHandler = Callable[[], Coroutine]


class Model(BaseModel, abc.ABC):
    def __getitem__(self, item):
        try:
            return self.__getattr__(item)
        except AttributeError as e:
            raise KeyError from e

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.dict() == other
        return super(Model, self).__eq__(other)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class Route(Model, abc.ABC):
    """
    An abstract Model that acts like a route factory
    """

    type: RouteTypes
    handler: Any
    routes: List[str]
    default_options: dict = {}

    @staticmethod
    def factory(data: Dict) -> "Route":
        try:
            type_ = data.pop("type")
        except KeyError as e:
            raise ValueError("Routes must have a type") from e

        if type_ not in RouteTypes:
            raise ValueError(f"'{type_}' is an invalid RouteType.")

        if type_ == RouteTypes.HTTP:
            return HTTPRoute(**data)
        if type_ == RouteTypes.AMQP_RABBITMQ:
            return AMQPRoute(**data)
        if type_ == RouteTypes.SSE:
            return SSERoute(**data)


class HTTPRoute(Route):
    type: RouteTypes = RouteTypes.HTTP
    methods: List[str]

    def aiohttp_routes(self) -> Iterable[RouteDef]:
        for route in self.routes:
            for method in self.methods:
                kwargs = {"allow_head": False} if method == "GET" else {}
                yield RouteDef(
                    method=method,
                    path=route,
                    handler=self.handler,
                    kwargs=kwargs,
                )


class _AMQPRouteOptions(Model):
    bulk_size: int = DefaultValues.BULK_SIZE
    bulk_flush_interval: int = DefaultValues.BULK_FLUSH_INTERVAL
    on_success: Actions = DefaultValues.ON_SUCCESS
    on_exception: Actions = DefaultValues.ON_EXCEPTION


class AMQPRoute(Route):
    type: RouteTypes = RouteTypes.AMQP_RABBITMQ
    vhost: str = settings.AMQP_DEFAULT_VHOST
    options: _AMQPRouteOptions


class _SSERouteOptions(Model):
    bulk_size: int = DefaultValues.BULK_SIZE
    bulk_flush_interval: int = DefaultValues.BULK_FLUSH_INTERVAL
    headers: Dict[str, str] = {}


class SSERoute(Route):
    type: RouteTypes = RouteTypes.SSE
    headers: Dict[str, str] = {}
    options: _SSERouteOptions = _SSERouteOptions()

    @validator("options", pre=True, whole=True, always=True)
    def add_default_headers(cls, v, values, **kwargs):
        headers = {
            **values.pop("headers", {}),
            **values.pop("default_options", {}).get("headers", {}),
        }
        v["headers"] = headers

        return v


class RoutesRegistry(UserDict):
    @cached_property
    def http_routes(self) -> Iterable[RouteDef]:
        routes = []
        for handler, route in self.items():
            if isinstance(route, HTTPRoute):
                routes.extend(route.aiohttp_routes())
        return routes

    @cached_property
    def amqp_routes(self) -> Iterable[AMQPRoute]:
        return tuple((r for r in self.values() if isinstance(r, AMQPRoute)))

    @cached_property
    def sse_routes(self) -> Iterable[SSERoute]:
        return tuple((r for r in self.values() if isinstance(r, SSERoute)))

    def __setitem__(self, key: RouteHandler, value: Union[Dict, Route]):
        if not isinstance(value, Route):
            route = Route.factory({"handler": key, **value})
        else:
            route = value
        super(RoutesRegistry, self).__setitem__(key, route)

    def add_route(self, route: Union[Dict, Route]) -> Route:
        if not isinstance(route, Route):
            route = Route.factory(route)

        self[route.handler] = route
        return route

    def route_for(self, handler: RouteHandler) -> Route:
        return self[handler]
