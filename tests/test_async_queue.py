import asyncio
import json
import logging

import aioamqp
import asynctest
from asynctest.mock import CoroutineMock
from unittest.mock import Mock, patch, call, ANY
from easyqueue.async_queue import AsyncQueue, AsyncQueueConsumerDelegate, _ensure_connected
from easyqueue.exceptions import UndecodableMessageException, \
    InvalidMessageSizeException
from tests.utils import typed_any


class AsyncBaseTestCase:
    test_queue_name = 'test_queue'
    consumer_tag = 'consumer_666'

    def setUp(self):
        self.conn_params = dict(host='money.que.é.good',
                                username='nós',
                                password='não',
                                virtual_host='have',
                                heartbeat=5)
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
        self._protocol = CoroutineMock(
            name='protocol',
            close=CoroutineMock()
        )
        self._protocol.channel = SubscriptableCoroutineMock(
            return_value=CoroutineMock(
                publish=CoroutineMock(),
                basic_qos=CoroutineMock(),
                basic_consume=CoroutineMock()
            )
        )
        mocked_connection = CoroutineMock(return_value=[self._transport,
                                                        self._protocol])
        self._connect_patch = patch.object(aioamqp, 'connect', mocked_connection)
        self._connect = self._connect_patch.start()

    def get_consumer(self) -> AsyncQueueConsumerDelegate:
        raise NotImplementedError


class AsynQueueTests(asynctest.TestCase):
    async def test_it_raises_value_error_if_max_message_length_is_a_negative_number(self):
        invalid_value = -666
        with self.assertRaises(ValueError):
            AsyncQueue(host='Olha',
                       username='a',
                       password='explosão',
                       loop=Mock(),
                       delegate=Mock(),
                       max_message_length=invalid_value)

    async def test_it_doesnt_raise_value_error_if_max_message_length_is_a_positive_number(self):
        valid_value = 666
        queue = AsyncQueue(host='Essa',
                           username='menina',
                           password='é terrorista',
                           loop=Mock(),
                           delegate=Mock(),
                           max_message_length=valid_value)
        self.assertEqual(queue.max_message_length, valid_value)

    async def test_it_doesnt_raise_value_error_if_max_message_length_is_zero(self):
        valid_value = 0
        queue = AsyncQueue(host='diogommartins.com',
                           username='diogo',
                           password='XablauBolado',
                           loop=Mock(),
                           delegate=Mock(),
                           max_message_length=valid_value)
        self.assertEqual(queue.max_message_length, valid_value)

    async def test_it_raises_an_error_if_its_initialized_with_both_delegate_and_delegate_class(self):
        with self.assertRaises(ValueError):
            AsyncQueue(host='diogommartins.com',
                       username='diogo',
                       password='XablauBolado',
                       loop=Mock(),
                       delegate=Mock(),
                       delegate_class=Mock())

    async def test_its_possibile_to_initialize_without_a_delegate(self):
            queue = AsyncQueue(host='diogommartins.com',
                               username='diogo',
                               password='XablauBolado',
                               loop=Mock())
            self.assertIsInstance(queue, AsyncQueue)

    async def test_it_initializes_a_delegate_if_delegate_class_is_provided(self):
        delegate_class = Mock()
        loop = Mock()
        queue = AsyncQueue(host='diogommartins.com',
                           username='diogo',
                           password='XablauBolado',
                           loop=loop,
                           delegate_class=delegate_class)
        delegate_class.assert_called_once_with(loop=loop, queue=queue)


