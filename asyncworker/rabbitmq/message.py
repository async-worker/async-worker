
from easyqueue.async import AsyncQueue
from asyncworker.options import Options


class RabbitMQMessage:

    def __init__(self, body, delivery_tag, on_success=Options.ACK, on_exception=Options.REQUEUE):
        self.body = body
        self._delivery_tag = delivery_tag
        self._on_success_action = on_success
        self._on_exception_action = on_exception
        self._final_action = None

    def reject(self, requeue=True):
        self._final_action = Options.REJECT
        if requeue:
            self._final_action = Options.REQUEUE
        self._on_success_action = None
        self._on_exception_action = None

    def accept(self):
        self._on_success_action = None
        self._on_exception_action = None
        self._final_action = Options.ACK

    async def _process_action(self, action: Options, queue: AsyncQueue):
        if action == Options.REJECT:
            await queue.reject(delivery_tag=self._delivery_tag, requeue=False)
        elif action == Options.REQUEUE:
            await queue.reject(delivery_tag=self._delivery_tag, requeue=True)
        elif action == Options.ACK:
            await queue.ack(delivery_tag=self._delivery_tag)

    async def process_success(self, queue: AsyncQueue):
        action = self._on_success_action or self._final_action
        return await self._process_action(action, queue)

    async def process_exception(self, queue: AsyncQueue):
        action = self._on_exception_action or self._final_action
        return await self._process_action(action, queue)
