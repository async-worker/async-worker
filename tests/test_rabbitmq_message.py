import asynctest
from asynctest.mock import CoroutineMock
from asynctest import mock

from asyncworker.rabbitmq import RabbitMQMessage
from asyncworker.options import Events, Actions

class RabbitMQMessageTest(asynctest.TestCase):

    def setUp(self):
        self.queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())

    #def test_defaults_to_be_acked(self):
    #    message = RabbitMQMessage({}, 10)
    #    self.assertTrue(message._do_ack)

    #def test_mark_message_to_be_rejected_and_requeued(self):
    #    message = RabbitMQMessage({}, 10)
    #    message.reject()
    #    self.assertFalse(message._do_ack)
    #    self.assertTrue(message._requeue)

    #def test_mark_message_to_be_rejected_and_discarded(self):
    #    message = RabbitMQMessage({}, 10)
    #    message.reject(requeue=False)
    #    self.assertFalse(message._do_ack)
    #    self.assertFalse(message._requeue)

    #def test_mark_message_to_be_acked(self):
    #    message = RabbitMQMessage({}, 10)
    #    message._do_ack = False
    #    message.accept()
    #    self.assertTrue(message._do_ack)

    #def test_initialize_with_body_and_delivery_tag(self):
    #    expected_body = {"key": "value"}
    #    message = RabbitMQMessage(body=expected_body, delivery_tag=42)
    #    self.assertEqual(expected_body, message.body)
    #    self.assertEqual(42, message._delivery_tag)

    #async def test_process_message_to_be_rejected_and_discarded(self):
    #    expected_body = {"key": "value"}
    #    message = RabbitMQMessage(body=expected_body, delivery_tag=42)
    #    queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
    #    message.reject(requeue=False)
    #    await message.process(queue_mock)
    #    self.assertEqual(0, queue_mock.ack.await_count)
    #    self.assertEqual(1, queue_mock.reject.await_count)
    #    self.assertEqual([mock.call(delivery_tag=42, requeue=False)], queue_mock.reject.await_args_list)

    #async def test_process_message_to_be_acked(self):
    #    expected_body = {"key": "value"}
    #    message = RabbitMQMessage(body=expected_body, delivery_tag=42)
    #    queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
    #    await message.process(queue_mock)
    #    queue_mock.ack.assert_awaited_once_with(delivery_tag=42)
    #    self.assertEqual(0, queue_mock.reject.await_count)

    #async def test_process_message_to_be_rejected(self):
    #    """
    #    Sempre fazemos reject com requeue.
    #    """
    #    expected_body = {"key": "value"}
    #    message = RabbitMQMessage(body=expected_body, delivery_tag=42)
    #    message.reject()

    #    queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
    #    await message.process(queue_mock)
    #    queue_mock.reject.assert_awaited_once_with(delivery_tag=42, requeue=True)
    #    self.assertEqual(0, queue_mock.ack.await_count)


    async def test_process_success_default_action(self):
        """
        Default é ACK, caso não digamos nada
        """
        message = RabbitMQMessage(body={}, delivery_tag=10)

        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_action_ack(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.ACK)

        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_action_reject(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.REJECT)

        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=False)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_action_requeue(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.REQUEUE)

        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_ack_to_requeue(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.ACK)
        message.reject(requeue=True)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_ack_to_reject(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.ACK)
        message.reject(requeue=False)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=False)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_reject_to_ack(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.REJECT)
        message.accept()
        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_from_reject_to_requeue(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.REJECT)
        message.reject(requeue=True)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_success_from_requeue_to_ack(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.REQUEUE)
        message.accept()
        await message.process_success(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_success_from_requeue_to_reject(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_success=Actions.REQUEUE)
        message.reject(requeue=False)
        await message.process_success(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=False)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_default_action(self):
        message = RabbitMQMessage(body={}, delivery_tag=10)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_action_requeue(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.REQUEUE)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_action_ack(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.ACK)

        await message.process_exception(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_exception_action_reject(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.REJECT)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=False)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_ack_to_requeue(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.ACK)
        message.reject(requeue=True)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_ack_to_reject(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.ACK)
        message.reject(requeue=False)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=False)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_reject_to_ack(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.REJECT)
        message.accept()

        await message.process_exception(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_exception_from_reject_to_requeue(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.REJECT)
        message.reject(requeue=True)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=True)
        self.queue_mock.ack.assert_not_awaited()

    async def test_process_exception_from_requeue_to_ack(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.REQUEUE)
        message.accept()

        await message.process_exception(self.queue_mock)
        self.queue_mock.ack.assert_awaited_with(delivery_tag=10)
        self.queue_mock.reject.assert_not_awaited()

    async def test_process_exception_from_requeue_to_reject(self):
        message = RabbitMQMessage(body={}, delivery_tag=10, on_exception=Actions.REQUEUE)
        message.reject(requeue=False)

        await message.process_exception(self.queue_mock)
        self.queue_mock.reject.assert_awaited_with(delivery_tag=10, requeue=False)
        self.queue_mock.ack.assert_not_awaited()

