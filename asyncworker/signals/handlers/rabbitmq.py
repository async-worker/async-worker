from typing import TYPE_CHECKING, List

from asyncworker.consumer import Consumer
from asyncworker.exceptions import InvalidRoute
from asyncworker.routes import AMQPRoute
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.rabbitmq.connection import AMQPConnection
from asyncworker.options import RouteTypes

if TYPE_CHECKING:  # pragma: no cover
    from asyncworker.app import App  # noqa: F401


class RabbitMQ(SignalHandler):
    def _get_connection_for_route(
        self, connections: List[AMQPConnection], route_info: AMQPRoute
    ):
        route_connection = route_info.options.get("connection")
        if route_connection is not None:
            connection = route_connection
        elif len(connections) > 1:
            raise InvalidRoute(
                "Invalid route definition for App. You are trying to "
                "define a RouteType.AMQP_RABBITMQ into an asyncworker.App "
                "with multiple connections without specifying which "
                "one to use."
            )
        else:
            try:
                connection = connections[0]
            except IndexError as e:
                raise InvalidRoute(
                    "Invalid route definition for App. You are trying to "
                    "define a RouteType.AMQP_RABBITMQ without an "
                    "AMQPConnection registered on App"
                ) from e
        return connection

    async def startup(self, app: "App"):
        app[RouteTypes.AMQP_RABBITMQ]["consumers"] = []
        connections: List[AMQPConnection] = app[RouteTypes.AMQP_RABBITMQ][
            "connections"
        ]
        for route_info in app.routes_registry.amqp_routes:
            connection = self._get_connection_for_route(connections, route_info)

            consumer = Consumer(
                route_info=route_info,
                host=connection.hostname,
                username=connection.username,
                password=connection.password,
                prefetch_count=connection.prefetch,
            )
            app[RouteTypes.AMQP_RABBITMQ]["consumers"].append(consumer)
            connection.register(consumer.queue)
            app.loop.create_task(consumer.start())