class AsyncQueueConnectionTests(AsyncBaseTestCase, asynctest.TestCase):
    def get_consumer(self):
        return CoroutineMock()

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

    async def test_connection_lock_ensures_amqp_connect_is_only_called_once(self):
        transport = Mock()
        protocol = Mock(channel=CoroutineMock(is_open=True))

        conn = (transport, protocol)
        with asynctest.patch('easyqueue.async_queue.aioamqp.connect', return_value=conn) as connect:
            await asyncio.gather(
                *(self.queue.connect() for _ in range(100))
            )
            self.assertEqual(connect.await_count, 1)

    async def test_connects_with_correct_args(self):
        expected = call(host=self.conn_params['host'],
                        password=self.conn_params['password'],
                        virtualhost=self.conn_params['virtual_host'],
                        login=self.conn_params['username'],
                        on_error=self.queue.delegate.on_connection_error,
                        loop=ANY,
                        heartbeat=self.conn_params['heartbeat'])

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

    async def test_it_puts_messages_into_queue_as_json_if_message_is_a_json_serializeable(self):
        message = {
            'artist': 'Great White',
            'song': 'Once Bitten Twice Shy',
            'album': 'Twice Shy'
        }
        exchange = Mock()
        routing_key = Mock()
        await self.queue.connect()
        await self.queue.put(data=message,
                             exchange=exchange,
                             routing_key=routing_key)

        expected = call(
            payload=json.dumps(message).encode(),
            routing_key=routing_key,
            exchange_name=exchange
        )
        self.assertEqual([expected],
                         self.queue._channel.publish.call_args_list)

    async def test_it_puts_messages_into_queue_as_is_if_message_is_already_a_json(self):
        message = {
            'artist': 'Great White',
            'song': 'Once Bitten Twice Shy',
            'album': 'Twice Shy'
        }
        exchange = Mock()
        routing_key = Mock()
        await self.queue.connect()
        await self.queue.put(serialized_data=json.dumps(message),
                             exchange=exchange,
                             routing_key=routing_key)

        expected = call(
            payload=json.dumps(message).encode(),
            routing_key=routing_key,
            exchange_name=exchange
        )
        self.assertEqual([expected],
                         self.queue._channel.publish.call_args_list)

    async def test_it_raises_an_error_if_both_data_and_json_are_passed_to_put_message(self):
        message = {
            'artist': 'Great White',
            'song': 'Once Bitten Twice Shy',
            'album': 'Twice Shy'
        }
        exchange = Mock()
        routing_key = Mock()
        await self.queue.connect()
        with self.assertRaises(ValueError):
            await self.queue.put(serialized_data=json.dumps(message),
                                 data=message,
                                 exchange=exchange,
                                 routing_key=routing_key)

        expected = call(
            payload=json.dumps(message).encode(),
            routing_key=routing_key,
            exchange_name=exchange
        )
        self.queue._channel.publish.assert_not_called()

    async def test_it_encodes_payload_into_bytes_if_payload_is_str(self):
        payload = json.dumps({"dog": "Xablau"})
        exchange = Mock()
        routing_key = Mock()
        await self.queue.connect()
        await self.queue.put(serialized_data=payload,
                             exchange=exchange,
                             routing_key=routing_key)

        self.queue._channel.publish.assert_awaited_once_with(
            payload=payload.encode(),
            routing_key=routing_key,
            exchange_name=exchange
        )

    async def test_it_doesnt_encodes_payload_into_bytes_if_payload_is_already_bytes(self):
        payload = json.dumps({"dog": "Xablau"}).encode()
        exchange = Mock()
        routing_key = Mock()
        await self.queue.connect()

        await self.queue.put(serialized_data=payload,
                             exchange=exchange,
                             routing_key=routing_key)

        self.queue._channel.publish.assert_awaited_once_with(
            payload=payload,
            routing_key=routing_key,
            exchange_name=exchange
        )

    async def test_connect_gets_awaited_if_put_is_called_before_connect(self):
        message = {
            'artist': 'Great White',
            'song': 'Once Bitten Twice Shy',
            'album': 'Twice Shy'
        }
        with asynctest.patch.object(self.queue, 'connect') as connect, \
             asynctest.patch.object(self.queue, '_channel', Mock(is_open=False, publish=CoroutineMock())):
            await self.queue.put(data=message, routing_key='Xablau')
            connect.assert_awaited_once()

    async def test_it_raises_and_error_if_put_message_isnt_json_serializeable(self):
        message = Mock()

        exchange = Mock()
        routing_key = Mock()
        await self.queue.connect()
        with self.assertRaises(TypeError):
            await self.queue.put(message,
                                 exchange=exchange,
                                 routing_key=routing_key)
        self.queue._channel.publish.assert_not_called()

    async def test_it_acks_messages(self):
        await self.queue.connect()

        tag = 666
        with patch.object(self.queue._channel,
                          'basic_client_ack',
                          CoroutineMock()) as basic_client_ack:
            await self.queue.ack(delivery_tag=tag)
            basic_client_ack.assert_awaited_once_with(tag)

    async def test_connect_gets_awaited_if_ack_is_called_before_connect(self):
        with asynctest.patch.object(self.queue, 'connect') as connect, \
             asynctest.patch.object(self.queue, '_channel', Mock(is_open=False, basic_client_ack=CoroutineMock())):
            await self.queue.ack(delivery_tag=1)
            connect.assert_awaited_once()

    async def test_it_rejects_messages_without_requeue(self):
        await self.queue.connect()

        tag = 666
        with patch.object(self.queue._channel,
                          'basic_reject',
                          CoroutineMock()) as basic_reject:
            await self.queue.reject(delivery_tag=tag)
            basic_reject.assert_awaited_once_with(delivery_tag=tag, requeue=False)

    async def test_it_rejects_messages_with_requeue(self):
        await self.queue.connect()

        tag = 666
        with patch.object(self.queue._channel,
                          'basic_reject',
                          CoroutineMock()) as basic_reject:
            await self.queue.reject(delivery_tag=tag, requeue=True)
            basic_reject.assert_awaited_once_with(delivery_tag=tag, requeue=True)

    async def test_connect_gets_awaited_if_reject_is_called_before_connect(self):
        with asynctest.patch.object(self.queue, 'connect') as connect, \
             asynctest.patch.object(self.queue, '_channel', Mock(is_open=False, basic_reject=CoroutineMock())):
            await self.queue.reject(delivery_tag=1)
            connect.assert_awaited_once()


