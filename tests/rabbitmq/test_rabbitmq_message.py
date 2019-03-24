import asynctest
from asynctest.mock import CoroutineMock
from asynctest import mock

from asyncworker.rabbitmq import RabbitMQMessage
from asyncworker.options import Events, Actions


class RabbitMQMessageTest(asynctest.TestCase):
    def setUp(self):
        self.queue_mock = CoroutineMock(
            ack=CoroutineMock(), reject=CoroutineMock()
        )
        self.AMQPMessage_mock = CoroutineMock()

    async def test_process_success_default_action(self):
        """
        Default é ACK, caso não digamos nada
        """
        message = RabbitMQMessage(
            body={}, delivery_tag=10, amqp_message=self.AMQPMessage_mock
        )

        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_action_ack(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.ACK,
            amqp_message=self.AMQPMessage_mock,
        )

        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_action_reject(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.REJECT,
            amqp_message=self.AMQPMessage_mock,
        )

        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=False
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_action_requeue(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.REQUEUE,
            amqp_message=self.AMQPMessage_mock,
        )

        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_ack_to_requeue(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.ACK,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=True)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_ack_to_reject(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.ACK,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=False)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=False
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_reject_to_ack(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.REJECT,
            amqp_message=self.AMQPMessage_mock,
        )
        message.accept()
        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_from_reject_to_requeue(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.REJECT,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=True)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_requeue_to_ack(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.REQUEUE,
            amqp_message=self.AMQPMessage_mock,
        )
        message.accept()
        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_from_requeue_to_reject(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_success=Actions.REQUEUE,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=False)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=False
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_default_action(self):
        message = RabbitMQMessage(
            body={}, delivery_tag=10, amqp_message=self.AMQPMessage_mock
        )

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_action_requeue(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.REQUEUE,
            amqp_message=self.AMQPMessage_mock,
        )

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_action_ack(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.ACK,
            amqp_message=self.AMQPMessage_mock,
        )

        await message.process_exception(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_exception_action_reject(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.REJECT,
            amqp_message=self.AMQPMessage_mock,
        )

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=False
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_ack_to_requeue(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.ACK,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=True)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_ack_to_reject(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.ACK,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=False)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=False
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_reject_to_ack(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.REJECT,
            amqp_message=self.AMQPMessage_mock,
        )
        message.accept()

        await message.process_exception(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_exception_from_reject_to_requeue(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.REJECT,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=True)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=True
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_requeue_to_ack(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.REQUEUE,
            amqp_message=self.AMQPMessage_mock,
        )
        message.accept()

        await message.process_exception(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(self.AMQPMessage_mock)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_exception_from_requeue_to_reject(self):
        message = RabbitMQMessage(
            body={},
            delivery_tag=10,
            on_exception=Actions.REQUEUE,
            amqp_message=self.AMQPMessage_mock,
        )
        message.reject(requeue=False)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(
            self.AMQPMessage_mock, requeue=False
        )
        self.queue_mock.ack.assert_not_awaited()
