from asynctest import TestCase, mock, CoroutineMock

from asyncworker import App, RouteTypes
from asyncworker.connections import AMQPConnection
from asyncworker.metrics.definitions.amqp import active_consumers


class AMQPExposedMetricsTest(TestCase):
    async def setUp(self):
        conn = AMQPConnection(
            hostname="127.0.0.1", username="guest", password="guest"
        )
        self.app = App(connections=[conn])

        active_consumers._metric_init()

    async def tearDown(self):
        await self.app.shutdown()

    async def test_consumer_count_1_consumer_1_route(self):
        @self.app.route(["queue-1"], RouteTypes.AMQP_RABBITMQ)
        async def _h(msgs):
            pass

        with mock.patch("asyncworker.consumer.Consumer.start", CoroutineMock()):
            samples = active_consumers.collect()[0].samples
            self.assertEqual(1, len(samples))
            self.assertEqual(0.0, samples[0].value)

            await self.app.startup()

            samples_after = active_consumers.collect()[0].samples
            self.assertEqual(1, len(samples_after))
            self.assertEqual(1.0, samples_after[0].value)

    async def test_active_consumers_1_consumer_2_route_paths(self):
        """
        Atualmente ligamos um consumer por @app.route(). Um mesmo consumer consegue
        ler de múltiplas filas (em um mesmo broker)
        """

        @self.app.route(["queue-1", "queue-2"], RouteTypes.AMQP_RABBITMQ)
        async def _h(msgs):
            pass

        with mock.patch("asyncworker.consumer.Consumer.start", CoroutineMock()):
            samples = active_consumers.collect()[0].samples
            self.assertEqual(1, len(samples))
            self.assertEqual(0.0, samples[0].value)

            await self.app.startup()

            samples_after = active_consumers.collect()[0].samples
            self.assertEqual(1, len(samples_after))
            self.assertEqual(1.0, samples_after[0].value)

    async def test_active_consumers_2_consumer_multiple_route_paths(self):
        """
        Atualmente ligamos um consumer por @app.route(). Um mesmo consumer consegue
        ler de múltiplas filas (em um mesmo broker)
        """

        @self.app.route(["queue-1", "queue-2"], RouteTypes.AMQP_RABBITMQ)
        async def _h_1(msgs):
            pass

        @self.app.route(["queue-3", "queue-4"], RouteTypes.AMQP_RABBITMQ)
        async def _h_2(msgs):
            pass

        with mock.patch("asyncworker.consumer.Consumer.start", CoroutineMock()):
            samples = active_consumers.collect()[0].samples
            self.assertEqual(1, len(samples))
            self.assertEqual(0.0, samples[0].value)

            await self.app.startup()

            samples_after = active_consumers.collect()[0].samples
            self.assertEqual(1, len(samples_after))
            self.assertEqual(2.0, samples_after[0].value)
