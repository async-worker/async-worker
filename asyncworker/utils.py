from functools import wraps
from time import time as now
from typing import Callable, Coroutine, Dict, Union


TimeitCallback = Callable[..., Coroutine]


class Timeit:
    TRANSACTIONS_KEY = 'transactions'

    def __init__(self,
                 name: str,
                 callback: TimeitCallback=None):
        self.name = name
        self.callback = callback
        self.start: float = None
        self.finish: float = None
        self._transactions: Dict[str, float] = {}

    def __call__(self,
                 coro: Callable[..., Coroutine]=None,
                 name: str=None) -> Union[Callable[..., Coroutine], 'TimeIt']:
        if name:
            child = Timeit(name=name)
            child._transactions = self._transactions
            return child

        @wraps(coro)
        async def wrapped(*args, **kwargs):
            async with self:
                return await coro(*args, **kwargs)
        return wrapped

    async def __aenter__(self):
        self.start = now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.finish = now()

        if self.name in self._transactions:
            raise ValueError("A transaction with the same name already exists.")

        self._transactions[self.name] = self.finish - self.start

        if self.callback:
            measurement = {
                self.TRANSACTIONS_KEY: self._transactions,
                'exc_type': exc_type,
                'exc_val': exc_val,
                'exc_tb': exc_tb,
            }
            await self.callback(**measurement)
