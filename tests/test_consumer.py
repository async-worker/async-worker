import asyncio
import unittest
from unittest import mock
from asynctest import CoroutineMock

from aioamqp.exceptions import AioamqpException

from worker.consumer import Consumer

from easyqueue.async import AsyncQueue

async def _handler(message_dict):
    return (42, message_dict)

class ConsumerTest(unittest.TestCase):

    def setUp(self):
        self.queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
        self.connection_parameters = ("127.0.0.1", "guest", "guest", 1024)
        self.one_route_fixture = {
            "route": ["/asgard/counts/ok"],
            "handler": _handler,
            "options": {
                "vhost": "/"
            }
        }

    def _run_async(self, coroutine, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(coroutine)

    def test_consumer_instantiate_async_queue_default_vhost(self):
        del self.one_route_fixture['options']['vhost']
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection_parameters

        self.assertTrue(isinstance(consumer.queue, AsyncQueue))
        self.assertEqual("/", connection_parameters['virtualhost'])
        self.assertEqual("127.0.0.1", connection_parameters['host'])
        self.assertEqual("guest", connection_parameters['login'])
        self.assertEqual("guest", connection_parameters['password'])

    def test_consumer_instantiate_async_queue_other_vhost(self):
        self.one_route_fixture.update({"options": {"vhost": "fluentd"}})
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection_parameters

        self.assertTrue(isinstance(consumer.queue, AsyncQueue))
        self.assertEqual("fluentd", connection_parameters['virtualhost'])

    def test_consumer_instantiate_async_queue_other_vhost_strip_slash(self):
        self.one_route_fixture.update({"options": {"vhost": "/fluentd"}})
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection_parameters

        self.assertTrue(isinstance(consumer.queue, AsyncQueue))
        self.assertEqual("fluentd", connection_parameters['virtualhost'])

    def test_consumer_instantiate_async_queue_prefetch_count(self):
        self.one_route_fixture.update({"options": {"vhost": "/fluentd"}})
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection_parameters

        self.assertTrue(isinstance(consumer.queue, AsyncQueue))
        self.assertEqual("fluentd", connection_parameters['virtualhost'])
        self.assertEqual(1024, consumer.queue.prefetch_count)

    def test_consumer_returns_correct_queue_name(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEqual(["/asgard/counts/ok"], consumer.queue_name)

    def test_on_queue_message_calls_inner_handler(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        coroutine = consumer.on_queue_message({"key": "value"}, delivery_tag=10, queue=self.queue_mock)
        self.assertEqual((42, {"key": "value"}), self._run_async(coroutine))


    def test_on_queue_message_auto_ack_on_success(self):
        """
        Se o handler registrado no @app.route() rodar com sucesso,
        devemos fazer o ack da mensagem
        """
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(ack=CoroutineMock())
        coroutine = consumer.on_queue_message({"key": "value"}, delivery_tag=10, queue=queue_mock)
        self.assertEqual((42, {"key": "value"}), self._run_async(coroutine))
        queue_mock.ack.assert_awaited_once_with(delivery_tag=10)

    def test_on_queue_message_rejects_on_exception(self):
        """
        Se o handler der raise em qualquer exception, devemos
        dar reject() na mensagem
        """
        async def exception_handler(message):
            return message.do_not_exist

        self.one_route_fixture['handler'] = exception_handler
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(ack=CoroutineMock(), reject=CoroutineMock())
        coroutine = consumer.on_queue_message({"key": "value"}, delivery_tag=10, queue=queue_mock)
        self.assertEqual(None, self._run_async(coroutine))
        queue_mock.reject.assert_awaited_once_with(delivery_tag=10, requeue=False)
        queue_mock.ack.assert_not_awaited

    def test_on_queue_message_precondition_failed_on_ack(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(ack=CoroutineMock(side_effect=AioamqpException))
        with self.assertRaises(AioamqpException):
            coroutine = consumer.on_queue_message({"key": "value"}, delivery_tag=10, queue=queue_mock)
            self._run_async(coroutine)
        queue_mock.ack.assert_awaited


    def test_return_correct_queue_name(self):
        """
        consumer.quene_name deve retornar o nome da fila que está sendo consumida.
        """
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEquals(self.one_route_fixture['route'], consumer.queue_name)

    def test_consume_all_queues(self):
        """
        """
        self.one_route_fixture['route'] = ["asgard/counts", "asgard/counts/errors"]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(consume=CoroutineMock())
        self._run_async(consumer.consume_all_queues(queue_mock))
        self.assertEqual(2, queue_mock.consume.await_count)
        self.assertEqual([mock.call(queue_name="asgard/counts"), mock.call(queue_name="asgard/counts/errors")], queue_mock.consume.await_args_list)

