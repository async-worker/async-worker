import json
import uuid
from random import randint

import aioamqp
import asynctest
from asynctest.mock import CoroutineMock
from unittest.mock import Mock, patch, call, ANY
from easyqueue.async import AsyncQueue, AsyncQueueConsumerDelegate
from easyqueue.exceptions import UndecodableMessageException
from easyqueue.tests.utils import typed_any


class AsyncBaseTestCase:
    test_queue_name = 'test_queue'
    consumer_tag = 'consumer_666'

    def setUp(self):
        self.conn_params = dict(host='money.que.é.good',
                                username='nós',
                                password='não',
                                virtual_host='have')
        self.queue = AsyncQueue(**self.conn_params,
                                delegate=self.get_consumer())
        self.mock_connection()

    def tearDown(self):
        self._connect_patch.stop()

    def mock_connection(self):
        class SubscriptableCoroutineMock(CoroutineMock):
            def __getitem__(_, item):
                if item == 'consumer_tag':
                    return self.consumer_tag
                raise NotImplementedError

        self._transport = CoroutineMock(name='transport')
        self._protocol = CoroutineMock(name='protocol')
        self._protocol.channel = SubscriptableCoroutineMock()
        mocked_connection = CoroutineMock(return_value=[self._transport,
                                                        self._protocol])
        self._connect_patch = patch.object(aioamqp, 'connect', mocked_connection)
        self._connect = self._connect_patch.start()

    def get_consumer(self) -> AsyncQueueConsumerDelegate:
        raise NotImplementedError


class AsyncQeueConnectionTests(AsyncBaseTestCase, asynctest.TestCase):
    def get_consumer(self):
        return Mock()

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

    async def test_it_closes_the_connection(self):
        await self.queue.connect()
        await self.queue.close()

        self.assertTrue(self._protocol.close.called)
        self.assertTrue(self._transport.close.called)

    async def test_it_dosent_call_consumer_handler_methods(self):
        self.assertFalse(self.queue.delegate.on_queue_message.called)
        self.assertFalse(self.queue.delegate.on_queue_error.called)


class AsynQueueConsumerTests(AsyncBaseTestCase, asynctest.TestCase):
    consumer_tag = 666

    def get_consumer(self):
        return Mock()

    async def test_calling_consume_without_a_connection_raises_an_error(self):
        with self.assertRaises(ConnectionError):
            await self.queue.consume(queue_name=Mock(),
                                     consumer_name=Mock())

    async def test_calling_consume_starts_message_consumption(self):
        await self.queue.connect()
        await self.queue.consume(Mock(), Mock())

        self.queue._channel.basic_consume.assert_called_once()

    async def test_calling_consume_binds_handler_method(self):
        await self.queue.connect()

        queue_name = Mock()
        consumer_name = Mock()
        expected_prefetch_count = 666

        self.queue.prefetch_count = expected_prefetch_count
        await self.queue.consume(queue_name, consumer_name)

        expected = call(callback=self.queue._handle_message,
                        queue_name=queue_name,
                        consumer_tag=consumer_name)
        self.assertEqual([expected],
                         self.queue._channel.basic_consume.call_args_list)

    async def test_calling_consume_sets_a_prefetch_qos(self):
        await self.queue.connect()

        expected_prefetch_count = 666
        self.queue.prefetch_count = expected_prefetch_count
        await self.queue.consume(Mock(), Mock())

        expected = call(connection_global=ANY,
                        prefetch_count=expected_prefetch_count,
                        prefetch_size=0)
        self.assertEqual([expected],
                         self.queue._channel.basic_qos.call_args_list)


class AsyncQeueConsumerHandlerMethodsTests(AsyncBaseTestCase, asynctest.TestCase):
    consumer_tag = 666

    def get_consumer(self):
        consumer = Mock()
        consumer.on_queue_message = CoroutineMock()
        consumer.on_queue_error = CoroutineMock()
        return consumer

    async def setUp(self):
        super().setUp()
        self.envelope = Mock(name='Envelope')
        self.properties = Mock(name='Properties')
        await self.queue.connect()

        await self.queue.consume(queue_name=self.test_queue_name,
                                 consumer_name=self.__class__.__name__)

    async def test_it_calls_on_queue_error_if_message_isnt_a_valid_json(self):
        content = "Subirusdoitiozin"
        await self.queue._handle_message(channel=self.queue._channel,
                                         body=content,
                                         envelope=self.envelope,
                                         properties=self.properties)

        consumer = self.queue.delegate
        self.assertFalse(consumer.on_queue_message.called)

        expected = call(body=content,
                        delivery_tag=self.envelope.delivery_tag,
                        error=typed_any(UndecodableMessageException),
                        queue=self.queue)
        self.assertEqual(consumer.on_queue_error.call_args_list, [expected])

    async def test_it_calls_on_queue_message_if_message_is_a_valid_json_as_bytes(self):
        content = {
            'artist': 'Caetano Veloso',
            'song': 'Não enche',
            'album': 'Livro'
        }
        body = bytes(json.dumps(content), encoding='utf-8')
        await self.queue._handle_message(channel=self.queue._channel,
                                         body=body,
                                         envelope=self.envelope,
                                         properties=self.properties)

        consumer = self.queue.delegate
        self.assertFalse(consumer.on_queue_error.called)

        expected = call(content=content,
                        delivery_tag=self.envelope.delivery_tag,
                        queue=self.queue)
        self.assertEqual(consumer.on_queue_message.call_args_list, [expected])

    async def test_it_calls_on_queue_message_if_message_is_a_valid_json(self):
        content = {
            'artist': 'Caetano Veloso',
            'song': 'Não enche',
            'album': 'Livro'
        }
        await self.queue._handle_message(channel=self.queue._channel,
                                         body=json.dumps(content),
                                         envelope=self.envelope,
                                         properties=self.properties)

        consumer = self.queue.delegate
        self.assertFalse(consumer.on_queue_error.called)

        expected = call(content=content,
                        delivery_tag=self.envelope.delivery_tag,
                        queue=self.queue)
        self.assertEqual(consumer.on_queue_message.call_args_list, [expected])
