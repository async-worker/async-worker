import asynctest
from asynctest import CoroutineMock, Mock, call, MagicMock
from asyncworker.signals.handlers.sse import SSE
from asyncworker.routes import RoutesRegistry
from asyncworker.options import RouteTypes
from asyncworker.sse.connection import SSEConnection


class AMQPTests(asynctest.TestCase):
    async def setUp(self):
        self.signal_handler = SSE()

        handler1 = Mock(return_value=CoroutineMock())
        handler2 = Mock(return_value=CoroutineMock())
        handler3 = Mock(return_value=CoroutineMock())

        self.routes_registry = RoutesRegistry(
            {
                handler1: {
                    "type": RouteTypes.SSE,
                    "routes": ["Xablau"],
                    "options": {},
                    "default_options": {},
                },
                handler2: {
                    "type": RouteTypes.SSE,
                    "routes": ["Xena", "sse"],
                    "options": MagicMock(),
                    "default_options": {},
                },
                handler3: {
                    "type": RouteTypes.AMQP_RABBITMQ,
                    "routes": ["invalid route"],
                    "options": MagicMock(),
                    "default_options": {},
                },
            }
        )

    @asynctest.patch("asyncworker.signals.handlers.sse.SSEConsumer")
    async def test_startup_initializes_and_starts_one_consumer_per_route(
        self, Consumer
    ):
        conn = SSEConnection(url="https://www.sieve.com.br/cultura/")
        app = asynctest.MagicMock(
            routes_registry=self.routes_registry,
            loop=Mock(create_task=CoroutineMock()),
            get_connection_for_route=Mock(return_value=conn),
        )
        await self.signal_handler.startup(app)

        Consumer.assert_has_calls(
            [
                call(
                    route_info=self.routes_registry.sse_routes[0],
                    url="https://www.sieve.com.br/cultura/Xablau",
                    username=conn.user,
                    password=conn.password,
                ),
                call(
                    route_info=self.routes_registry.sse_routes[1],
                    url="https://www.sieve.com.br/cultura/Xena",
                    username=conn.user,
                    password=conn.password,
                ),
                call(
                    route_info=self.routes_registry.sse_routes[1],
                    url="https://www.sieve.com.br/cultura/sse",
                    username=conn.user,
                    password=conn.password,
                ),
            ],
            any_order=True,
        )
        Consumer.return_value.start.assert_has_calls([call(), call()])
        app[RouteTypes.SSE].__getitem__.return_value.append.assert_has_calls(
            [call(Consumer.return_value), call(Consumer.return_value)]
        )