class AsyncQueueConsumerTests(AsyncBaseTestCase, asynctest.TestCase):
    consumer_tag = 666

    def get_consumer(self):
        return CoroutineMock(
            on_before_start_consumption=CoroutineMock(),
            on_consumption_start=CoroutineMock()
        )

    async def test_it_raises_an_error_if_consume_is_called_without_a_delegate(self):
        with self.assertRaises(RuntimeError):
            self.queue.delegate = None
            await self.queue.consume(queue_name=Mock(),
                                     consumer_name=Mock())

    async def test_it_calls_will_start_consumption_before_queue_consume(self):
        await self.queue.connect()

        with asynctest.patch.object(self.queue._channel,
                                    'basic_consume',
                                    side_effect=Exception()):

            queue_name = Mock()
            self.queue.delegate.on_before_start_consumption.assert_not_called()
            with self.assertRaises(Exception):
                await self.queue.consume(queue_name, Mock())

            self.queue.delegate.on_before_start_consumption.called_once_with(queue_name,
                                                                             queue=self.queue)

    async def test_connect_gets_awaited_if_consume_is_called_before_connect(self):
        channel = Mock(
            is_open=False,
            basic_qos=CoroutineMock(),
            basic_consume=CoroutineMock()
        )
        with asynctest.patch.object(self.queue, 'connect') as connect, \
             asynctest.patch.object(self.queue, '_channel', channel):
            queue_name = Mock()
            await self.queue.consume(queue_name)
            connect.assert_awaited_once()

    async def test_calling_consume_starts_message_consumption(self):
        await self.queue.connect()
        await self.queue.consume(Mock(), Mock())

        self.assertEqual(self.queue._channel.basic_consume.call_count, 1)

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

    async def test_calling_consume_starts_a_connection(self):
        q_name = 'miles.davis_blue.in.green'

        class Foo(AsyncQueueConsumerDelegate):
            loop = self.loop
            queue_name = q_name
            queue = self.queue

            on_connection_error = CoroutineMock()
            on_message_handle_error = CoroutineMock()
            on_queue_error = CoroutineMock()
            on_queue_message = CoroutineMock()
            on_consumer_start = CoroutineMock()

        consumer = Foo()
        self.queue.delegate = consumer
        with patch.object(self.queue, 'consume', side_effect=CoroutineMock()) as patched_consume:
            await consumer.queue.start_consumer()
            patched_consume.assert_called_once_with(queue_name=q_name)
            self.assertTrue(self._connect.called)

    async def test_starting_the_consumer_calls_on_consumer_starts_on_delegate_class(self):
        consumer = Mock(queue=self.queue, on_consumption_start=CoroutineMock())
        self.queue.delegate = consumer
        consumer_tag = 'Xablau'
        with patch.object(self.queue, 'consume', CoroutineMock(return_value=consumer_tag)):
            await consumer.queue.start_consumer()
            consumer.on_consumption_start.assert_awaited_once_with(consumer_tag, queue=self.queue)

    async def test_calling_consume_starts_a_consumption_task(self):
        q_name = 'dance.to.the.decadence.dance'

        class Foo(AsyncQueueConsumerDelegate):
            queue_name = q_name
            queue = CoroutineMock(
                start_consumer=CoroutineMock()
            )

            on_connection_error = CoroutineMock()
            on_consumption_start = CoroutineMock()
            on_message_handle_error = CoroutineMock()
            on_queue_error = CoroutineMock()
            on_queue_message = CoroutineMock()

        consumer = Foo()
        self.queue.delegate = consumer

        await consumer.start()

        consumer.queue.start_consumer.assert_awaited_once()


