from time import time
from typing import Callable, Coroutine

now = time


class Timeit:
    def __init__(self,
                 name: str,
                 callback: Callable[..., Coroutine],
                 **kwargs):
        self.name = name
        self.callback = callback
        self.__kwargs = kwargs
        self.start: float = None
        self.finish: float = None

    @property
    def time_delta(self) -> float:
        return self.finish - self.start

    async def __aenter__(self):
        self.start = now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.finish = now()
        if exc_type:
            await self.callback(
                self.name,
                self.time_delta,
                exc_type=exc_type,
                exc_val=exc_val,
                exc_tb=exc_tb,
                **self.__kwargs
            )
        else:
            await self.callback(self.name, self.time_delta, **self.__kwargs)
