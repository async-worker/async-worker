from urllib.parse import urljoin

from asyncworker.options import RouteTypes
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.sse.consumer import SSEConsumer


class SSE(SignalHandler):
    async def startup(self, app):  # type: ignore
        app[RouteTypes.SSE] = {"consumers": []}
        for route_info in app.routes_registry.sse_routes:
            for route in route_info["routes"]:
                consumer = SSEConsumer(
                    route_info=route_info,
                    url=urljoin(app.url, route),
                    username=app.user,
                    password=app.password,
                )
                app[RouteTypes.SSE]["consumers"].append(consumer)
                app.loop.create_task(consumer.start())
