import asyncio
import unittest
from unittest.mock import Mock, patch, call, ANY

import asynctest
from asynctest.mock import CoroutineMock

import aioamqp

from easyqueue.async import AsyncQueueConsumer, AsyncQueueConsumerDelegate
from easyqueue.tests.utils import unittest_run_loop, make_mocked_coro


class AsyncBaseTestCase:
    test_queue_name = 'test_queue'

    def setUp(self):
        self.conn_params = dict(host='money.que.é.good',
                                username='nos',
                                password='nao',
                                virtual_host='have')
        self.queue = AsyncQueueConsumer(**self.conn_params,
                                        delegate=self.get_consumer())
        self.mock_connection()

    def tearDown(self):
        self._connect_patch.stop()

    def mock_connection(self):
        self._transport = CoroutineMock(name='transport')
        self._protocol = CoroutineMock(name='protocol')
        mocked_connection = CoroutineMock(return_value=[self._transport,
                                                        self._protocol])
        self._connect_patch = patch.object(aioamqp, 'connect', mocked_connection)
        self._connect = self._connect_patch.start()

    def get_consumer(self) -> AsyncQueueConsumerDelegate:
        raise NotImplementedError
    #
    # async def create_queue(self):
    #     await self.queue._channel.queue_declare(self.test_queue_name)
    #
    # async def _destroy_queue(self):
    #     await self.queue._channel.queue_delete(self.test_queue_name)


class AsyncQeueConnectionTests(AsyncBaseTestCase, asynctest.TestCase):
    def get_consumer(self):
        consumer = Mock()
        consumer.on_queue_message = CoroutineMock()
        consumer.on_queue_error = CoroutineMock()
        return consumer

    async def test_connect_opens_a_connection_communication_channel(self):
        self.assertFalse(self.queue.is_connected)
        self.assertIsNone(self.queue._protocol)
        self.assertIsNone(self.queue._transport)
        self.assertIsNone(self.queue._channel)

        await self.queue.connect()

        self.assertTrue(self.queue.is_connected)
        self.assertEqual(self.queue._protocol, self._protocol)
        self.assertEqual(self.queue._transport, self._transport)
        self.assertIsNotNone(self.queue._channel)

    async def test_connects_with_correct_args(self):
        expected = call(host=self.conn_params['host'],
                        password=self.conn_params['password'],
                        virtualhost=self.conn_params['virtual_host'],
                        login=self.conn_params['username'],
                        loop=ANY)

        await self.queue.connect()
        self.assertEqual([expected], self._connect.call_args_list)

