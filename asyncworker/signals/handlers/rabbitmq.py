from typing import TYPE_CHECKING, List

from asyncworker.consumer import Consumer
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.rabbitmq.connection import AMQPConnection
from asyncworker.options import RouteTypes

if TYPE_CHECKING:  # pragma: no cover
    from asyncworker.app import App  # noqa: F401


class RabbitMQ(SignalHandler):
    async def startup(self, app: "App"):
        app[RouteTypes.AMQP_RABBITMQ]["consumers"] = []
        connections: List[AMQPConnection] = app[RouteTypes.AMQP_RABBITMQ][
            "connections"
        ]
        for route_info in app.routes_registry.amqp_routes:
            try:
                connection = connections[0]
            except IndexError as e:
                raise ValueError(
                    "Invalid route definition for App. You are trying to "
                    "define a RouteType.AMQP_RABBITMQ without an "
                    "AMQPConnection registered on App."
                ) from e

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
