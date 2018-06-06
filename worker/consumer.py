from easyqueue.async import AsyncQueueConsumerDelegate, AsyncQueue


class Consumer(AsyncQueueConsumerDelegate):

    #def __init__(self,
    #             host: str,
    #             username: str,
    #             password: str,
    #             delegate_class: Type['AsyncQueueConsumerDelegate'] = None,
    #             delegate: 'AsyncQueueConsumerDelegate' = None,
    #             virtual_host: str = '/',
    #             heartbeat: int = 60,
    #             prefetch_count: int = 100,
    #             max_message_length=0,
    #             loop=None):
    def __init__(self, route_info, host, username, password, prefetch_count=128):
        self.route = route_info
        self._handler = route_info['handler']
        self._queue_name = route_info['route']
        self._route_options = route_info['options']
        self.queue = AsyncQueue(host,
                                username,
                                password,
                                virtual_host=self._route_options.get("vhost", "/"),
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


    async def on_queue_message(self, message_dict, delivery_tag, queue):
        """
        Callback called every time that a new, valid and deserialized message
        is ready to be handled.

        :param delivery_tag: delivery_tag of the consumed message
        :type delivery_tag: int
        :param content: parsed message body
        :type content: dict
        :type queue: AsyncQueue
        """
        return await self._handler(message_dict)
        #try:
        #    return await self._handler(message)
        #    await self.queue.ack(tag)
        #except Exception as e:
        #    await self.queue.reject(tag)

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

    async def on_message_handle_error(self, handler_error: Exception,
                                      **kwargs):
        """
        Callback called when an uncaught exception was raised during message
        handling stage.

        :param handler_error: The exception that triggered
        :param kwargs: arguments used to call the coroutine that handled
        the message
        :return:
        """
        pass

    async def on_connection_error(self, exception: Exception):
        """
        Called when the connection fails
        """
        pass

