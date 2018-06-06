import asyncio
import unittest

from worker.consumer import Consumer

from easyqueue.async import AsyncQueue

async def _handler(message_dict):
    return (42, message_dict)

class ConsumerTest(unittest.TestCase):

    def setUp(self):
        self.connection_parameters = ("127.0.0.1", "guest", "guest", 1024)
        self.one_route_fixture = {
            "route": "/asgard/counts/ok",
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
        self.one_route_fixture.update({"options": {"vhost": "/fluentd"}})
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection_parameters

        self.assertTrue(isinstance(consumer.queue, AsyncQueue))
        self.assertEqual("/fluentd", connection_parameters['virtualhost'])

    def test_consumer_instantiate_async_queue_prefetch_count(self):
        self.one_route_fixture.update({"options": {"vhost": "/fluentd"}})
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection_parameters

        self.assertTrue(isinstance(consumer.queue, AsyncQueue))
        self.assertEqual("/fluentd", connection_parameters['virtualhost'])
        self.assertEqual(1024, consumer.queue.prefetch_count)

    def test_consumer_returns_correct_queue_name(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEqual("/asgard/counts/ok", consumer.queue_name)

    def test_on_queue_message_calls_inner_handler(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        coroutine = consumer.on_queue_message({"key": "value"}, delivery_tag=10, queue=None)
        self.assertEqual((42, {"key": "value"}), self._run_async(coroutine))


    def test_on_queue_message_auto_ack_on_success(self):
        """
        Se o handler registrado no @app.route() rodar com sucesso,
        devemos fazer o ack da mensagem
        """
        self.fail()

    def test_on_queue_message_rejects_on_exception(self):
        """
        Se o handler der raise em qualquer exception, devemos
        dar reject() na mensagem
        """
        self.fail()

    def test_return_correct_queue_name(self):
        """
        consumer.quene_name deve retornar o nome da fila que está sendo consumida.
        """
        self.fail()
