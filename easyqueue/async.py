import abc
import aioamqp
import asyncio
from typing import Any, Dict
from json.decoder import JSONDecodeError
from easyqueue.queue import BaseJsonQueue
from easyqueue.exceptions import UndecodableMessageException, \
    InvalidMessageSizeException, MessageError


class AsyncQueueConsumerDelegate(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def loop(self) -> asyncio.BaseEventLoop:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def queue(self) -> 'AsyncQueue':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def queue_name(self) -> str:
        raise NotImplementedError

    async def _consume(self):
        await self.queue.connect()
        await self.queue.consume(queue_name=self.queue_name)

    async def on_queue_message(self, content, delivery_tag, queue):
        """
        :param delivery_tag: delivery_tag of the consumed message 
        :type delivery_tag: int
        :param content: parsed message body
        :type content: dict
        :type queue: AsyncQueue
        """
        raise NotImplementedError

    async def on_queue_error(self, body, delivery_tag, error, queue):
        """
        :param body: unparsed, raw message content
        :type body: Any
        :param delivery_tag: delivery_tag of the consumed message 
        :type delivery_tag: int
        :type queue: AsyncQueue
        """
        raise NotImplementedError

    def run(self):
        self.loop.create_task(self._consume())
        self.loop.run_forever()


class AsyncQueue(BaseJsonQueue):
    def __init__(self,
                 host: str,
                 username: str,
                 password: str,
                 delegate: AsyncQueueConsumerDelegate,
                 virtual_host: str = '/',
                 heartbeat: int = 60,
                 prefetch_count: int=100,
                 max_message_length=0,
                 loop=None):

        super().__init__(host, username, password, virtual_host, heartbeat)

        self.delegate = delegate
        self.loop = loop or asyncio.get_event_loop()
        self.prefetch_count = prefetch_count

        if max_message_length < 0:
            raise ValueError("max_message_length must be a positive integer")

        self.max_message_length = max_message_length

        self._protocol = None  # type: aioamqp.protocol.AmqpProtocol
        self._transport = None  # type: asyncio.BaseTransport
        self._channel = None  # type: aioamqp.channel.Channel

    @property
    def connection_parameters(self):
        return {
            'host': self.host,
            'login': self.username,
            'password': self.password,
            'virtualhost': self.virtual_host,
            'loop': self.loop
        }

    @property
    def is_connected(self):
        # todo: This may not be enough
        return self._channel and self._channel.is_open

    async def connect(self):
        conn = await aioamqp.connect(**self.connection_parameters)
        self._transport, self._protocol = conn
        self._channel = await self._protocol.channel()

    async def close(self):
        await self._protocol.close()
        self._transport.close()

    async def ack(self, delivery_tag: int):
        return await self._channel.basic_client_ack(delivery_tag)

    async def reject(self, delivery_tag: int, requeue=False):
        return await self._channel.basic_reject(delivery_tag=delivery_tag,
                                                requeue=requeue)

    async def put(self, body: any, routing_key: str, exchange: str = '', priority: int = 0):
        if priority:
            raise NotImplementedError
        payload = self.serialize(body)
        return await self._channel.publish(payload=payload,
                                           exchange_name=exchange,
                                           routing_key=routing_key)

    def _parse_message(self, body) -> Dict[str, Any]:
        if self.max_message_length:
            if len(body) > self.max_message_length:
                raise InvalidMessageSizeException(body)
        try:
            return self.deserialize(body)
        except TypeError as e:
            return self._parse_message(body.decode())
        except JSONDecodeError as e:
            raise UndecodableMessageException('"{body}" can\'t be decoded as JSON'
                                              .format(body=body))

    async def _handle_message(self, channel, body, envelope, properties):
        tag = envelope.delivery_tag
        try:
            content = self._parse_message(body)
        except MessageError as e:
            callback = self.delegate.on_queue_error(body=body,
                                                    delivery_tag=tag,
                                                    error=e,
                                                    queue=self)
        else:
            callback = self.delegate.on_queue_message(content=content,
                                                      delivery_tag=tag,
                                                      queue=self)
        self.loop.create_task(callback)

    async def consume(self, queue_name: str, consumer_name='') -> str:
        """
        :param queue_name: queue to consume
        :return: the consumer tag. Useful for cancelling/stopping consumption
        """
        # todo: Implement a consumer tag generator
        if self._channel is None:
            raise ConnectionError("Queue isn't connected. "
                                  "Did you forgot to wait for `connect()`?")

        await self._channel.basic_qos(prefetch_count=self.prefetch_count,
                                      prefetch_size=0,
                                      connection_global=False)
        tag = await self._channel.basic_consume(callback=self._handle_message,
                                                consumer_tag=consumer_name,
                                                queue_name=queue_name)
        return tag['consumer_tag']
