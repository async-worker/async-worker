import asyncio

import aiobotocore
from asynctest import TestCase

from asyncworker import App, RouteTypes
from asyncworker.connections import SQSConnection

consume_callback_shoud_not_be_called = False
handler_with_requeue_called = 0
handler_without_requeue_called = 0
successful_message_value_is_equal = False

message_processed_multiple_connections = False
message_processed_other_vhost = False


class SQSConsumerTest(TestCase):
    async def setUp(self):
        self.queue_url = "https://sqs.us-east-1.amazonaws.com/375164415270/messaging-diogo-asyncworker-test"
        self.connection = SQSConnection(region="us-east-1")
        self.app = App(connections=[self.connection])

    async def tearDown(self):
        handler_without_requeue_called = 0
        handler_with_requeue_called = 0

    async def test_process_one_successful_message(self):
        """
        Um worker com dois handlers um que publica e outro que lê a mensagem
        No final um ack() é chamado
        """
        message = {"key": "value"}

        @self.app.sqs.consume([self.queue_url])
        async def handler(messages):
            global successful_message_value_is_equal
            successful_message_value_is_equal = (
                messages[0].body["key"] == message["key"]
            )

        await self.app.startup()
        await asyncio.sleep(1000)
        await self.app.shutdown()
