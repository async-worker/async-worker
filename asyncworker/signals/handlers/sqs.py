from typing import TYPE_CHECKING

from asyncworker.connections import SQSConnection
from asyncworker.options import RouteTypes
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.sqs.consumer import SQSConsumer

if TYPE_CHECKING:  # pragma: no cover
    from asyncworker.app import App  # noqa: F401


class SQS(SignalHandler):
    async def startup(self, app: "App"):
        app[RouteTypes.SQS]["consumers"] = []
        for route_info in app.routes_registry.sqs_routes:
            for queue_url in route_info.routes:
                conn: SQSConnection = app.get_connection_for_route(route_info)
                consumer = SQSConsumer(conn, queue_url)

                app[RouteTypes.SQS]["consumers"].append(consumer)
                app.loop.create_task(consumer.start())
