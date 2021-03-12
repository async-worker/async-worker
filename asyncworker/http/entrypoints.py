from typing import Callable, List, Type, get_type_hints

from asyncworker.entrypoints import _extract_async_callable, EntrypointInterface
from asyncworker.http import HTTPMethods
from asyncworker.http.types import PathParam
from asyncworker.http.wrapper import RequestWrapper
from asyncworker.routes import RoutesRegistry, HTTPRoute, call_http_handler
from asyncworker.typing import get_origin, get_args
from asyncworker.utils import get_handler_original_typehints


class PathParamSpec:
    def __init__(self, name, base: Type):
        self.name = name
        self.base = base


def _parse_path(f):
    handler_type_hints = get_handler_original_typehints(f)
    path_params = [
        PathParamSpec(name=name, base=_type)
        for name, _type in handler_type_hints.items()
        if get_origin(handler_type_hints[name]) is PathParam
    ]

    async def _wrap(wrapper: RequestWrapper):
        for p in path_params:
            typed_val = await p.base.from_request(
                request=wrapper, arg_name=p.name, arg_type=get_args(p.base)[0]
            )
            wrapper.types_registry.set(typed_val, p.base, param_name=p.name)
        return await call_http_handler(wrapper, f)

    return _wrap


def _register_http_handler(
    registry: RoutesRegistry, routes: List[str], method: HTTPMethods
) -> Callable:
    def _wrap(f):

        cb = _extract_async_callable(f)

        cb_with_parse_path = _parse_path(cb)
        route = HTTPRoute(
            handler=cb_with_parse_path, routes=routes, methods=[method]
        )
        registry.add_http_route(route)

        return f

    return _wrap


class HTTPEntryPointImpl(EntrypointInterface):
    def _route(self, routes: List[str], method: HTTPMethods) -> Callable:
        return _register_http_handler(self.app.routes_registry, routes, method)

    def get(self, routes: List[str]) -> Callable:
        return self._route(routes=routes, method=HTTPMethods.GET)

    def head(self, routes: List[str]) -> Callable:
        return self._route(routes=routes, method=HTTPMethods.HEAD)

    def delete(self, routes: List[str]) -> Callable:
        return self._route(routes=routes, method=HTTPMethods.DELETE)

    def patch(self, routes: List[str]) -> Callable:
        return self._route(routes=routes, method=HTTPMethods.PATCH)

    def post(self, routes: List[str]) -> Callable:
        return self._route(routes=routes, method=HTTPMethods.POST)

    def put(self, routes: List[str]) -> Callable:
        return self._route(routes=routes, method=HTTPMethods.PUT)
