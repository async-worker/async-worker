from easyqueue import AsyncQueue
from asyncworker.options import Actions


class RabbitMQMessage:
    def __init__(self,
                 body,
                 delivery_tag: int,
                 on_success: Actions=Actions.ACK,
                 on_exception: Actions=Actions.REQUEUE) -> None:
        self.body = body
        self._delivery_tag = delivery_tag
        self._on_success_action = on_success
        self._on_exception_action = on_exception
        self._final_action = None

    def reject(self, requeue=True):
        self._final_action = Actions.REQUEUE if requeue else Actions.REJECT

    def accept(self):
        self._final_action = Actions.ACK

    async def _process_action(self, action: Actions, queue: AsyncQueue):
        if action == Actions.REJECT:
            await queue.reject(delivery_tag=self._delivery_tag, requeue=False)
        elif action == Actions.REQUEUE:
            await queue.reject(delivery_tag=self._delivery_tag, requeue=True)
        elif action == Actions.ACK:
            await queue.ack(delivery_tag=self._delivery_tag)

    async def process_success(self, queue: AsyncQueue):
        action = self._final_action or self._on_success_action
        return await self._process_action(action, queue)

    async def process_exception(self, queue: AsyncQueue):
        action = self._final_action or self._on_exception_action
        return await self._process_action(action, queue)
