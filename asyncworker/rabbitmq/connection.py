from collections import Mapping
from typing import Dict, List, Union, Iterator, Any, Optional

from pydantic import validator

from asyncworker.connections import BaseConnection
from asyncworker.options import RouteTypes
from asyncworker.easyqueue.queue import JsonQueue

from asyncworker.conf import settings


Message = Union[List, Dict]


class AMQPConnection(Mapping, BaseConnection):
    hostname: str
    username: str
    password: str
    route_type = RouteTypes.AMQP_RABBITMQ
    prefetch: int = settings.AMQP_DEFAULT_PREFETCH_COUNT
    heartbeat: int = settings.AMQP_DEFAULT_HEARTBEAT
    name: Optional[str] = None
    connections: Dict[str, JsonQueue] = {}

    class Config:
        arbitrary_types_allowed = True

    # def __post_init__(self) -> None:
    @validator("connections", pre=True, always=True, check_fields=False)
    def set_connections(cls, v):
        return v or {}

    def __len__(self) -> int:
        return len(self.connections)

    def __iter__(self) -> Iterator[str]:
        return iter(self.connections)

    def __getitem__(self, key: str) -> JsonQueue:
        """
        Gets a JsonQueue instance for a given virtual host

        :param key: The virtual host of the connection
        :return: An instance of the connection
        """
        try:
            return self.connections[key]
        except KeyError:
            conn: JsonQueue = JsonQueue(
                host=self.hostname,
                username=self.username,
                password=self.password,
                virtual_host=key,
            )
            self.connections[key] = conn
            return conn

    def register(self, queue: JsonQueue) -> None:
        self.connections[queue.virtual_host] = queue

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
