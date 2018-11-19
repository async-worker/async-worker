from typing import TYPE_CHECKING

from asyncworker.consumer import Consumer
from asyncworker.signals.handlers.base import SignalHandler

if TYPE_CHECKING:  # pragma: no cover
    from asyncworker import App


class RabbitMQ(SignalHandler):
    async def startup(self, app: 'App'):
        app['consumers'] = []
        for route_info in app.routes_registry.amqp_routes:
            consumer = Consumer(route_info, app.host, app.user,
                                app.password, app.prefetch_count)
            app['consumers'].append(consumer)
            app.loop.create_task(consumer.start())
