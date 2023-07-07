from asyncio import Task
from typing import TYPE_CHECKING, List

from asyncworker.connections import AMQPConnection
from asyncworker.consumer import Consumer
from asyncworker.options import RouteTypes
from asyncworker.signals.handlers.base import SignalHandler

if TYPE_CHECKING:  # pragma: no cover
    from asyncworker.app import App  # noqa: F401


class RabbitMQ(SignalHandler):
    async def startup(self, app: "App") -> List[Task]:
        tasks = []

        app[RouteTypes.AMQP_RABBITMQ]["consumers"] = []
        for route_info in app.routes_registry.amqp_routes:
            conn: AMQPConnection = app.get_connection_for_route(route_info)

            consumer = Consumer(
                route_info=route_info,
                host=conn.hostname,
                port=conn.port,
                username=conn.username,
                password=conn.password,
                prefetch_count=conn.prefetch,
            )
            app[RouteTypes.AMQP_RABBITMQ]["consumers"].append(consumer)
            conn.register(consumer.queue)
            task = app.loop.create_task(consumer.start())

            tasks.append(task)

        return tasks
