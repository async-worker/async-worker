import abc
import json
import amqp
from typing import Dict, Tuple, Any, Generator

from easyqueue.exceptions import EmptyQueueException, \
    UndecodableMessageException, InvalidMessageSizeException

Message = Tuple[Dict, int]


class DeliveryModes:
    NON_PERSISTENT = 1
    PERSISTENT = 2


class BaseQueue(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def serialize(self, body: Any) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, body: str) -> Any:
        raise NotImplementedError

    def _parse_message(self, content) -> Dict[str, Any]:
        """
        Gets the raw message body as an input, handles deserialization and 
        outputs 
        :param content: The raw message body
        """
        try:
            return self.deserialize(content)
        except TypeError:
            return self.deserialize(content.decode())
        except json.decoder.JSONDecodeError as e:
            raise UndecodableMessageException('"{content}" can\'t be decoded as JSON'
                                              .format(content=content))


class BaseJsonQueue(BaseQueue):
    content_type = 'application/json'

    def __init__(self,
                 host: str,
                 username: str,
                 password: str,
                 virtual_host: str='/',
                 heartbeat: int=60,
                 max_message_size: int=None):
        self.host = host
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.heartbeat = heartbeat
        self.max_message_length = max_message_size

    def serialize(self, body: Any) -> str:
        return json.dumps(body)

    def deserialize(self, body: str) -> Any:
        return json.loads(body)


class ExternalQueue(BaseJsonQueue):
    def __init__(self,
                 host: str,
                 username: str,
                 password: str,
                 virtual_host: str='/',
                 exchange: str=None,
                 queue_name=None,
                 heartbeat: int=60,
                 redeliver_to_garbage_queue=False,
                 max_message_size: int=None):
        super().__init__(host,
                         username,
                         password,
                         virtual_host,
                         heartbeat,
                         max_message_size)
        self.queue_name = queue_name
        self.exchange = exchange
        self.garbage_routing_key = queue_name + '_garbage'
        self.redeliver_to_garbage_queue = redeliver_to_garbage_queue
        self.__connection = self._connect()
        self._channel = self.__connection.channel()

    @property
    def connection_parameters(self):
        return {
            'host': self.host,
            'userid': self.username,
            'password': self.password,
            'virtual_host': self.virtual_host,
            'heartbeat': self.heartbeat
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        self.__connection.close()

    def _connect(self) -> amqp.Connection:
        connection = amqp.Connection(**self.connection_parameters)
        connection.connect()

        return connection

    def _parse_message(self, content) -> Dict[str, Any]:
        try:
            return super()._parse_message(content)
        except UndecodableMessageException as e:
            if self.redeliver_to_garbage_queue:
                self.put(content, routing_key=self.garbage_routing_key)
            raise e

    def get(self) -> Tuple[dict, int]:
        message = self._channel.basic_get(queue=self.queue_name)
        if not message:
            raise EmptyQueueException

        if self.max_message_length:
            if len(message.body) > self.max_message_length:
                raise InvalidMessageSizeException(message)

        content = self._parse_message(message.body)

        return content, message.delivery_tag

    def get_many(self, max_quantity: int) -> Generator[Message, None, None]:
        for i in range(max_quantity):
            try:
                yield self.get()
            except EmptyQueueException:
                break

    def put(self, body: any, routing_key: str, exchange: str=None, priority: int=0):
        """
        Enqueues message.

        :param body: Can be one of three options:
            - amqp.Message: The message itself will be published
            - Dict: Will be encoded with json.dumps and included inside an
                    amqp.Message as its body
            - Any: If not amqp.Message or Dict, the body will be included
                   as is in a amqp.Message as its body

        :param routing_key: Routing key used to publish the message.
        :param priority: Priority when publishing the message.

        :rtype: vine.promise
        """
        if isinstance(body, amqp.Message):
            message = body  # publish as is
        else:
            body = json.dumps(body) if isinstance(body, dict) else body
            message = amqp.Message(body,
                                   delivery_mode=DeliveryModes.PERSISTENT,
                                   content_type=self.content_type,
                                   priority=priority)

        return self._channel.basic_publish(msg=message,
                                           exchange=exchange or self.exchange,
                                           routing_key=routing_key)

    def reject(self, delivery_tag: int, requeue=True):
        """
        Rejects a message from the queue, i.e. By default, returns it to the
        top of the queue.
        :param delivery_tag: second value on the tuple returned from `get()`.
        """
        ret = self._channel.basic_reject(delivery_tag, requeue=requeue)
        # todo: ver retorno e documentar
        return ret

    def ack(self, delivery_tag: int):
        """
        Acks a message from the queue.
        :param delivery_tag: second value on the tuple returned from get().
        """
        return self._channel.basic_ack(delivery_tag)
