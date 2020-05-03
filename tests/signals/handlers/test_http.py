from random import randint

import asynctest
from aiohttp import web
from asynctest import skip, mock, CoroutineMock, Mock, patch

from asyncworker import App
from asyncworker.conf import settings, Settings
from asyncworker.http.wrapper import RequestWrapper
from asyncworker.metrics.aiohttp_resources import metrics_route_handler
from asyncworker.routes import call_http_handler, RouteTypes, RoutesRegistry
from asyncworker.signals.handlers.http import HTTPServer
from asyncworker.testing import HttpClientContext
from asyncworker.types.registry import TypesRegistry


class HTTPServerTests(asynctest.TestCase):
    async def setUp(self):
        self.signal_handler = HTTPServer()

        handler1 = Mock(return_value=CoroutineMock())
        handler2 = Mock(return_value=CoroutineMock())

        self.routes_registry = RoutesRegistry(
            {
                handler1: {
                    "type": RouteTypes.HTTP,
                    "routes": ["/xablau"],
                    "methods": ["GET"],
                },
                handler2: {
                    "type": RouteTypes.HTTP,
                    "routes": ["/xena"],
                    "methods": ["GET", "POST"],
                },
            }
        )
        self.app = App(connections=[])

    @asynctest.patch("asyncworker.signals.handlers.http.web.TCPSite.start")
    async def test_startup_initializes_an_web_application(self, start):
        self.app.routes_registry = self.routes_registry

        await self.signal_handler.startup(self.app)

        self.assertIsInstance(self.app[RouteTypes.HTTP]["app"], web.Application)
        self.assertIsInstance(
            self.app[RouteTypes.HTTP]["runner"], web.AppRunner
        )
        site: web.TCPSite = self.app[RouteTypes.HTTP]["site"]
        self.assertIsInstance(site, web.TCPSite)

        self.assertEqual(site._port, settings.HTTP_PORT)
        self.assertEqual(site._host, settings.HTTP_HOST)

        start.assert_awaited_once()

    @asynctest.patch("asyncworker.signals.handlers.http.web.TCPSite.start")
    async def test_startup_exposes_metrics_http_route(self, start):
        with patch(
            "aiohttp.web_urldispatcher.UrlDispatcher.add_route"
        ) as add_route:
            await self.signal_handler.startup(self.app)

            add_route.assert_called_once_with(
                method="GET",
                path=settings.METRICS_HTTP_ROUTE_PATH,
                handler=metrics_route_handler,
            )

    @asynctest.patch("asyncworker.signals.handlers.http.web.AppRunner.cleanup")
    async def test_shutdown_closes_the_running_http_server(self, cleanup):
        with patch(
            "asyncworker.signals.handlers.http.settings",
            HTTP_PORT=randint(30000, 60000),
        ):
            self.app.routes_registry = self.routes_registry

        await self.signal_handler.startup(self.app)
        cleanup.assert_not_awaited()

        await self.signal_handler.shutdown(self.app)
        cleanup.assert_awaited_once()

    @asynctest.patch("asyncworker.signals.handlers.http.web.AppRunner.cleanup")
    async def test_shutdown_does_nothing_if_app_doesnt_have_an_http_runner(
        self, cleanup
    ):
        self.app.routes_registry = self.routes_registry

        self.assertNotIn("runner", self.app[RouteTypes.HTTP])

        await self.signal_handler.shutdown(self.app)

        cleanup.assert_not_awaited()

    async def test_simple_handler_200_response(self):
        """
        Tests if a response is correctly handled, Starts a real aiohttp server
        """

        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        async def index():
            return web.json_response({"OK": True})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/")
                self.assertEqual(resp.status, 200)
                data = await resp.json()
                self.assertDictEqual({"OK": True}, data)

    async def test_can_call_handler_without_annotation(self):
        """
        For backward compatiilty, wew can call a handler that receives
        one parameter and does not have any type annotations
        """

        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        async def handler():
            return web.json_response({})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/")
                self.assertEqual(200, resp.status)

    async def test_add_registry_to_all_requests(self):
        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        async def handler(wrapper: RequestWrapper):
            request = wrapper.http_request
            registry: TypesRegistry = request["types_registry"]
            assert registry is not None
            assert isinstance(registry, TypesRegistry)
            return web.json_response({})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/")
                self.assertEqual(200, resp.status)

    async def test_resolves_handler_parameters(self):
        expected_user_name = "Some User Name"

        class User:
            def __init__(self, name):
                self.name = name

        def insert_user_into_type_registry(handler):
            async def _wrapper(wrapper: RequestWrapper):
                wrapper.types_registry.set(User(name=expected_user_name))
                return await call_http_handler(wrapper.http_request, handler)

            return _wrapper

        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        @insert_user_into_type_registry
        async def handler(user: User):
            return web.json_response({"name": user.name})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/")
                self.assertEqual(200, resp.status)
                resp_data = await resp.json()
                self.assertEqual({"name": expected_user_name}, resp_data)

    async def test_multiple_decorators_using_call_handler(self):
        expected_user_name = "Some User Name"
        expected_account_name = "Account Name"

        class User:
            def __init__(self, name):
                self.name = name

        class Account:
            def __init__(self, name):
                self.name = name

        def insert_user_into_type_registry(handler):
            async def _wrapper(wrapper: RequestWrapper):
                wrapper.types_registry.set(User(name=expected_user_name))
                return await call_http_handler(wrapper.http_request, handler)

            return _wrapper

        def insert_account_into_type_registry(handler):
            async def _wrapper(wrapper: RequestWrapper):
                wrapper.types_registry.set(Account(name=expected_account_name))
                return await call_http_handler(wrapper.http_request, handler)

            return _wrapper

        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        @insert_account_into_type_registry
        @insert_user_into_type_registry
        async def handler(user: User, account: Account):
            return web.json_response(
                {"account": account.name, "user": user.name}
            )

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/")
                self.assertEqual(200, resp.status)
                resp_data = await resp.json()
                self.assertEqual(
                    {
                        "user": expected_user_name,
                        "account": expected_account_name,
                    },
                    resp_data,
                )

    async def test_resolves_handler_parameters_when_receiving_request_wrapper(
        self
    ):
        def my_decorator(handler):
            async def _wrapper(wrapper: RequestWrapper):
                return await call_http_handler(wrapper.http_request, handler)

            return _wrapper

        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        @my_decorator
        async def handler(wrapper: RequestWrapper):
            return web.json_response({"num": wrapper.http_request.query["num"]})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/", params={"num": 42})
                self.assertEqual(200, resp.status)
                resp_data = await resp.json()
                self.assertEqual({"num": "42"}, resp_data)

    async def test_ignores_return_annotation_when_resolving_parameters(self):
        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        async def handler(wrapper: RequestWrapper) -> web.Response:
            return web.json_response({"num": wrapper.http_request.query["num"]})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/", params={"num": 42})
                self.assertEqual(200, resp.status)
                resp_data = await resp.json()
                self.assertEqual({"num": "42"}, resp_data)

    async def test_handler_can_receive_aiohttp_request(self):
        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        async def handler(request: web.Request) -> web.Response:
            return web.json_response({"num": request.query["num"]})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/", params={"num": 42})
                self.assertEqual(200, resp.status)
                resp_data = await resp.json()
                self.assertEqual({"num": "42"}, resp_data)

    async def test_handler_decorator_can_receive_aiohttp_request(self):
        def my_decorator(handler):
            async def _wrapper(request: web.Request):
                return await call_http_handler(request, handler)

            return _wrapper

        @self.app.route(["/"], type=RouteTypes.HTTP, methods=["GET"])
        @my_decorator
        async def handler(wrapper: RequestWrapper):
            return web.json_response({"num": wrapper.http_request.query["num"]})

        async with HttpClientContext(self.app) as client:
            settings_mock = Settings()
            with mock.patch(
                "asyncworker.signals.handlers.http.settings", settings_mock
            ):
                resp = await client.get("/", params={"num": 42})
                self.assertEqual(200, resp.status)
                resp_data = await resp.json()
                self.assertEqual({"num": "42"}, resp_data)
