from typing import Callable, TypeVar, Generic

from aioamqp.channel import Channel
from aioamqp.envelope import Envelope
from aioamqp.properties import Properties

from easyqueue.connection import AMQPConnection


T = TypeVar("T")


class AMQPMessage(Generic[T]):
    __slots__ = (
        "connection",
        "channel",
        "queue_name",
        "serialized_data",
        "delivery_tag",
        "_envelope",
        "_properties",
        "_deserialization_method",
        "__deserialized_data",
    )

    def __init__(
        self,
        connection: AMQPConnection,
        channel: Channel,
        queue_name: str,
        serialized_data: bytes,
        delivery_tag: int,
        envelope: Envelope,
        properties: Properties,
        deserialization_method: Callable[[bytes], T],
    ) -> None:
        self.queue_name = queue_name
        self.serialized_data = serialized_data
        self.delivery_tag = delivery_tag
        self.connection = connection
        self.channel = channel
        self._envelope = envelope
        self._properties = properties
        self._deserialization_method = deserialization_method

        self.__deserialized_data: T

    @property
    def deserialized_data(self) -> T:
        if self.__deserialized_data:
            return self.__deserialized_data
        self.__deserialized_data = self._deserialization_method(
            self.serialized_data
        )
        return self.__deserialized_data