class AsyncQueueConsumerHandlerMethodsTests(AsyncBaseTestCase, asynctest.TestCase):
    consumer_tag = 666

    def get_consumer(self):
        return CoroutineMock(
            on_before_start_consumption=CoroutineMock(),
            on_message_handle_error=CoroutineMock()
        )

    async def setUp(self):
        super().setUp()
        self.envelope = Mock(name='Envelope')
        self.properties = Mock(name='Properties')
        await self.queue.connect()

        await self.queue.consume(queue_name=self.test_queue_name,
                                 consumer_name=self.__class__.__name__)

    async def test_it_calls_on_queue_error_if_message_isnt_a_valid_json(self):
        content = "Subirusdoitiozin"
        with patch.object(self.queue, '_handle_callback',
                          CoroutineMock()) as _handle_callback:
            await self.queue._handle_message(channel=self.queue._channel,
                                             body=content,
                                             envelope=self.envelope,
                                             properties=self.properties)

            consumer = self.queue.delegate
            self.assertFalse(consumer.on_queue_message.called)

            _handle_callback.assert_called_once_with(consumer.on_queue_error,
                                                     body=content,
                                                     delivery_tag=self.envelope.delivery_tag,
                                                     error=typed_any(UndecodableMessageException),
                                                     queue=self.queue)

    async def test_it_calls_on_queue_error_if_message_length_is_too_big(self):
        content = {
            "artist": "Mr. Big",
            "album": "Big, Bigger, Biggest! The Best of Mr. Big",
            "song": "Rock & Roll Over"
        }
        json_content = json.dumps(content)

        Actual_Size = len(json_content)
        self.queue.max_message_length = Actual_Size - 1

        with patch.object(self.queue, '_handle_callback',
                          CoroutineMock()) as _handle_callback:
            await self.queue._handle_message(channel=self.queue._channel,
                                             body=json_content,
                                             envelope=self.envelope,
                                             properties=self.properties)

            consumer = self.queue.delegate
            self.assertFalse(consumer.on_queue_message.called)

            _handle_callback.assert_called_once_with(consumer.on_queue_error,
                                                     body=json_content,
                                                     delivery_tag=self.envelope.delivery_tag,
                                                     error=typed_any(InvalidMessageSizeException),
                                                     queue=self.queue)

    async def test_it_calls_on_queue_message_if_message_is_a_valid_json_as_bytes(self):
        content = {
            'artist': 'Caetano Veloso',
            'song': 'Não enche',
            'album': 'Livro'
        }
        body = bytes(json.dumps(content), encoding='utf-8')
        with patch.object(self.queue, '_handle_callback',
                          CoroutineMock()) as _handle_callback:
            await self.queue._handle_message(channel=self.queue._channel,
                                             body=body,
                                             envelope=self.envelope,
                                             properties=self.properties)

            consumer = self.queue.delegate
            self.assertFalse(consumer.on_queue_error.called)

            _handle_callback.assert_called_once_with(consumer.on_queue_message,
                                                          content=content,
                                                          delivery_tag=self.envelope.delivery_tag,
                                                          queue=self.queue)

    async def test_it_calls_on_queue_message_if_message_is_a_valid_json(self):
        content = {
            'artist': 'Caetano Veloso',
            'song': 'Não enche',
            'album': 'Livro'
        }

        with patch.object(self.queue, '_handle_callback',
                          CoroutineMock()) as _handle_callback:
            await self.queue._handle_message(channel=self.queue._channel,
                                             body=json.dumps(content),
                                             envelope=self.envelope,
                                             properties=self.properties)

            consumer = self.queue.delegate
            self.assertFalse(consumer.on_queue_error.called)

            _handle_callback.assert_called_once_with(consumer.on_queue_message,
                                                          content=content,
                                                          delivery_tag=self.envelope.delivery_tag,
                                                          queue=self.queue)

    async def test_it_calls_on_message_handle_error_if_message_handler_raises_an_error(self):
        content = {
            'artist': 'Caetano Veloso',
            'song': 'Não enche',
            'album': 'Livro'
        }

        consumer = self.queue.delegate
        error = consumer.on_queue_message.side_effect = KeyError()
        kwargs = dict(callback=consumer.on_queue_message,
                      channel=self.queue._channel,
                      body=json.dumps(content),
                      envelope=self.envelope,
                      properties=self.properties)
        await self.queue._handle_callback(**kwargs)

        self.assertFalse(consumer.on_queue_error.called)

        del kwargs['callback']

        consumer.on_message_handle_error.assert_called_once_with(handler_error=error,
                                                                 **kwargs)


