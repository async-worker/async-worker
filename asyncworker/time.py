import asyncio
from collections import AsyncIterator
from datetime import datetime


class ClockTicker(AsyncIterator):
    def __init__(self, seconds: int):
        """
        :param seconds: Tick interval in seconds
        """
        self.seconds = seconds
        self.current_iteration = 0
        self._running = True
        self._tick_event = asyncio.Event()
        self._main_task: asyncio.Task

    def __aiter__(self) -> AsyncIterator:
        self._running = True
        self.current_iteration = 0
        self._main_task = asyncio.ensure_future(self._run())
        return self

    async def __anext__(self) -> int:
        if not self._running:
            raise StopAsyncIteration
        await self._tick_event.wait()
        self._tick_event.clear()
        i = self.current_iteration
        self.current_iteration += 1
        return i

    async def _run(self):
        while self._running:
            self._tick_event.set()
            await asyncio.sleep(self.seconds)

    def stop(self):
        self._running = False


# async def main():
#     clock = ClockTicker(seconds=1)
#     async for tick in clock:
#         print(tick, datetime.now())
#         await asyncio.sleep(2)  # do something time expensive
#         if tick == 2:
#             clock.stop()
#
#
# asyncio.run(main())
