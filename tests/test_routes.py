import unittest

from aiohttp import web
from asynctest import CoroutineMock, TestCase

from asyncworker import RouteTypes, App
from asyncworker.exceptions import InvalidRoute
from asyncworker.routes import RoutesRegistry, HTTPRoute, AMQPRoute
from asyncworker.testing import HttpClientContext


class RoutesRegistryTests(unittest.TestCase):
    def setUp(self):
        self.routes_registry = RoutesRegistry()

    def test_it_registers_routes(self):
        handler = CoroutineMock()

        route = HTTPRoute(
            routes=["/"], methods=["POST"], handler=handler, default_options={}
        )

        self.routes_registry.add_route(route)

        self.assertEqual(route, self.routes_registry.route_for(handler))

    def test_route_for(self):
        handler = CoroutineMock()

        route = HTTPRoute(
            routes=["/"], methods=["POST"], handler=handler, default_options={}
        )

        self.routes_registry[handler] = route

        self.assertEqual(self.routes_registry.route_for(handler), route)

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
        route = HTTPRoute(
            routes=["/"], methods=["POST"], handler=handler, default_options={}
        )

        self.routes_registry.add_route(route)

        self.assertEqual(route["type"], RouteTypes.HTTP)
        with self.assertRaises(KeyError):
            _ = route["Invalid key"]

    def test_routes_get_method(self):
        handler = CoroutineMock()
        route = HTTPRoute(
            routes=["/"], methods=["POST"], handler=handler, default_options={}
        )

        self.routes_registry.add_route(route)

        self.assertEqual(route.get("type"), RouteTypes.HTTP)
        self.assertEqual(route.get("Invalid key", "Default"), "Default")


class HTTPRoutesTests(unittest.TestCase):
    def test_it_raise_an_error_for_invalid_methods(self):
        with self.assertRaises(ValueError):
            HTTPRoute(
                methods=["POST", "Xablau"],
                handler=CoroutineMock(),
                routes=["/"],
            )

    def test_valid_http_methods(self):
        route = HTTPRoute(
            methods=[
                "POST",
                "GET",
                "DELeTE",
                "PUT",
                "head",
                "options",
                "patch",
                "TRACE",
                "connect",
            ],
            handler=CoroutineMock(),
            routes=["/"],
        )
        self.assertIsInstance(route, HTTPRoute)


class AMQPRouteTests(TestCase):
    async def test_it_raises_an_error_if_route_connection_is_invalid(self):
        with self.assertRaises(ValueError):
            AMQPRoute(
                routes=["Xablau", "Xena"],
                handler=lambda *args, **kwargs: 42,
                options={"connection": (..., ..., ...)},
            )

    async def test_can_registrer_a_callable_as_a_valid_handler(self):
        app = App()

        class MyHandler:
            async def __call__(self, req: web.Request):
                return web.json_response({"OK": True})

        handler = MyHandler()

        app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])(handler)

        async with HttpClientContext(app) as client:
            resp = await client.get("/")
            data = await resp.json()
            self.assertEqual({"OK": True}, data)

    async def test_raise_if_object_is_not_callable(self):
        app = App()

        class MyHandler:
            pass

        handler = MyHandler()

        with self.assertRaises(TypeError):
            app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])(handler)
