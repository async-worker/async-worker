from collections import Mapping
from typing import Dict, List, Union, Iterator, Any

from asyncworker.easyqueue.async_queue import AsyncJsonQueue

from asyncworker.conf import settings


Message = Union[List, Dict]


class AMQPConnection(Mapping):
    def __init__(self, hostname: str, username: str, password: str) -> None:
        self.hostname = hostname
        self.username = username
        self.password = password
        self.__connections: Dict[str, AsyncJsonQueue] = {}

    def __len__(self) -> int:
        return len(self.__connections)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__connections)

    def __getitem__(self, key: str) -> AsyncJsonQueue:
        """
        Gets a AsyncJsonQueue instance for a given virtual host

        :param key: The virtual host of the connection
        :return: An instance of the connection
        """
        try:
            return self.__connections[key]
        except KeyError:
            conn: AsyncJsonQueue = AsyncJsonQueue(
                host=self.hostname,
                username=self.username,
                password=self.password,
                virtual_host=key,
            )
            self.__connections[key] = conn
            return conn

    def register(self, queue: AsyncJsonQueue) -> None:
        self.__connections[queue.virtual_host] = queue

    async def put(
        self,
        routing_key: str,
        data: Any = None,
        serialized_data: Union[str, bytes] = None,
        exchange: str = "",
        vhost: str = settings.AMQP_DEFAULT_VHOST,
    ):
        conn = self[vhost]
        return await conn.put(
            routing_key=routing_key,
            data=data,
            serialized_data=serialized_data,
            exchange=exchange,
        )
