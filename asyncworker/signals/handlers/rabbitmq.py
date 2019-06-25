from typing import TYPE_CHECKING

from asyncworker.consumer import Consumer
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.rabbitmq.connection import AMQPConnection
from asyncworker.options import RouteTypes

if TYPE_CHECKING:  # pragma: no cover
    from asyncworker.app import App  # noqa: F401


class RabbitMQ(SignalHandler):
    async def startup(self, app: "App"):
        app[RouteTypes.AMQP_RABBITMQ]["consumers"] = []
        for route_info in app.routes_registry.amqp_routes:
            conn: AMQPConnection = app.get_connection_for_route(route_info)

            consumer = Consumer(
                route_info=route_info,
                host=conn.hostname,
                username=conn.username,
                password=conn.password,
                prefetch_count=conn.prefetch,
            )
            app[RouteTypes.AMQP_RABBITMQ]["consumers"].append(consumer)
            conn.register(consumer.queue)
            app.loop.create_task(consumer.start())
