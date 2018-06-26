import asynctest
from asynctest.mock import CoroutineMock

from asyncworker.rabbitmq import RabbitMQMessage


class RabbitMQMessageTest(asynctest.TestCase):

    def test_defaults_to_be_acked(self):
        message = RabbitMQMessage({}, 10)
        self.assertTrue(message._do_ack)

    def test_mark_message_to_be_rejected(self):
        message = RabbitMQMessage({}, 10)
        message.reject()
        self.assertFalse(message._do_ack)

    def test_mark_message_to_be_acked(self):
        message = RabbitMQMessage({}, 10)
        message._do_ack = False
        message.accept()
        self.assertTrue(message._do_ack)

    def test_initialize_with_body_and_delivery_tag(self):
        expected_body = {"key": "value"}
        message = RabbitMQMessage(body=expected_body, delivery_tag=42)
        self.assertEqual(expected_body, message.body)
        self.assertEqual(42, message._delivery_tag)

    async def test_process_message_to_be_acked(self):
        expected_body = {"key": "value"}
        message = RabbitMQMessage(body=expected_body, delivery_tag=42)
        queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
        await message.process(queue_mock)
        queue_mock.ack.assert_awaited_once_with(delivery_tag=42)
        self.assertEqual(0, queue_mock.reject.await_count)

    async def test_process_message_to_be_rejected(self):
        """
        Sempre fazemos reject com requeue.
        """
        expected_body = {"key": "value"}
        message = RabbitMQMessage(body=expected_body, delivery_tag=42)
        message.reject()

        queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
        await message.process(queue_mock)
        queue_mock.reject.assert_awaited_once_with(delivery_tag=42, requeue=True)
        self.assertEqual(0, queue_mock.ack.await_count)
