from urllib.parse import urljoin

from asyncworker.connections import SSEConnection
from asyncworker.options import RouteTypes
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.sse.consumer import SSEConsumer


class SSE(SignalHandler):
    async def startup(self, app):  # type: ignore
        app[RouteTypes.SSE]["consumers"] = []
        for route_info in app.routes_registry.sse_routes:
            conn: SSEConnection = app.get_connection_for_route(route_info)
            for route in route_info["routes"]:
                consumer = SSEConsumer(
                    route_info=route_info,
                    url=urljoin(conn.url, route),
                    username=conn.user,
                    password=conn.password,
                )
                app[RouteTypes.SSE]["consumers"].append(consumer)
                app.loop.create_task(consumer.start())
