import unittest

from asynctest import CoroutineMock

from asyncworker import RouteTypes
from asyncworker.routes import RoutesRegistry


class RoutesRegistryTests(unittest.TestCase):
    def setUp(self):
        self.routes_registry = RoutesRegistry()

    def test_it_registers_routes(self):
        handler = CoroutineMock()

        route_data = {
            "type": RouteTypes.HTTP,
            "routes": ["/"],
            "methods": ["POST"],
            "handler": handler,
            "default_options": {},
        }

        new_route = self.routes_registry.add_route(route_data)

        self.assertEqual(new_route, self.routes_registry.route_for(handler))

    def test_route_for(self):
        handler = CoroutineMock()

        route_data = {
            "type": RouteTypes.HTTP,
            "routes": ["/"],
            "methods": ["POST"],
            "handler": handler,
            "default_options": {},
        }

        self.routes_registry[handler] = route_data

        self.assertEqual(self.routes_registry.route_for(handler), route_data)

    def test_it_raise_an_error_if_the_route_has_an_invalid_type(self):
        routes_registry = RoutesRegistry()

        handler = CoroutineMock()
        route_data = {
            "type": "Xablau",
            "routes": ["/"],
            "methods": ["POST"],
            "handler": handler,
            "default_options": {},
        }

        with self.assertRaises(ValueError):
            routes_registry[handler] = route_data

    def test_it_raises_an_error_if_route_dict_dosnt_have_a_type(self):
        handler = CoroutineMock()
        route_data = {
            "routes": ["/"],
            "methods": ["POST"],
            "handler": handler,
            "default_options": {},
        }

        with self.assertRaises(ValueError):
            self.routes_registry[handler] = route_data

    def test_routes_are_subscriptables(self):
        handler = CoroutineMock()
        route_data = {
            "type": RouteTypes.HTTP,
            "routes": ["/"],
            "methods": ["POST"],
            "handler": handler,
            "default_options": {},
        }

        new_route = self.routes_registry.add_route(route_data)

        self.assertEqual(new_route["type"], RouteTypes.HTTP)
        with self.assertRaises(KeyError):
            _ = new_route["Invalid key"]

    def test_routes_get_method(self):
        handler = CoroutineMock()
        route_data = {
            "type": RouteTypes.HTTP,
            "routes": ["/"],
            "methods": ["POST"],
            "handler": handler,
            "default_options": {},
        }

        new_route = self.routes_registry.add_route(route_data)

        self.assertEqual(new_route.get("type"), RouteTypes.HTTP)
        self.assertEqual(new_route.get("Invalid key", "Default"), "Default")
