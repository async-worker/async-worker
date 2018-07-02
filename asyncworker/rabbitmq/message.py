
from easyqueue.async import AsyncQueue

class RabbitMQMessage:

    def __init__(self, body, delivery_tag):
        self._do_ack = True
        self.body = body
        self._delivery_tag = delivery_tag

    def reject(self):
        self._do_ack = False

    def accept(self):
        self._do_ack = True

    async def process(self, queue: AsyncQueue):
        if self._do_ack:
            await queue.ack(delivery_tag=self._delivery_tag)
        else:
            await queue.reject(delivery_tag=self._delivery_tag, requeue=True)
