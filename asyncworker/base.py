import asyncio
from signal import Signals
from collections import MutableMapping
from typing import Iterable, Tuple, Callable, Coroutine, Dict, Optional, Set, \
    List

from cached_property import cached_property

from asyncworker.conf import logger
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.routes import RoutesRegistry
from asyncworker.options import RouteTypes, Options
from asyncworker.signals.base import Signal, Freezable
from asyncworker.utils import entrypoint


class BaseApp(MutableMapping, Freezable):
    handlers: Tuple[SignalHandler, ...]
    shutdown_os_signals = (Signals.SIGINT, Signals.SIGTERM)

    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.routes_registry = RoutesRegistry()
        self.default_route_options: dict = {}

        self._state: dict = {}
        self._frozen = False
        self._on_startup: Signal = Signal(self)
        self._on_shutdown: Signal = Signal(self)

        for handler in self.handlers:
            self._on_startup.append(handler.startup)
            self._on_shutdown.append(handler.shutdown)

        for signal in self.shutdown_os_signals:
            self.loop.add_signal_handler(signal, self.shutdown)

    def _check_frozen(self):
        if self.frozen():
            raise RuntimeError("You shouldnt change the state of started "
                               "application")

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
        logger.info("Booting App...")
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

        Is called automatically when the application receives a SIGINT or SIGTERM
        """
        return asyncio.ensure_future(self._on_shutdown.send(self))

    def route(self,
              routes: Iterable[str],
              type: RouteTypes,
              options: dict=None,
              **kwargs):
        if options is None:
            options = {}
        if not isinstance(type, RouteTypes):
            raise TypeError(f"type parameter is not a valid RouteTypes."
                            f" Found: '{type}'")

        def wrapper(f):
            self.routes_registry[f] = {
                'type': type,
                'routes': routes,
                'handler': f,
                'options': options,
                'default_options': self.default_route_options,
                **kwargs
            }
            return f
        return wrapper

    def run_on_startup(self, coro: Callable[['BaseApp'], Coroutine]) -> None:
        """
        Registers a coroutine to be awaited for during app startup
        """
        self._on_startup.insert(0, coro)

    def run_on_shutdown(self, coro: Callable[['BaseApp'], Coroutine]) -> None:
        """
        Registers a coroutine to be awaited for during app shutdown
        """
        self._on_shutdown.append(coro)

    def run_every(self, seconds: int, options: Optional[Dict] = None):
        """
        Registers a coroutine to be called with a given interval
        """
        def wrapper(task: Callable[..., Coroutine]):
            runner = IntervaledTaskRunner(seconds, task, options)
            self._task_runners.append(runner)
            return task

        return wrapper


class IntervaledTaskRunner:
    def __init__(
        self,
        seconds: int,
        task: Callable[..., Coroutine],
        options: Optional[Dict] = None,
    ):
        self.seconds = seconds
        self.options = options or {}
        self.task = task
        self.running_tasks: Set[asyncio.Task] = set()
        self.task_is_done_event = asyncio.Event()
        self._keep_running = True
        self._started = False

    @cached_property
    def max_concurrency(self) -> Optional[int]:
        return self.options.get(Options.MAX_CONCURRENCY)

    async def can_dispatch_task(self) -> bool:
        if not self.max_concurrency:
            return True

        if len(self.running_tasks) < self.max_concurrency:
            return True

        if await self.task_is_done_event.wait():
            return True

    async def _wrapped_task(self):
        try:
            await self.task()
        finally:
            self.task_is_done_event.set()
            self.running_tasks.remove(asyncio.current_task())

    def start(self) -> asyncio.Task:
        self._started = True
        return asyncio.ensure_future(self._run())

    async def stop(self):
        self._keep_running = False
        await asyncio.gather(*self.running_tasks)

    async def _run(self):
        while self._keep_running:
            if await self.can_dispatch_task():
                task = asyncio.ensure_future(self._wrapped_task())
                self.running_tasks.add(task)
                await asyncio.sleep(self.seconds)
                self.task_is_done_event.clear()
