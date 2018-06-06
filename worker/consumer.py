import asyncio
from easyqueue.async import AsyncQueueConsumerDelegate, AsyncQueue
from aioamqp.exceptions import AioamqpException


class Consumer(AsyncQueueConsumerDelegate):

    def __init__(self, route_info, host, username, password, prefetch_count=128):
        self.route = route_info
        self._handler = route_info['handler']
        self._queue_name = route_info['route']
        self._route_options = route_info['options']
        vhost = self._route_options.get("vhost", "/")
        if vhost != "/":
            vhost = vhost.lstrip("/")
        self.queue = AsyncQueue(host,
                                username,
                                password,
                                virtual_host=vhost,
                                delegate=self,
                                prefetch_count=prefetch_count)

    @property
    def queue_name(self) -> str:
        return self._queue_name

    async def on_before_start_consumption(self, queue_name: str, queue: 'AsyncQueue'):
        """
        Coroutine called before queue consumption starts. May be overwritten to
        implement further custom initialization.

        :param queue_name: Queue name that will be consumed
        :type queue_name: str
        :param queue: AsynQueue instanced
        :type queue: AsyncQueue
        """
        pass

    async def on_consumption_start(self, consumer_tag: str, queue: 'AsyncQueue'):
        """
        Coroutine called once consumption started.
        """


    async def on_queue_message(self, content, delivery_tag, queue):
        """
        Callback called every time that a new, valid and deserialized message
        is ready to be handled.

        :param delivery_tag: delivery_tag of the consumed message
        :type delivery_tag: int
        :param content: parsed message body
        :type content: dict
        :type queue: AsyncQueue
        """
        try:
            rv = await self._handler(content)
            await queue.ack(delivery_tag=delivery_tag)
            return rv
        except AioamqpException as aioamqpException:
            raise aioamqpException
        except Exception as e:
            await queue.reject(delivery_tag=delivery_tag, requeue=False)

    async def on_queue_error(self, body, delivery_tag, error, queue):
        """
        Callback called every time that an error occurred during the validation
        or deserialization stage.

        :param body: unparsed, raw message content
        :type body: Any
        :param delivery_tag: delivery_tag of the consumed message
        :type delivery_tag: int
        :param error: THe error that caused the callback to be called
        :type error: MessageError
        :type queue: AsyncQueue
        """
        pass

    async def on_message_handle_error(self, handler_error: Exception, **kwargs):
        """
        Callback called when an uncaught exception was raised during message
        handling stage.

        :param handler_error: The exception that triggered
        :param kwargs: arguments used to call the coroutine that handled
        the message
        :return:
        """
        print(handler_error)
        print(**kwargs)

    async def on_connection_error(self, exception: Exception):
        """
        Called when the connection fails
        """
        pass

    async def consume_all_queues(self, queue):
        for queue_name in self._queue_name:
            # Por enquanto não estamos gaurdando a consumer_tag retornada
            # se precisar, podemos passar a guardar.
            await queue.consume(queue_name=queue_name)

    async def start(self):
        while True:
            await asyncio.sleep(1)
            if self.queue.is_connected:
                continue
            try:
                await self.queue.connect()
                await self.consume_all_queues(self.queue)
            except Exception as e:
                print("Connection failed, retrying")
                raise e

