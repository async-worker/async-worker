import unittest

from tom.queue import ExternalQueue
from tom.tests.utils import fetcher_js_b2w_msg


class QueueTests(unittest.TestCase):
    """
    A gente pode fazer isso tanto criando uma fila só pra isso e depois
    destruindo a mesma, ou mockando o amqp.Connection com o
    utils.MockedAMQPConnection
    """
    routing_key = 'api'
    mock_message = fetcher_js_b2w_msg

    def setUp(self):
        self.queue = ExternalQueue(host="10.168.26.113",
                                   username='guest',
                                   password='guest',
                                   queue_name="fetcher_api_b2w",
                                   exchange="fetcher")

    def test_it_put_messages(self):
        self.queue.put(body=self.mock_message,
                       routing_key="api")

    def test_it_fails_to_put_message_with_invalid_format(self):
        pass

    def test_it_gets_messages(self):
        message, delivery_tag = self.queue.get()

        self.assertIsInstance(message, dict)
        self.assertIsInstance(delivery_tag, int)

    def test_it_sends_invalid_messages_to_garbage(self):
        pass

    def test_it_acks_message_with_valid_delivery_tag(self):
        pass

    def test_it_fails_to_ack_message_with_invalid_delivery_tag(self):
        pass

