import functools
import asyncio
from collections import UserDict
from typing import Iterable, Callable, Coroutine, Dict, Optional

from .consumer import Consumer

from asyncworker import conf
from asyncworker.options import Options, Defaultvalues, Events
from .bucket import Bucket


def entrypoint(f):
    @functools.wraps(f)
    def _(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return _

class BaseApp:
    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.routes_registry: Routes[Route, Dict] = {}

    def _build_consumers(self):
        raise NotImplementedError()

    @entrypoint
    async def run(self) -> None:
        conf.logger.info("Booting App...")
        self._on_startup.freeze()
        await self.startup()
        consumers = self._build_consumers()
        for consumer in consumers:
            self.loop.create_task(consumer.start())
        while True:
            await asyncio.sleep(10)

    async def startup(self) -> None:
        """Causes on_startup signal

        Should be called in the event loop along with the request handler.
        """
        await self._on_startup.send(self)

    async def start_http_server(self, app: 'BaseApp'):
        app.http_app = web.Application()
        for func, route in app.routes_registry.http_routes().item():
            app.http_app.add_routes(route)

        self.http_runner = web.AppRunner(app.http_app)
        await self.http_runner.setup()
        site = web.TCPSite(self.http_runner, )

    async def stop_http_server(self, app: 'BaseApp'):
        await app.http_runner.cleanup()


class App(BaseApp):
    def __init__(self, host, user, password, prefetch_count):
        super(App, self).__init__()
        self.host = host
        self.user = user
        self.password = password
        self.prefetch_count = prefetch_count

    def _build_consumers(self):
        consumers = []
        for _handler, route_info in self.routes_registry.items():
            consumers.append(Consumer(route_info, self.host, self.user, self.password, self.prefetch_count))
        return consumers

    def route(self, routes, vhost="/", options={}):
        def wrap(f):
            self.routes_registry[f] = {
                "route": routes,
                "handler": f,
                "options": {
                    "vhost": vhost,
                    "bulk_size": options.get(Options.BULK_SIZE, Defaultvalues.BULK_SIZE),
                    "bulk_flush_interval": options.get(Options.BULK_FLUSH_INTERVAL, Defaultvalues.BULK_FLUSH_INTERVAL),
                    Events.ON_SUCCESS: options.get(Events.ON_SUCCESS, Defaultvalues.ON_SUCCESS),
                    Events.ON_EXCEPTION: options.get(Events.ON_EXCEPTION, Defaultvalues.ON_EXCEPTION),
                }
            }
            return f
        return wrap

