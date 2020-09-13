from typing import List, Optional

from asyncworker import conf
from asyncworker.connections import SQSConnection
from asyncworker.entrypoints import EntrypointInterface, _extract_async_callable
from asyncworker.routes import AMQPRouteOptions, RoutesRegistry, SQSRoute


def _register_handler(
    registry: RoutesRegistry,
    routes: List[str],
    connection: Optional[SQSConnection],
    options: Optional[AMQPRouteOptions],
):
    def _wrap(f):

        cb = _extract_async_callable(f)
        route = SQSRoute(
            handler=cb, routes=routes, connection=connection, options=options
        )
        registry.add_sqs_route(route)

        return f

    return _wrap


class SQSRouteEntryPointImpl(EntrypointInterface):
    def consume(
        self,
        routes: List[str],
        connection: Optional[SQSConnection] = None,
        options: Optional[AMQPRouteOptions] = AMQPRouteOptions(),
    ):
        return _register_handler(
            self.app.routes_registry, routes, connection, options
        )
