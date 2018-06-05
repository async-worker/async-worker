import unittest
import asyncio

from worker import App

class AppTest(unittest.TestCase):

    def test_register_hander_on_route_registry(self):
        expected_route = ["/asgard/counts/ok"]
        expected_vhost = "/"
        app = App()
        @app.route(expected_route, vhost=expected_vhost)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_registry_entry = {
            "route": expected_route[0],
            "handler": _handler,
            "options": {
                "vhost": expected_vhost
            }
        }
        self.assertEqual(expected_registry_entry, app.routes_registry['/asgard/counts/ok'])
        self.assertEqual(42, asyncio.get_event_loop().run_until_complete(_handler(None)))

    def test_register_list_of_routes_to_the_same_handler(self):
        expected_routes = ["/asgard/counts/ok", "/asgard/counts/errors"]
        expected_vhost = "/"
        app = App()
        @app.route(expected_routes, vhost=expected_vhost)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        expected_ok_registry_entry = {
            "route": expected_routes[0],
            "handler": _handler,
            "options": {
                "vhost": expected_vhost
            }
        }

        expected_errors_registry_entry = {
            "route": expected_routes[1],
            "handler": _handler,
            "options": {
                "vhost": expected_vhost
            }
        }
        self.assertEqual(expected_ok_registry_entry, app.routes_registry['/asgard/counts/ok'])
        self.assertEqual(expected_errors_registry_entry, app.routes_registry['/asgard/counts/errors'])
        self.assertEqual(42, asyncio.get_event_loop().run_until_complete(_handler(None)))
