import asyncio
from signal import Signals
from collections import MutableMapping
from typing import Iterable, Callable, Coroutine, Dict, Any, Optional

from asyncworker.conf import logger
from asyncworker.exceptions import InvalidRoute
from asyncworker.signals.handlers.http import HTTPServer
from asyncworker.signals.handlers.rabbitmq import RabbitMQ
from asyncworker.routes import RoutesRegistry, Route
from asyncworker.options import RouteTypes, Options, DefaultValues
from asyncworker.signals.base import Signal, Freezable
from asyncworker.signals.handlers.sse import SSE
from asyncworker.task_runners import ScheduledTaskRunner
from asyncworker.utils import entrypoint


class App(MutableMapping, Freezable):
    handlers = (RabbitMQ(), HTTPServer(), SSE())
    shutdown_os_signals = (Signals.SIGINT, Signals.SIGTERM)

    def __init__(self, connections: Optional[Iterable] = None) -> None:
        if connections is None:
            connections = []
        self.loop = asyncio.get_event_loop()
        self.routes_registry = RoutesRegistry()
        self.default_route_options: dict = {}

        self._state: Dict[Any, Any] = self._get_initial_state()
        self._frozen = False
        self._add_connections(connections)

        self._on_startup: Signal = Signal(self)
        self._on_shutdown: Signal = Signal(self)

        for handler in self.handlers:
            self._on_startup.append(handler.startup)
            self._on_shutdown.append(handler.shutdown)

        for signal in self.shutdown_os_signals:
            self.loop.add_signal_handler(signal, self.shutdown)

    def _check_frozen(self):
        if self.frozen():
            raise RuntimeError(
                "You shouldnt change the state of started " "application"
            )

    def _get_initial_state(self) -> Dict[Any, Any]:
        return {route_type: {} for route_type in RouteTypes}

    def _add_connections(self, connections):
        for route_type in RouteTypes:
            self[route_type]["connections"] = []
        for connection in connections:
            self[connection.route_type]["connections"].append(connection)

    def frozen(self) -> bool:
        return self._frozen

    async def freeze(self) -> None:
        self._frozen = True

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._check_frozen()
        self._state[key] = value

    def __delitem__(self, key):
        self._check_frozen()
        del self._state[key]

    def __len__(self):
        return len(self._state)

    def __iter__(self):
        return iter(self._state)

    @entrypoint
    async def run(self):
        await logger.debug({"event": "Booting App..."})
        await self.startup()

        while True:
            await asyncio.sleep(10)

    async def startup(self):
        """
        Causes on_startup signal

        Should be called in the event loop along with the request handler.
        """
        await self._on_startup.send(self)

    def shutdown(self) -> asyncio.Future:
        """
        Schedules an on_startup signal

        Is called automatically when the application receives
        a SIGINT or SIGTERM
        """
        return asyncio.ensure_future(self._on_shutdown.send(self))

    def route(
        self,
        routes: Iterable[str],
        type: RouteTypes,
        options: dict = None,
        **kwargs,
    ):
        if options is None:
            options = {}
        if not isinstance(type, RouteTypes):
            raise TypeError(
                f"type parameter is not a valid RouteTypes." f" Found: '{type}'"
            )

        def wrapper(f):
            self.routes_registry[f] = {
                "type": type,
                "routes": routes,
                "handler": f,
                "options": options,
                "default_options": self.default_route_options,
                **kwargs,
            }
            return f

        return wrapper

    def run_on_startup(self, coro: Callable[["App"], Coroutine]) -> None:
        """
        Registers a coroutine to be awaited for during app startup
        """
        self._on_startup.append(coro)

    def run_on_shutdown(self, coro: Callable[["App"], Coroutine]) -> None:
        """
        Registers a coroutine to be awaited for during app shutdown
        """
        self._on_shutdown.append(coro)

    def run_every(self, seconds: int, options: Dict = None):
        """
        Registers a coroutine to be called with a given interval
        """
        if options is None:
            options = {}

        max_concurrency = options.get(
            Options.MAX_CONCURRENCY, DefaultValues.RUN_EVERY_MAX_CONCURRENCY
        )

        def wrapper(task: Callable[..., Coroutine]):
            runner = ScheduledTaskRunner(
                seconds=seconds,
                task=task,
                app=self,
                max_concurrency=max_concurrency,
            )
            self._on_startup.append(runner.start)
            self._on_shutdown.append(runner.stop)
            if "task_runners" not in self:
                self["task_runners"] = []
            self["task_runners"].append(runner)

            return task

        return wrapper

    def get_connection_for_route(self, route_info: Route):
        route_connection = route_info.options.get("connection")
        connections = self[route_info.type]["connections"]
        if route_connection is not None:
            connection = route_connection
        elif len(connections) > 1:
            raise InvalidRoute(
                f"Invalid route definition for App. You are trying to "
                f"define a {route_info.type} into an asyncworker.App "
                f"with multiple connections without specifying which "
                f"one to use."
            )
        else:
            try:
                connection = connections[0]
            except IndexError as e:
                raise InvalidRoute(
                    f"Invalid route definition for App. You are trying to "
                    f"define a {route_info.type} without an "
                    f"Connection registered on App"
                ) from e
        return connection
