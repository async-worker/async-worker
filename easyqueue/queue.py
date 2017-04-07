import json

import amqp
from typing import Dict, Tuple, Any, Generator

from easyqueue.exceptions import EmptyQueueException, \
    UndecodableMessageException, InvalidMessageSizeException

Message = Tuple[Dict, int]


class DeliveryModes:
    NON_PERSISTENT = 1
    PERSISTENT = 2


class ExternalQueue(object):
    content_type = 'application/json'

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
        self.host = host
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.heartbeat = heartbeat
        self.exchange = exchange
        self.queue_name = queue_name
        self.garbage_routing_key = queue_name + '_garbage'
        self.redeliver_to_garbage_queue = redeliver_to_garbage_queue
        self.max_message_length = max_message_size

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

    def _parse_message(self, message) -> Dict[str, Any]:
        body = message.body
        try:
            return json.loads(body)
        except TypeError:
            return json.loads(body.decode())
        except json.decoder.JSONDecodeError as e:
            if self.redeliver_to_garbage_queue:
                self.put(message, routing_key=self.garbage_routing_key)
            raise UndecodableMessageException('"{body}" can\'t be decoded as JSON'
                                              .format(body=body))

    def get(self) -> Tuple[dict, int]:
        message = self._channel.basic_get(queue=self.queue_name)
        if not message:
            raise EmptyQueueException

        if self.max_message_length:
            if len(message.body) > self.max_message_length:
                raise InvalidMessageSizeException

        content = self._parse_message(message)

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

    def reject(self, delivery_tag: int):
        """
        Rejects a message from the queue, i.e. returns it to the
        top of the queue.
        :param delivery_tag: second value on the tuple returned from `get()`.
        """
        ret = self._channel.basic_reject(delivery_tag, requeue=True)
        # todo: ver retorno e documentar
        return ret

    def ack(self, delivery_tag: int):
        """
        Acks a message from the queue.
        :param delivery_tag: second value on the tuple returned from get().
        """
        return self._channel.basic_ack(delivery_tag)
