import asyncio
import unittest
from asynctest import CoroutineMock, mock, Mock
import asynctest

from asyncworker.easyqueue.queue import JsonQueue
from aioamqp.exceptions import AioamqpException

from asyncworker.bucket import Bucket
from asyncworker.consumer import Consumer
from asyncworker import conf, App
from asyncworker.easyqueue.message import AMQPMessage
from asyncworker.options import Events, Actions, RouteTypes


async def _handler(message):
    return (42, message[0].body)


class ConsumerTest(asynctest.TestCase):
    use_default_loop = True

    def setUp(self):
        self.queue_mock = Mock(
            connection=Mock(is_connected=True), spec=JsonQueue
        )
        self.logger_mock = CoroutineMock(
            info=CoroutineMock(), debug=CoroutineMock(), error=CoroutineMock()
        )
        self.connection_parameters = ("127.0.0.1", "guest", "guest", 1024)
        self.one_route_fixture = {
            "routes": ["/asgard/counts/ok"],
            "handler": _handler,
            "options": {
                "vhost": "/",
                "bulk_size": 1,
                "bulk_flush_interval": 60,
                Events.ON_SUCCESS: Actions.ACK,
                Events.ON_EXCEPTION: Actions.REQUEUE,
            },
        }
        self.app = App(
            **{
                "host": "127.0.0.1",
                "user": "guest",
                "password": "guest",
                "prefetch_count": 1024,
            }
        )
        self.mock_message = self._make_msg()
        mock.patch.object(
            conf, "settings", mock.Mock(FLUSH_TIMEOUT=0.1)
        ).start()

    def _make_msg(self, **kwargs) -> AMQPMessage:
        default_kwargs = dict(
            delivery_tag=10,
            connection=self.queue_mock.connection,
            channel=Mock(),
            queue=self.queue_mock,
            envelope=Mock(),
            properties=Mock(),
            deserialization_method=Mock(),
            queue_name="queue_name",
            serialized_data=Mock(),
        )
        return AMQPMessage(**{**default_kwargs, **kwargs})

    def tearDown(self):
        mock.patch.stopall()

    def test_consumer_adjusts_bulk_size(self):
        """
        Se escolhermos um prefetch menor do que o bulk_size, significa que nosso "bucket"
        nunca vai encher e isso significa que nosso consumer ficará congelado, em um deadlock:
            Ele estará esperando o bucket encher
            E ao mesmo tempo estará o esperando o bucket esvaziar para que possa receber mais mensagens do RabbitMQ


        Vamos setar o bulk_size com sendo min(bulk_size, prefetch_count)
        """
        self.one_route_fixture["options"]["bulk_size"] = 2048
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEqual(1024, consumer.bucket.size)

        self.one_route_fixture["options"]["bulk_size"] = 4096
        consumer = Consumer(
            self.one_route_fixture,
            host="127.0.0.1",
            username="guest",
            password="guest",
            prefetch_count=8192,
        )
        self.assertEqual(4096, consumer.bucket.size)

    def test_consumer_instantiate_using_bucket_class(self):
        class MyBucket(Bucket):
            pass

        consumer = Consumer(
            self.one_route_fixture,
            *self.connection_parameters,
            bucket_class=MyBucket,
        )
        self.assertTrue(isinstance(consumer.bucket, MyBucket))

    def test_consumer_instantiate_correct_size_bucket(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEqual(
            self.one_route_fixture["options"]["bulk_size"], consumer.bucket.size
        )

    def test_consumer_instantiate_async_queue_default_vhost(self):
        del self.one_route_fixture["options"]["vhost"]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection.connection_parameters

        self.assertTrue(isinstance(consumer.queue, JsonQueue))
        self.assertEqual("/", connection_parameters["virtualhost"])
        self.assertEqual("127.0.0.1", connection_parameters["host"])
        self.assertEqual("guest", connection_parameters["login"])
        self.assertEqual("guest", connection_parameters["password"])

    def test_consumer_instantiate_async_queue_other_vhost(self):
        self.one_route_fixture["options"]["vhost"] = "fluentd"
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection.connection_parameters

        self.assertTrue(isinstance(consumer.queue, JsonQueue))
        self.assertEqual("fluentd", connection_parameters["virtualhost"])

    def test_consumer_instantiate_async_queue_other_vhost_strip_slash(self):
        self.one_route_fixture["options"]["vhost"] = "/fluentd"
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection.connection_parameters

        self.assertTrue(isinstance(consumer.queue, JsonQueue))
        self.assertEqual("fluentd", connection_parameters["virtualhost"])

    def test_consumer_instantiate_async_queue_prefetch_count(self):
        self.one_route_fixture["options"]["vhost"] = "/fluentd"
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        connection_parameters = consumer.queue.connection.connection_parameters

        self.assertTrue(isinstance(consumer.queue, JsonQueue))
        self.assertEqual("fluentd", connection_parameters["virtualhost"])
        self.assertEqual(1024, consumer.queue.prefetch_count)

    def test_consumer_returns_correct_queue_name(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEqual(["/asgard/counts/ok"], consumer.queue_name)

    async def test_on_queue_message_calls_inner_handler(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        result = await consumer.on_queue_message(msg=self.mock_message)

        self.assertEqual((42, self.mock_message.deserialized_data), result)

    async def test_on_exception_requeue_message(self):
        """
        Confirma que em caso de exceção, será feito `message.reject(requeue=True)`
        """

        @self.app.route(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={Events.ON_EXCEPTION: Actions.REQUEUE},
        )
        async def _handler(messages):
            raise Exception("BOOM!")

        route = self.app.routes_registry.amqp_routes[0]
        consumer = Consumer(route, *self.connection_parameters)

        with self.assertRaises(Exception):
            await consumer.on_queue_message(msg=self.mock_message)
        self.queue_mock.reject.assert_awaited_with(
            delivery_tag=self.mock_message.delivery_tag, requeue=True
        )

    async def test_on_exception_reject_message(self):
        @self.app.route(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={Events.ON_EXCEPTION: Actions.REJECT},
        )
        async def _handler(messages):
            raise Exception("BOOM!")

        route = self.app.routes_registry.amqp_routes[0]
        consumer = Consumer(route, *self.connection_parameters)

        with self.assertRaises(Exception):
            await consumer.on_queue_message(msg=self.mock_message)
        self.queue_mock.reject.assert_awaited_with(
            delivery_tag=self.mock_message.delivery_tag, requeue=False
        )

    async def test_on_exception_ack_message(self):
        @self.app.route(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={Events.ON_EXCEPTION: Actions.ACK},
        )
        async def _handler(messages):
            raise Exception("BOOM!")

        route = self.app.routes_registry.amqp_routes[0]
        consumer = Consumer(route, *self.connection_parameters)
        with self.assertRaises(Exception):
            await consumer.on_queue_message(msg=self.mock_message)

        self.queue_mock.ack.assert_awaited_with(
            delivery_tag=self.mock_message.delivery_tag
        )

    async def test_on_success_ack(self):
        @self.app.route(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={Events.ON_SUCCESS: Actions.ACK},
        )
        async def _handler(messages):
            return 42

        route = self.app.routes_registry.amqp_routes[0]
        consumer = Consumer(route, *self.connection_parameters)

        await consumer.on_queue_message(msg=self.mock_message)
        self.queue_mock.ack.assert_awaited_with(
            delivery_tag=self.mock_message.delivery_tag
        )

    async def test_on_success_reject(self):
        @self.app.route(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={Events.ON_SUCCESS: Actions.REJECT},
        )
        async def _handler(messages):
            return 42

        route = self.app.routes_registry.amqp_routes[0]
        consumer = Consumer(route, *self.connection_parameters)

        await consumer.on_queue_message(msg=self.mock_message)
        self.queue_mock.reject.assert_awaited_with(
            delivery_tag=self.mock_message.delivery_tag, requeue=False
        )

    async def test_on_success_requeue(self):
        @self.app.route(
            ["queue"],
            type=RouteTypes.AMQP_RABBITMQ,
            options={Events.ON_SUCCESS: Actions.REQUEUE},
        )
        async def _handler(messages):
            return 42

        route = self.app.routes_registry.amqp_routes[0]
        consumer = Consumer(route, *self.connection_parameters)

        await consumer.on_queue_message(msg=self.mock_message)
        self.queue_mock.reject.assert_awaited_with(
            delivery_tag=self.mock_message.delivery_tag, requeue=True
        )

    async def test_on_queue_message_auto_ack_on_success(self):
        """
        Se o handler registrado no @app.route() rodar com sucesso,
        devemos fazer o ack da mensagem
        """
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)

        result = await consumer.on_queue_message(msg=self.mock_message)

        self.assertEqual((42, self.mock_message.deserialized_data), result)
        self.queue_mock.ack.assert_awaited_once_with(
            delivery_tag=self.mock_message.delivery_tag
        )
        self.queue_mock.reject.assert_not_awaited()

    async def test_on_exception_default_action_bulk_messages(self):
        """
        Se o handler der raise em qualquer exception, devemos
        dar reject() na mensagem
        """

        async def exception_handler(message):
            return message.do_not_exist

        self.one_route_fixture["handler"] = exception_handler
        self.one_route_fixture["options"]["bulk_size"] = 2

        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)

        msgs = [self._make_msg(delivery_tag=1), self._make_msg(delivery_tag=2)]
        with self.assertRaises(AttributeError):
            await consumer.on_queue_message(msg=msgs[0])
            await consumer.on_queue_message(msg=msgs[1])

        self.queue_mock.reject.assert_has_awaits(
            [
                mock.call(delivery_tag=msgs[0].delivery_tag, requeue=True),
                mock.call(delivery_tag=msgs[1].delivery_tag, requeue=True),
            ],
            any_order=True,
        )
        self.queue_mock.ack.assert_not_awaited()

    async def test_on_queue_message_precondition_failed_on_ack(self):
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(
            ack=CoroutineMock(side_effect=AioamqpException)
        )
        with self.assertRaises(AioamqpException):
            await consumer.on_queue_message(
                msg=self._make_msg(queue=queue_mock)
            )

    async def test_on_queue_message_bulk_size_one(self):
        class MyBucket(Bucket):
            def pop_all(self):
                return self._items

        handler_mock = CoroutineMock()
        self.one_route_fixture["handler"] = handler_mock
        self.one_route_fixture["options"]["bulk_size"] = 1

        consumer = Consumer(
            self.one_route_fixture,
            *self.connection_parameters,
            bucket_class=MyBucket,
        )
        msg = self._make_msg(delivery_tag=20)
        await consumer.on_queue_message(msg=msg)
        handler_mock.assert_awaited_once_with(consumer.bucket._items)

        self.queue_mock.ack.assert_awaited_once_with(
            delivery_tag=msg.delivery_tag
        )
        self.assertEqual(0, self.queue_mock.reject.call_count)

    async def test_on_queue_message_bulk_size_bigger_that_one(self):
        """
        Confere que o handler real só é chamado quando o bucket atinge o limite máximo de
        tamanho. E que o handler é chamado com a lista de mensagens.
        * Bucket deve estart vazio após o "flush"
        """

        class MyBucket(Bucket):
            def pop_all(self):
                return self._items

        handler_mock = CoroutineMock()
        self.one_route_fixture["handler"] = handler_mock
        self.one_route_fixture["options"]["bulk_size"] = 2

        consumer = Consumer(
            self.one_route_fixture,
            *self.connection_parameters,
            bucket_class=MyBucket,
        )
        msgs = [
            self._make_msg(delivery_tag=10),
            self._make_msg(delivery_tag=20),
        ]
        await consumer.on_queue_message(msg=msgs[0])
        handler_mock.assert_not_awaited()

        await consumer.on_queue_message(msg=msgs[1])
        handler_mock.assert_awaited_once_with(consumer.bucket._items)

        self.queue_mock.ack.assert_has_awaits(
            [
                mock.call(delivery_tag=msgs[0].delivery_tag),
                mock.call(delivery_tag=msgs[1].delivery_tag),
            ],
            any_order=True,
        )

        self.queue_mock.reject.assert_not_awaited()

    async def test_on_queue_message_bulk_mixed_ack_and_reject(self):
        async def handler(messages):
            messages[1].reject()
            messages[2].reject()

        self.one_route_fixture["handler"] = handler
        self.one_route_fixture["options"]["bulk_size"] = 5

        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)

        msgs = [self._make_msg(delivery_tag=i) for i in range(5)]
        for msg in msgs:
            await consumer.on_queue_message(msg)

        await consumer.on_queue_message(self._make_msg(delivery_tag=10))
        await consumer.on_queue_message(self._make_msg(delivery_tag=11))
        await consumer.on_queue_message(self._make_msg(delivery_tag=12))
        await consumer.on_queue_message(self._make_msg(delivery_tag=13))
        await consumer.on_queue_message(self._make_msg(delivery_tag=14))

        self.queue_mock.ack.assert_has_awaits(
            [
                mock.call(delivery_tag=msgs[0].delivery_tag),
                mock.call(delivery_tag=msgs[3].delivery_tag),
                mock.call(delivery_tag=msgs[4].delivery_tag),
            ],
            any_order=True,
        )
        self.queue_mock.reject.assert_has_awaits(
            [
                mock.call(delivery_tag=msgs[1].delivery_tag, requeue=True),
                mock.call(delivery_tag=msgs[2].delivery_tag, requeue=True),
            ],
            any_order=True,
        )

    async def test_on_queue_message_bulk_mixed_ack_and_reject_on_success_reject(
        self
    ):
        self.maxDiff = None

        async def handler(messages):
            messages[1].reject(requeue=True)
            messages[2].reject(requeue=True)

        self.one_route_fixture["handler"] = handler
        self.one_route_fixture["options"]["bulk_size"] = 5
        self.one_route_fixture["options"][Events.ON_SUCCESS] = Actions.REJECT

        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)

        msgs = [self._make_msg(delivery_tag=i) for i in range(5)]
        for msg in msgs:
            await consumer.on_queue_message(msg)

        self.queue_mock.reject.assert_has_awaits(
            [
                mock.call(delivery_tag=msgs[0].delivery_tag, requeue=False),
                mock.call(delivery_tag=msgs[1].delivery_tag, requeue=True),
                mock.call(delivery_tag=msgs[2].delivery_tag, requeue=True),
                mock.call(delivery_tag=msgs[3].delivery_tag, requeue=False),
                mock.call(delivery_tag=msgs[4].delivery_tag, requeue=False),
            ],
            any_order=True,
        )

    async def test_bulk_flushes_on_timeout_even_with_bucket_not_full(self):
        class MyBucket(Bucket):
            def pop_all(self):
                global items
                items = self._items
                self._items = []
                return items

        handler_mock = CoroutineMock()
        self.one_route_fixture["handler"] = handler_mock
        self.one_route_fixture["options"]["bulk_size"] = 3

        consumer = Consumer(
            self.one_route_fixture,
            *self.connection_parameters,
            bucket_class=MyBucket,
        )
        queue_mock = CoroutineMock(ack=CoroutineMock())

        msgs = [
            self._make_msg(delivery_tag=10),
            self._make_msg(delivery_tag=11),
        ]
        await consumer.on_queue_message(msgs[0])
        handler_mock.assert_not_awaited()

        await consumer.on_queue_message(msgs[1])
        handler_mock.assert_not_awaited()


        await asyncio.sleep(4)

        self.loop.create_task(consumer._flush_clocked(queue_mock))
        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertEqual(1, handler_mock.await_count)
        handler_mock.assert_awaited_once_with(items)

        self.assertCountEqual(
            [mock.call(delivery_tag=10), mock.call(delivery_tag=20)],
            queue_mock.ack.await_args_list,
        )
        queue_mock.reject.assert_not_called()

    async def test_do_not_flush_if_bucket_is_already_empty_when_timeout_expires(
        self
    ):
        class MyBucket(Bucket):
            def pop_all(self):
                global items
                items = self._items
                self._items = []
                return items

        handler_mock = CoroutineMock()
        self.one_route_fixture["handler"] = handler_mock
        self.one_route_fixture["options"]["bulk_size"] = 3

        consumer = Consumer(
            self.one_route_fixture,
            *self.connection_parameters,
            bucket_class=MyBucket,
        )
        queue_mock = CoroutineMock(ack=CoroutineMock())

        self.loop.create_task(consumer._flush_clocked(queue_mock))
        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertEqual(0, handler_mock.await_count)

    async def test_clock_flush_dont_stop_on_exception_in_flush_clocked(self):
        class MyBucket(Bucket):
            def pop_all(self):
                global items
                items = self._items
                self._items = []
                return items

        async def handler(*args):
            raise Exception()

        self.one_route_fixture["handler"] = handler
        self.one_route_fixture["options"]["bulk_size"] = 3

        consumer = Consumer(
            self.one_route_fixture,
            *self.connection_parameters,
            bucket_class=MyBucket,
        )
        queue_mock = mock.Mock(reject=CoroutineMock())
        await consumer.on_queue_message({}, 10, queue_mock)
        self.loop.create_task(consumer._flush_clocked(queue_mock))

        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertEqual(1, consumer.clock.current_iteration)
        await consumer.on_queue_message({}, 10, queue_mock)

        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertEqual(2, consumer.clock.current_iteration)
        await consumer.clock.stop()
        await asyncio.sleep(0.1)

    async def test_on_message_handle_error_logs_exception(self):
        """
        Logamos a exception lançada pelo handler.
        Aqui o try/except serve apenas para termos uma exception real, com traceback.
        """
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with mock.patch.object(conf, "logger", self.logger_mock):
            try:
                1 / 0
            except Exception as e:
                await consumer.on_message_handle_error(e)
                self.logger_mock.error.assert_awaited_with(
                    {
                        "exc_message": "division by zero",
                        "exc_traceback": mock.ANY,
                    }
                )

    async def test_on_connection_error_logs_exception(self):
        """
        Logamos qualquer erro de conexão com o Rabbit, inclusive acesso negado
        """
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with mock.patch.object(conf, "logger", self.logger_mock):
            try:
                1 / 0
            except Exception as e:
                await consumer.on_connection_error(e)
                self.logger_mock.error.assert_awaited_with(
                    {
                        "exc_message": "division by zero",
                        "exc_traceback": mock.ANY,
                    }
                )

    async def test_on_queue_error_logs_exception_and_acks_message(self):
        """
        Logamos qualquer erro de parsing/validação de mensagem
        """
        delivery_tag = 42
        body = "not a JSON"
        queue_mock = CoroutineMock(ack=CoroutineMock())

        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with mock.patch.object(conf, "logger", self.logger_mock):
            await consumer.on_queue_error(
                body, delivery_tag, "Error: not a JSON", queue_mock
            )
            self.logger_mock.error.assert_awaited_with(
                {
                    "exception": "Error: not a JSON",
                    "original_msg": body,
                    "parse-error": True,
                }
            )
            queue_mock.ack.assert_awaited_once_with(delivery_tag=delivery_tag)

    def test_return_correct_queue_name(self):
        """
        consumer.quene_name deve retornar o nome da fila que está sendo consumida.
        """
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        self.assertEqual(self.one_route_fixture["routes"], consumer.queue_name)

    async def test_consume_all_queues(self):
        """
        """
        self.one_route_fixture["routes"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(consume=CoroutineMock())
        await consumer.consume_all_queues(queue_mock)

        queue_mock.consume.assert_has_awaits(
            [
                mock.call(queue_name="asgard/counts"),
                mock.call(queue_name="asgard/counts/errors"),
            ],
            any_order=True,
        )

    async def test_start_calls_connect_and_consume_for_each_queue(self):
        self.one_route_fixture["routes"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(
            consume=CoroutineMock(),
            connection=Mock(connect=CoroutineMock(), is_connected=False),
        )
        consumer.queue = queue_mock

        with asynctest.patch.object(
            consumer, "keep_runnig", side_effect=[True, False]
        ) as keep_running_mock, asynctest.patch.object(
            consumer, "clock_task", side_effect=[True, True]
        ), mock.patch.object(
            asyncio, "sleep"
        ):
            await consumer.start()

        self.assertEqual(1, queue_mock.connection.connect.await_count)
        self.assertEqual(2, queue_mock.consume.await_count)
        self.assertEqual(
            [
                mock.call(queue_name="asgard/counts"),
                mock.call(queue_name="asgard/counts/errors"),
            ],
            queue_mock.consume.await_args_list,
        )

    async def test_start_reconnects_if_connection_failed_bla(self):
        self.one_route_fixture["routes"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with unittest.mock.patch.object(
            consumer, "keep_runnig", side_effect=[True, True, False]
        ), asynctest.patch.object(asyncio, "sleep"), asynctest.patch.object(
            consumer, "clock_task", side_effect=[True, True]
        ):
            is_connected_mock = mock.PropertyMock(
                side_effect=[False, False, True]
            )
            queue_mock = CoroutineMock(
                consume=CoroutineMock(),
                connection=Mock(
                    connect=CoroutineMock(side_effect=[AioamqpException, True])
                ),
            )
            type(queue_mock.connection).is_connected = is_connected_mock
            consumer.queue = queue_mock

            await consumer.start()
            self.assertEqual(1, queue_mock.connection.connect.await_count)
            self.assertEqual(2, queue_mock.consume.await_count)
            self.assertEqual(
                [
                    mock.call(queue_name="asgard/counts"),
                    mock.call(queue_name="asgard/counts/errors"),
                ],
                queue_mock.consume.await_args_list,
            )

    async def test_start_always_calls_sleep(self):
        """
        Regression:
            O sleep deve ser chamado *sempre*, e não apenas quando há tentativa de conexão.
            Aqui, tentamos reconectar apenas uma vez, mas mesmo assim o sleep é chamado 3x, pois o loop principal
            roda 3x.
        """
        self.one_route_fixture["route"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with unittest.mock.patch.object(
            consumer, "keep_runnig", side_effect=[True, True, True, False]
        ), asynctest.patch.object(
            asyncio, "sleep"
        ) as sleep_mock, asynctest.patch.object(
            consumer, "clock_task", side_effect=[True, True]
        ):
            is_connected_mock = mock.PropertyMock(
                side_effect=[False, True, True, True]
            )
            queue_mock = CoroutineMock(
                consume=CoroutineMock(), connect=CoroutineMock()
            )
            type(queue_mock).is_connected = is_connected_mock
            consumer.queue = queue_mock

            await consumer.start()
            self.assertEqual(3, sleep_mock.await_count)

    async def test_start_dont_created_clock_when_connection_failed(self):
        self.one_route_fixture["routes"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with unittest.mock.patch.object(
            consumer, "keep_runnig", side_effect=[True, True, True, False]
        ):
            is_connected_mock = mock.PropertyMock(
                side_effect=[True, False, True]
            )
            queue_mock = CoroutineMock(
                consume=CoroutineMock(),
                connect=CoroutineMock(side_effect=[AioamqpException, True]),
            )
            type(queue_mock).is_connected = is_connected_mock
            consumer.queue = queue_mock

            await consumer.start()
        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertIsNone(consumer.clock_task)
        await consumer.clock.stop()
        await asyncio.sleep(0.1)

    async def test_start_create_clock_flusher(self):
        self.one_route_fixture["routes"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        with unittest.mock.patch.object(
            consumer, "keep_runnig", side_effect=[True, True, True, False]
        ):
            is_connected_mock = mock.PropertyMock(
                side_effect=[True, False, False]
            )
            queue_mock = CoroutineMock(
                consume=CoroutineMock(),
                connect=CoroutineMock(side_effect=[AioamqpException, True]),
            )
            type(queue_mock).is_connected = is_connected_mock
            consumer.queue = queue_mock

            await consumer.start()
        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertIsNotNone(consumer.clock_task)
        await consumer.clock.stop()
        await asyncio.sleep(0.1)

    async def test_start_dont_created_another_clock_when_restart(self):
        self.one_route_fixture["routes"] = [
            "asgard/counts",
            "asgard/counts/errors",
        ]
        consumer = Consumer(self.one_route_fixture, *self.connection_parameters)
        queue_mock = CoroutineMock(
            consume=CoroutineMock(),
            connect=CoroutineMock(side_effect=[True, True]),
        )

        with unittest.mock.patch.object(
            consumer, "keep_runnig", side_effect=[True, False, True, False]
        ):
            is_connected_mock = mock.PropertyMock(side_effect=[False, False])
            type(queue_mock).is_connected = is_connected_mock
            consumer.queue = queue_mock

            await consumer.start()
            my_task = consumer.clock_task

            await consumer.start()

        # Realizando sleep para devolver o loop para o clock
        await asyncio.sleep(0.1)
        self.assertTrue(my_task is consumer.clock_task)
        await consumer.clock.stop()
        await asyncio.sleep(0.1)
