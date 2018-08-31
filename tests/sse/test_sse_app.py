import unittest
import asyncio
import asynctest

from asyncworker.sse.app import SSEApplication
from asyncworker.options import Options, Defaultvalues, Events, Actions

from asynctest.mock import CoroutineMock

class AppTest(asynctest.TestCase):

    def setUp(self):
        self.default_headers = {"X-New-Header": "X-Value"}
        self.logger = CoroutineMock()
        self.connection_parameters = {"url": "http://127.0.0.1", "user": "guest", "password": "guest", "logger": self.logger, "headers": self.default_headers}

    async def test_check_route_registry_full_options(self):
        expected_route = ["/v2/events", "/other/path"]
        app = SSEApplication(**self.connection_parameters)
        @app.route(expected_route, options={Options.BULK_SIZE: 1024, Options.BULK_FLUSH_INTERVAL: 120})
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_registry_entry = {
            "routes": expected_route,
            "handler": _handler,
            "options": {
                "bulk_size": 1024,
                "bulk_flush_interval": 120,
                "headers": self.default_headers,
            }
        }
        self.assertEqual(expected_registry_entry, app.routes_registry[_handler])
        self.assertEqual(42, await app.routes_registry[_handler]['handler'](None))
        self.assertEqual(self.logger, app.logger)

    async def test_check_route_registry_add_headers_per_handler(self):
        expected_route = ["/v2/events", "/other/path"]
        aditional_headers = {"X-Other-Header": "X-Other-Value"}
        app = SSEApplication(**self.connection_parameters)
        @app.route(expected_route, headers=aditional_headers, options={Options.BULK_SIZE: 1024, Options.BULK_FLUSH_INTERVAL: 120})
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_registry_entry = {
            "routes": expected_route,
            "handler": _handler,
            "options": {
                "bulk_size": 1024,
                "bulk_flush_interval": 120,
                "headers": {
                    **self.default_headers,
                    **aditional_headers,
                },
            }
        }
        self.assertEqual(expected_registry_entry, app.routes_registry[_handler])
        self.assertEqual(42, await app.routes_registry[_handler]['handler'](None))

    async def test_register_hander_on_route_registry(self):
        expected_route = ["/asgard/counts/ok"]
        expected_vhost = "/"
        app = SSEApplication(**self.connection_parameters)
        @app.route(expected_route)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(_handler, app.routes_registry[_handler]['handler'])
        self.assertEqual(42, await app.routes_registry[_handler]['handler'](None))

    async def test_register_bulk_size(self):
        expected_bulk_size = 1024
        app = SSEApplication(**self.connection_parameters)
        @app.route(["my-queue"], options={Options.BULK_SIZE: expected_bulk_size})
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(expected_bulk_size, app.routes_registry[_handler]['options']['bulk_size'])
        self.assertEqual(42, await app.routes_registry[_handler]['handler'](None))


    async def test_register_bulk_flush_timeout(self):
        expected_bulk_flush_interval = 120
        app = SSEApplication(**self.connection_parameters)
        @app.route(["my-queue"], options={Options.BULK_FLUSH_INTERVAL: expected_bulk_flush_interval})
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(expected_bulk_flush_interval, app.routes_registry[_handler]['options']['bulk_flush_interval'])
        self.assertEqual(42, await app.routes_registry[_handler]['handler'](None))


    async def test_register_default_bulk_size_and_default_bulk_flush_timeout(self):
        app = SSEApplication(**self.connection_parameters)
        @app.route(["my-queue"])
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(Defaultvalues.BULK_SIZE, app.routes_registry[_handler]['options']['bulk_size'])
        self.assertEqual(Defaultvalues.BULK_FLUSH_INTERVAL, app.routes_registry[_handler]['options']['bulk_flush_interval'])
        self.assertEqual(42, await app.routes_registry[_handler]['handler'](None))

    @unittest.skip("Decidir se teremos ON_SUCCESS Event")
    async def test_register_action_on_success(self):
        app = SSEApplication(**self.connection_parameters)
        @app.route(["my-queue"], options = {Events.ON_SUCCESS: Actions.REJECT})
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(Actions.REJECT, app.routes_registry[_handler]['options'][Events.ON_SUCCESS])

    @unittest.skip("Decidir se teremos ON_EXCEPTION Event")
    async def test_register_action_on_exception(self):
        app = SSEApplication(**self.connection_parameters)
        @app.route(["my-queue"], options = {Events.ON_EXCEPTION: Actions.ACK})
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(Actions.ACK, app.routes_registry[_handler]['options'][Events.ON_EXCEPTION])

    @unittest.skip("Decidir se teremos ON_SUCCESS/ON_EXCEPTION Event")
    async def test_test_register_default_actions(self):
        app = SSEApplication(**self.connection_parameters)
        @app.route(["my-queue"])
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(Actions.ACK, app.routes_registry[_handler]['options'][Events.ON_SUCCESS])
        self.assertEqual(Actions.REQUEUE, app.routes_registry[_handler]['options'][Events.ON_EXCEPTION])

    async def test_app_receives_queue_connection(self):
        app = SSEApplication(url="http://127.0.0.1", user="guest", password="guest", headers={"A": "B"}, logger=None)
        self.assertEqual("http://127.0.0.1", app.url)
        self.assertEqual("guest", app.user)
        self.assertEqual("guest", app.password)
        self.assertEqual({"A": "B"}, app.headers)

    @unittest.skip("Ainda a ser implementado")
    async def test_instantiate_one_consumer_per_handler_one_handler_registered(self):
        """
        Para cada handler registrado, teremos um Consumer. Esse Consumer conseguirá consumir múltiplas
        filas, se necessário.
        """
        app = App(**self.connection_parameters)
        @app.route(["asgard/counts"], vhost="/")
        async def _handler(message):
            return message

        consumers = app._build_consumers()
        self.assertEqual(1, len(consumers))
        self.assertEqual(["asgard/counts"], consumers[0].queue_name)
        self.assertEqual("/", consumers[0].vhost)

        queue_connection_parameters = consumers[0].queue.connection_parameters
        self.assertEqual(self.connection_parameters['host'], queue_connection_parameters['host'])
        self.assertEqual(self.connection_parameters['user'], queue_connection_parameters['login'])
        self.assertEqual(self.connection_parameters['password'], queue_connection_parameters['password'])
        self.assertEqual(self.connection_parameters['prefetch_count'], consumers[0].queue.prefetch_count)

    @unittest.skip("Ainda a ser implementado")
    async def test_instantiate_one_consumer_per_handler_multiple_handlers_registered(self):
        app = App(**self.connection_parameters)

        @app.route(["asgard/counts"], vhost="/")
        async def _handler(message):
            return message

        @app.route(["asgard/counts/errors"], vhost="fluentd")
        async def _other_handler(message):
            return message

        consumers = app._build_consumers()
        self.assertEqual(2, len(consumers))

        self.assertEqual(["asgard/counts"], consumers[0].queue_name)
        self.assertEqual("/", consumers[0].vhost)
        queue_connection_parameters = consumers[0].queue.connection_parameters
        self.assertEqual(self.connection_parameters['host'], queue_connection_parameters['host'])
        self.assertEqual(self.connection_parameters['user'], queue_connection_parameters['login'])
        self.assertEqual(self.connection_parameters['password'], queue_connection_parameters['password'])
        self.assertEqual(self.connection_parameters['prefetch_count'], consumers[0].queue.prefetch_count)

        self.assertEqual(["asgard/counts/errors"], consumers[1].queue_name)
        self.assertEqual("fluentd", consumers[1].vhost)
        queue_connection_parameters = consumers[1].queue.connection_parameters
        self.assertEqual(self.connection_parameters['host'], queue_connection_parameters['host'])
        self.assertEqual(self.connection_parameters['user'], queue_connection_parameters['login'])
        self.assertEqual(self.connection_parameters['password'], queue_connection_parameters['password'])
        self.assertEqual(self.connection_parameters['prefetch_count'], consumers[1].queue.prefetch_count)

