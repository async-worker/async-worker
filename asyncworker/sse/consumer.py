import asyncio
import json
import traceback
from enum import Enum, auto
from typing import Type, List, Dict
from urllib.parse import urljoin

import aiohttp
from aiohttp.client import ClientTimeout, ClientSession, ClientResponse

from asyncworker import conf
from asyncworker.bucket import Bucket
from asyncworker.sse.message import SSEMessage


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

    def __init__(
        self,
        route_info: Dict,
        url: str,
        username: str = None,
        password: str = None,
        bucket_class: Type[Bucket] = Bucket,
    ) -> None:
        self.url = url
        self.session = ClientSession(timeout=timeout)
        self.bucket = bucket_class(size=route_info["options"]["bulk_size"])
        self.route_info = route_info
        self._handler = route_info["handler"]
        self.username = username
        self.password = password
        self.routes: List[str] = []
        for route in self.route_info["routes"]:
            self.routes.append(urljoin(self.url, route))

    def keep_runnig(self):
        return True

    async def on_event(self, event_name: bytes, event_raw_body):
        rv = None
        all_messages: List[SSEMessage] = []

        if not self.bucket.is_full():
            message = SSEMessage(
                event_name=event_name.decode("utf-8"),
                event_body=json.loads(event_raw_body),
            )
            self.bucket.put(message)

        if self.bucket.is_full():
            all_messages = self.bucket.pop_all()
            rv = await self._handler(all_messages)
        return rv

    async def on_connection_error(self, exception):
        await conf.logger.error(
            {
                "type": "connection-failed",
                "dest": self.url,
                "retry": True,
                "exc_traceback": traceback.format_exc(),
            }
        )

    async def on_exception(self, exception):
        await conf.logger.error(
            {
                "type": "unhandled-exception",
                "dest": self.url,
                "retry": True,
                "exc_traceback": traceback.format_exc(),
            }
        )

    async def on_connection(self):
        await conf.logger.debug({"event": "on-connection", "url": self.url})

    def _parse_sse_line(self, line: bytes) -> bytes:
        return line.split(EVENT_FIELD_SEPARATOR, 1)[1].strip()

    async def _consume_events(self, response: ClientResponse):
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

    async def _connect(self, session: ClientSession) -> ClientResponse:
        response = await session.get(
            self.url, headers={"Accept": "text/event-stream"}
        )
        await self.on_connection()
        return response

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
