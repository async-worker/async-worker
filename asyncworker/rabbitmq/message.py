from asyncworker.options import Actions

from asyncworker.easyqueue.message import AMQPMessage


class RabbitMQMessage:
    def __init__(
        self,
        delivery_tag: int,
        amqp_message: AMQPMessage,
        on_success: Actions = Actions.ACK,
        on_exception: Actions = Actions.REQUEUE,
    ) -> None:
        self._delivery_tag = delivery_tag
        self._on_success_action = on_success
        self._on_exception_action = on_exception
        self._final_action = None
        self._amqp_message = amqp_message

    @property
    def body(self):
        return self._amqp_message.deserialized_data

    @property
    def serialized_data(self):
        return self._amqp_message.serialized_data

    def reject(self, requeue=True):
        self._final_action = Actions.REQUEUE if requeue else Actions.REJECT

    def accept(self):
        self._final_action = Actions.ACK

    async def _process_action(self, action: Actions, queue: JsonQueue):
        if action == Actions.REJECT:
            await queue.reject(self._amqp_message, requeue=False)
        elif action == Actions.REQUEUE:
            await queue.reject(self._amqp_message, requeue=True)
        elif action == Actions.ACK:
            await queue.ack(self._amqp_message)

    async def process_success(self, queue: JsonQueue):
        action = self._final_action or self._on_success_action
        return await self._process_action(action, queue)

    async def process_exception(self, queue: JsonQueue):
        action = self._final_action or self._on_exception_action
        return await self._process_action(action, queue)
