from typing import TYPE_CHECKING
from urllib.parse import urljoin

from asyncworker.signal_handlers.base import SignalHandler
from asyncworker.sse.consumer import SSEConsumer


if TYPE_CHECKING:
    from asyncworker.sse.app import SSEApplication


class SSE(SignalHandler):
    async def startup(self, app: 'SSEApplication'):
        app['sse_consumers'] = []
        for route_info in app.routes_registry.sse_routes:
            for route in route_info['routes']:
                final_url = urljoin(app.url, route)
                consumer = SSEConsumer(route_info, final_url,
                                       app.user, app.password)
                app['sse_consumers'].append(consumer)
        return app['sse_consumers']
