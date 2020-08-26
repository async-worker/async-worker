from aiohttp import web
from asynctest import CoroutineMock, TestCase

from asyncworker import RouteTypes, App
from asyncworker.http.wrapper import RequestWrapper
from asyncworker.options import Actions
from asyncworker.routes import (
    call_http_handler,
    RoutesRegistry,
    HTTPRoute,
    AMQPRoute,
    _AMQPRouteOptions,
)
from asyncworker.testing import HttpClientContext


class RoutesRegistryTests(TestCase):
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

    def test_register_http_handler(self):
        route = HTTPRoute(
            handler=CoroutineMock(), routes=["/foo"], methods=["GET"]
        )
        self.routes_registry.add_http_route(route)

        self.assertEqual(len(self.routes_registry.http_routes), 1)
        self.assertEqual(self.routes_registry.http_routes[0], route)

    def test_register_amqp_handler(self):
        route = AMQPRoute(
            handler=CoroutineMock(),
            routes=["queue1", "queue2"],
            options=_AMQPRouteOptions(),
        )

        self.routes_registry.add_amqp_route(route)

        self.assertEqual(len(self.routes_registry.amqp_routes), 1)
        self.assertEqual(self.routes_registry.amqp_routes[0], route)


class HTTPRouteModelTests(TestCase):
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


class HTTPRouteRegisterTest(TestCase):
    async def test_can_registrer_a_callable_as_a_valid_handler(self):
        app = App()

        class MyHandler:
            async def __call__(self, wrapper: RequestWrapper):
                return web.json_response({"OK": True})

        handler = MyHandler()

        app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])(handler)

        async with HttpClientContext(app) as client:
            resp = await client.get("/")
            data = await resp.json()
            self.assertEqual({"OK": True}, data)

    async def test_can_registrer_a_callable_as_a_valid_handler_new_decorator(
        self
    ):
        app = App()

        class MyHandler:
            async def __call__(self, wrapper: RequestWrapper):
                return web.json_response({"OK": True})

        handler = MyHandler()
        app.http.get(["/"])(handler)

        async with HttpClientContext(app) as client:
            resp = await client.get("/")
            data = await resp.json()
            self.assertEqual({"OK": True}, data)

    async def test_can_registrer_a_coroutine_as_a_valid_handler_new_decorator(
        self
    ):
        app = App()

        @app.http.get(["/"])
        async def handler(wrapper: RequestWrapper):
            return web.json_response({"OK": True})

        async with HttpClientContext(app) as client:
            resp = await client.get("/")
            data = await resp.json()
            self.assertEqual({"OK": True}, data)

    async def test_raise_if_handler_is_not_coroutine(self):
        app = App()

        with self.assertRaises(TypeError) as err:

            @app.http.get(["/"])
            def handler(wrapper: RequestWrapper):
                return web.json_response({"OK": True})

        self.assertTrue("handler must be async" in err.exception.args[0])

    async def test_raise_if_object_is_not_callable(self):
        app = App()

        class MyHandler:
            pass

        handler = MyHandler()

        with self.assertRaises(TypeError):
            app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])(handler)

    async def test_raise_if_object_is_not_callable_new_decorator(self):
        app = App()

        class MyHandler:
            pass

        handler = MyHandler()

        with self.assertRaises(TypeError):
            app.http.get(["/"])(handler)

    async def test_handler_receives_request_object(self):
        """
        Certifica que um decorator customizado pode receber
        uma instânccia de aiohttp.web.Request
        """
        app = App()

        def _deco(handler):
            async def _wrap(req: web.Request):
                return await call_http_handler(req, handler)

            return _wrap

        @app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        @_deco
        async def handler(wrapper: RequestWrapper):
            req = wrapper.http_request
            return web.json_response(dict(req.query.items()))

        async with HttpClientContext(app) as client:
            resp = await client.get("/?a=10&b=20")
            data = await resp.json()
            self.assertEqual({"a": "10", "b": "20"}, data)

    async def test_custom_decorator_receives_request_wrapper(self):
        """
        Certifica que um decorator customizado pode receber
        uma instância de asyncworker.http.wrapper.RequestWrapper
        """
        app = App()

        def _deco(handler):
            async def _wrap(req: RequestWrapper):
                return await call_http_handler(req.http_request, handler)

            return _wrap

        @app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        @_deco
        async def handler(wrap: RequestWrapper):
            return web.json_response(dict(wrap.http_request.query.items()))

        async with HttpClientContext(app) as client:
            resp = await client.get("/?a=30&b=42")
            data = await resp.json()
            self.assertEqual({"a": "30", "b": "42"}, data)


