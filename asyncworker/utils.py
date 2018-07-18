from functools import wraps
from time import time as now
from typing import Callable, Coroutine


TimeitCallback = Callable[..., Coroutine]


class Timeit:
    def __init__(self,
                 name: str,
                 callback: TimeitCallback):
        self.name = name
        self.callback = callback
        self.start: float = None
        self.finish: float = None

    def __call__(self, coro: Callable[..., Coroutine]):
        @wraps(coro)
        async def wrapped(*args, **kwargs):
            async with self:
                return await coro(*args, **kwargs)
        return wrapped

    @property
    def time_delta(self) -> float:
        return self.finish - self.start

    async def __aenter__(self):
        self.start = now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.finish = now()
        await self.callback(
            name=self.name,
            time_delta=self.time_delta,
            exc_type=exc_type,
            exc_val=exc_val,
            exc_tb=exc_tb
        )
