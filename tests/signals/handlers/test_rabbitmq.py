import asynctest
from asynctest import CoroutineMock, Mock, call
from asyncworker.signals.handlers.rabbitmq import RabbitMQ
from asyncworker.routes import RoutesRegistry
from asyncworker.options import RouteTypes


class AMQPTests(asynctest.TestCase):
    async def setUp(self):
        self.signal_handler = RabbitMQ()

        handler1 = Mock(return_value=CoroutineMock())
        handler2 = Mock(return_value=CoroutineMock())

        self.routes_registry = RoutesRegistry(
            {
                handler1: {
                    "type": RouteTypes.AMQP_RABBITMQ,
                    "routes": ["Xablau"],
                    "options": {},
                },
                handler2: {
                    "type": RouteTypes.AMQP_RABBITMQ,
                    "routes": ["Xena"],
                    "options": {},
                },
            }
        )

    @asynctest.patch("asyncworker.signals.handlers.rabbitmq.Consumer")
    async def test_startup_initializes_and_starts_one_consumer_per_route(
        self, Consumer
    ):
        app = asynctest.MagicMock(
            routes_registry=self.routes_registry,
            loop=Mock(create_task=CoroutineMock()),
            prefetch_count=1,
        )
        await self.signal_handler.startup(app)

        Consumer.assert_has_calls(
            [
                call(
                    self.routes_registry.amqp_routes[0],
                    app.host,
                    app.user,
                    app.password,
                    app.prefetch_count,
                ),
                call(
                    self.routes_registry.amqp_routes[1],
                    app.host,
                    app.user,
                    app.password,
                    app.prefetch_count,
                ),
            ],
            any_order=True,
        )
        Consumer.return_value.start.assert_has_calls([call(), call()])
        app.__getitem__.return_value.append.assert_has_calls(
            [call(Consumer.return_value), call(Consumer.return_value)]
        )