class AMQPRouteModelTests(TestCase):
    async def test_it_raises_an_error_if_route_connection_is_invalid(self):
        with self.assertRaises(ValueError):
            AMQPRoute(
                routes=["Xablau", "Xena"],
                handler=lambda *args, **kwargs: 42,
                options={"connection": (..., ..., ...)},
            )


class AMQPRouteRegiterTest(TestCase):
    async def test_can_registrer_a_callable_as_a_valid_handler(self):
        app = App()

        class MyHandler:
            async def __call__(self):
                pass

        handler = MyHandler()

        app.route(["/"], type=RouteTypes.AMQP_RABBITMQ)(handler)

        self.assertEqual(1, len(app.routes_registry.amqp_routes))
        self.assertEqual(
            handler.__call__, app.routes_registry.amqp_routes[0].handler
        )

    async def test_can_registrer_a_callable_as_a_valid_handler_amqp_route_register(
        self
    ):
        app = App()

        class MyHandler:
            async def __call__(self):
                pass

        handler = MyHandler()

        app.amqp.consume(["/"])(handler)

        self.assertEqual(1, len(app.routes_registry.amqp_routes))
        self.assertEqual(
            handler.__call__, app.routes_registry.amqp_routes[0].handler
        )

    async def test_raise_if_object_is_not_callable_register_with_app_route(
        self
    ):
        app = App()

        class MyHandler:
            pass

        handler = MyHandler()

        with self.assertRaises(TypeError):
            app.route(["/"], type=RouteTypes.AMQP_RABBITMQ)(handler)

    async def test_raise_if_object_is_not_callable_register_with_amqp_route_register(
        self
    ):
        app = App()

        class MyHandler:
            pass

        handler = MyHandler()

        with self.assertRaises(TypeError):
            app.amqp.consume(["my-queue"])(handler)

    async def test_raise_if_handler_is_sync(self):
        app = App()

        with self.assertRaises(TypeError) as err:

            @app.amqp.consume(["/"])
            def handler():
                pass

        self.assertTrue("handler must be async" in err.exception.args[0])

    async def test_can_register_async_handler(self):
        app = App()

        @app.amqp.consume(["/"])
        async def handler():
            pass

        self.assertEqual(1, len(app.routes_registry.amqp_routes))
        self.assertEqual(handler, app.routes_registry.amqp_routes[0].handler)

    async def test_register_handler_with_options(self):
        app = App()

        options = _AMQPRouteOptions(
            bulk_size=1024,
            bulk_flush_intereval=10,
            on_success=Actions.ACK,
            on_exception=Actions.REJECT,
        )

        @app.amqp.consume(["/"], options=options)
        async def handler():
            pass

        self.assertEqual(1, len(app.routes_registry.amqp_routes))
        self.assertEqual(handler, app.routes_registry.amqp_routes[0].handler)
        self.assertEqual(options, app.routes_registry.amqp_routes[0].options)

    async def test_raises_if_handler_is_not_coroutine(self):
        """
        Certifica que um decorator customizado pode receber
        uma instânccia de aiohttp.web.Request
        """
        app = App()

        def handler(wrapper: RequestWrapper):
            req = wrapper.http_request
            return web.json_response(dict(req.query.items()))

        with self.assertRaises(TypeError) as ex:
            app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])(handler)

        self.assertTrue("handler must be a coroutine" in ex.exception.args[0])
