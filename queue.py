import json
from typing import Dict, Tuple, Any, Generator

import amqp
from amqp import AMQPError


Message = Tuple[Dict, int]


class DeliveryModes(object):
    NON_PERSISTENT = 1
    PERSISTENT = 2


class EmptyQueueException(Exception):
    """No message to get"""


class ExternalQueue(object):
    content_type = 'application/json'

    def __init__(self, host: str, username: str, password: str,
                 virtual_host: str='/', exchange: str=None, queue_name=None,
                 heartbeat: int=0):
        self.host = host
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.heartbeat = heartbeat
        self.exchange = exchange
        self.queue_name = queue_name
        self.garbage_routing_key = NotImplementedError

        self.__connection = self._connect()
        self._channel = self.__connection.channel()
        # self.__assert_garbage_queue_exists()

    def __assert_garbage_queue_exists(self):
        garbage_queue_name = self.queue_name + '_garbage'
        raise NotImplementedError

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
        # self.__connection.connect()
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
            # garbage
            self.put(message, routing_key=self.garbage_routing_key)
            raise NotImplementedError

    def get(self) -> Tuple[dict, int]:
        message = self._channel.basic_get(queue=self.queue_name)
        if not message:
            raise EmptyQueueException

        content = self._parse_message(message)

        return content, message.delivery_tag

    def get_many(self, max_quantity: int) -> Generator[Message, None, None]:
        # todo: Será que faz sentido ter algum método acessório pra isso ?
        for i in range(max_quantity):
            try:
                yield self.get()
            except EmptyQueueException:
                break

    def put(self, body: dict, routing_key: str, priority: int = 0):
        """
        :rtype: vine.promise
        """
        message = amqp.Message(json.dumps(body),
                               delivery_mode=DeliveryModes.PERSISTENT,
                               content_type=self.content_type,
                               priority=priority)

        return self._channel.basic_publish(msg=message,
                                           exchange=self.exchange,
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
        try:
            ret = self._channel.basic_ack(delivery_tag)
            return ret
        except AMQPError as e:
            # There's nothing we can do, we can't ack the message in
            # a different channel than the one we got it from
            raise NotImplementedError
