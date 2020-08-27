from typing import List, Optional

from asyncworker.entrypoints import EntrypointInterface, _extract_async_callable
from asyncworker.routes import AMQPRouteOptions, RoutesRegistry, AMQPRoute


def _register_amqp_handler(
    registry: RoutesRegistry,
    routes: List[str],
    options: Optional[AMQPRouteOptions],
):
    def _wrap(f):

        cb = _extract_async_callable(f)
        route = AMQPRoute(handler=cb, routes=routes, options=options)
        registry.add_amqp_route(route)

        return f

    return _wrap


class AMQPRouteEntryPointImpl(EntrypointInterface):
    def consume(
        self,
        routes: List[str],
        options: Optional[AMQPRouteOptions] = AMQPRouteOptions(),
    ):
        return _register_amqp_handler(self.app.routes_registry, routes, options)
