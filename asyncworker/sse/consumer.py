from enum import Enum, auto
from aiohttp import ClientSession, ClientTimeout
import aiohttp
import asyncio
import traceback

from asyncworker.sse.message import SSEMessage


from asyncworker import conf

class State(Enum):
    WAIT_FOR_DATA = auto()
    EVENT_NAME_FOUND = auto()
    EVENT_DATA_FOUND = auto()

EMPTY = b""
EVENT_NAME_PREFIX = b"event:"
EVENT_DATA_PREFIX = b"data:"
EVENT_FIELD_SEPARATOR = b":"


timeout = ClientTimeout(sock_read=5)


class SSEConsumer:
    interval = 10

    def __init__(self, url):
        self.url = url
        self.session = ClientSession(timeout=timeout)

    def keep_runnig(self):
        return True

    async def on_event(self, event_name, event_raw_body):
        pass

    async def on_connection_error(self, exception):
        conf.logger.error({
            "type": "connection-failed",
            "dest": self.url, "retry": True,
            "exc_traceback": traceback.format_exc()
        })

    async def on_exception(self, exception):
        conf.logger.error({
            "type": "unhandled-exception",
            "dest": self.url, "retry": True,
            "exc_traceback": traceback.format_exc()
        })

    def _parse_sse_line(self, line):
        return line.split(EVENT_FIELD_SEPARATOR, 1)[1].strip()
    
    async def _consume_events(self, response):
        self.state = State.WAIT_FOR_DATA 
        event_name = EMPTY
        event_body = EMPTY
        async for line in response.content:
            if line.startswith(EVENT_NAME_PREFIX):
                event_name = self._parse_sse_line(line)
                self.state = State.EVENT_NAME_FOUND

            if line.startswith(EVENT_DATA_PREFIX):
                event_body = self._parse_sse_line(line)
                self.state = State.EVENT_DATA_FOUND

            if self.state == State.EVENT_DATA_FOUND:
                await self.on_event(event_name, event_body)
                self.state = State.WAIT_FOR_DATA
                event_name = EMPTY
                event_body = EMPTY

    async def _connect(self, session):
        return await session.get(self.url, headers={"Accept": "text/event-stream"})

    async def start(self):
        while self.keep_runnig():
            response = None
            try:
                response = await self._connect(self.session)
                await self._consume_events(response)
            except aiohttp.ClientError as err:
                await self.on_connection_error(err)
            except Exception as e:
                await self.on_exception(e)

            await asyncio.sleep(self.interval)