class EnsureConnectedDecoratorTests(asynctest.TestCase):
    async def test_it_calls_connect_if_queue_isnt_connected(self):
        async_queue = Mock(
            is_connected=False,
            connect=CoroutineMock()
        )
        coro = CoroutineMock()
        wrapped = _ensure_connected(coro)
        await wrapped(async_queue, 1, dog='Xablau')

        async_queue.connect.assert_awaited_once()
        coro.assert_awaited_once_with(async_queue, 1, dog='Xablau')

    async def test_it_doesnt_calls_connect_if_queue_is_connected(self):
        async_queue = Mock(
            is_connected=True,
            connect=CoroutineMock()
        )
        coro = CoroutineMock()
        wrapped = _ensure_connected(coro)
        await wrapped(async_queue, 1, dog='Xablau')

        async_queue.connect.assert_not_awaited()
        coro.assert_awaited_once_with(async_queue, 1, dog='Xablau')

    async def test_it_waits_before_trying_to_reconnect_if_connect_fails(self):
        seconds = 666
        async_queue = Mock(
            is_connected=False,
            is_running=True,
            connect=CoroutineMock(side_effect=[ConnectionError,  True]),
            seconds_between_conn_retry=seconds
        )
        coro = CoroutineMock()
        with asynctest.patch("easyqueue.async_queue.asyncio.sleep") as sleep:
            wrapped = _ensure_connected(coro)
            await wrapped(async_queue, 1, dog='Xablau')
            sleep.assert_awaited_once_with(seconds)

        # todo: CoroutineMock.side_effect is raised only on call, not on await
        async_queue.connect.assert_has_awaits([call()])
        async_queue.connect.assert_has_calls([call(), call()])
        coro.assert_awaited_once_with(async_queue, 1, dog='Xablau')

    async def test_it_logs_connection_retries_if_a_logger_istance_is_available(self):
        async_queue = Mock(
            is_connected=False,
            is_running=True,
            connect=CoroutineMock(side_effect=[ConnectionError, True]),
            logger=Mock(spec=logging.Logger)
        )
        coro = CoroutineMock()
        with asynctest.patch("easyqueue.async_queue.asyncio.sleep") as sleep:
            wrapped = _ensure_connected(coro)
            await wrapped(async_queue, 1, dog='Xablau')

        async_queue.logger.error.assert_called_once()
