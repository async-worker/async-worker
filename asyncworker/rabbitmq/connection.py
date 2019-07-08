from collections import Mapping
from typing import Dict, List, Union, Iterator, Any

from asyncworker.conf import settings
from asyncworker.easyqueue.queue import JsonQueue

Message = Union[List, Dict]


class AMQPConnection(Mapping):
    def __init__(self, hostname: str, username: str, password: str) -> None:
        self.hostname = hostname
        self.username = username
        self.password = password
        self.__connections: Dict[str, JsonQueue] = {}

    def __len__(self) -> int:
        return len(self.__connections)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__connections)

    def __getitem__(self, key: str) -> JsonQueue:
        """
        Gets a JsonQueue instance for a given virtual host

        :param key: The virtual host of the connection
        :return: An instance of the connection
        """
        try:
            return self.__connections[key]
        except KeyError:
            conn: JsonQueue = JsonQueue(
                host=self.hostname,
                username=self.username,
                password=self.password,
                virtual_host=key,
            )
            self.__connections[key] = conn
            return conn

    def register(self, queue: JsonQueue) -> None:
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
