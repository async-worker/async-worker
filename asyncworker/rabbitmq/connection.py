from collections import Mapping
from typing import Dict, List, Union, Iterator

from easyqueue import AsyncQueue

from asyncworker.conf import settings


Message = Union[List, Dict]


class RabbitMQProxyConnection(Mapping):
    def __init__(self) -> None:
        self.__connections: Dict[str, AsyncQueue] = {}

    def __len__(self) -> int:
        return len(self.__connections)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__connections)

    def __getitem__(self, key: str) -> AsyncQueue:
        return self.__connections[key]

    def register(self, queue: AsyncQueue) -> None:
        self.__connections[queue.virtual_host] = queue

    async def put(
        self,
        body: Message,
        routing_key: str,
        exchange: str,
        vhost: str = settings.AMQP_DEFAULT_VHOST,
    ):
        try:
            conn = self.__connections[vhost]
        except KeyError as e:
            raise RuntimeError(
                f"Connection not initialized for vhost '{vhost}'"
            ) from e
        return await conn.put(body, routing_key, exchange)
