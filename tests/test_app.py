import unittest
import asyncio

from worker import App

class AppTest(unittest.TestCase):

    def setUp(self):
        self.connection_parameters = {"host": "127.0.0.1", "user": "guest", "password": "guest", "prefetch_count": 1024}

    def test_register_hander_on_route_registry(self):
        expected_route = ["/asgard/counts/ok"]
        expected_vhost = "/"
        app = App(**self.connection_parameters)
        @app.route(expected_route, vhost=expected_vhost)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_registry_entry = {
            "route": expected_route,
            "handler": _handler,
            "options": {
                "vhost": expected_vhost
            }
        }
        self.assertEqual(expected_registry_entry, app.routes_registry[_handler])
        self.assertEqual(42, asyncio.get_event_loop().run_until_complete(_handler(None)))

    def test_register_list_of_routes_to_the_same_handler(self):
        expected_routes = ["/asgard/counts/ok", "/asgard/counts/errors"]
        expected_vhost = "/"
        app = App(**self.connection_parameters)
        @app.route(expected_routes, vhost=expected_vhost)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_registry_entry = {
            "route": expected_routes,
            "handler": _handler,
            "options": {
                "vhost": expected_vhost
            }
        }

        self.assertEqual(expected_registry_entry, app.routes_registry[_handler])
        self.assertEqual(42, asyncio.get_event_loop().run_until_complete(_handler(None)))

    def test_register_with_default_vhost(self):
        expected_route = ["/asgard/counts/ok"]
        expected_vhost = "/"
        app = App(**self.connection_parameters)
        @app.route(expected_route)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_registry_entry = {
            "route": expected_route,
            "handler": _handler,
            "options": {
                "vhost": expected_vhost
            }
        }
        self.assertEqual(expected_registry_entry, app.routes_registry[_handler])
        self.assertEqual(42, asyncio.get_event_loop().run_until_complete(_handler(None)))

    def test_app_receives_queue_connection(self):
        app = App(host="127.0.0.1", user="guest", password="guest", prefetch_count=1024)
        self.assertEqual("127.0.0.1", app.host)
        self.assertEqual("guest", app.user)
        self.assertEqual("guest", app.password)
        self.assertEqual(1024, app.prefetch_count)

    def test_instantiate_one_consumer_per_handler_one_handler_registered(self):
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

    def test_instantiate_one_consumer_per_handler_multiple_handlers_registered(self):
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

