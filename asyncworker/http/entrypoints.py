from typing import Callable, List

from asyncworker.entrypoints import _extract_async_callable, EntrypointInterface
from asyncworker.http import HTTPMethods
from asyncworker.routes import RoutesRegistry, HTTPRoute


def _register_http_handler(
    registry: RoutesRegistry, routes: List[str], method: HTTPMethods
) -> Callable:
    def _wrap(f):

        cb = _extract_async_callable(f)
        route = HTTPRoute(handler=cb, routes=routes, methods=[method])
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
