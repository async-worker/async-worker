import unittest

import asynctest
from urllib.parse import urljoin

from asyncworker import App
from asyncworker.routes import SSERoute
from asyncworker.options import (
    Options,
    DefaultValues,
    Events,
    Actions,
    RouteTypes,
)

from asyncworker.sse.connection import SSEConnection


class AppTest(asynctest.TestCase):
    def setUp(self):
        self.default_headers = {"X-New-Header": "X-Value"}
        self.connection_parameters = {
            "url": "http://127.0.0.1",
            "user": "guest",
            "password": "guest",
        }

    @asynctest.skip(
        "Additional headers logic is broken because SSEConsumer isn't using "
        "the headers provided by the route"
    )
    async def test_check_route_registry_full_options(self):
        expected_route = ["/v2/events", "/other/path"]
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(
            expected_route,
            type=RouteTypes.SSE,
            options={Options.BULK_SIZE: 1024, Options.BULK_FLUSH_INTERVAL: 120},
        )
        async def _handler(message):
            return 42

        routes = app.routes_registry.sse_routes
        self.assertIsNotNone(routes)
        expected_registry_entry = {
            "type": RouteTypes.SSE,
            "routes": expected_route,
            "handler": _handler,
            "options": {
                "bulk_size": 1024,
                "bulk_flush_interval": 120,
                "headers": self.default_headers,
            },
        }
        self.assertEqual(expected_registry_entry, routes[0])
        self.assertEqual(42, await routes[0]["handler"](None))
        self.assertEqual(self.logger, app.logger)

    @asynctest.skip(
        "Additional headers logic is broken because SSEConsumer isn't using "
        "the headers provided by the route"
    )
    async def test_check_route_registry_add_headers_per_handler(self):
        expected_route = ["/v2/events", "/other/path"]
        aditional_headers = {"X-Other-Header": "X-Other-Value"}
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(
            expected_route,
            type=RouteTypes.SSE,
            headers=aditional_headers,
            options={Options.BULK_SIZE: 1024, Options.BULK_FLUSH_INTERVAL: 120},
        )
        async def _handler(message):
            return 42

        routes = app.routes_registry.sse_routes
        self.assertIsNotNone(routes)
        expected_registry_entry = SSERoute(
            type=RouteTypes.SSE,
            routes=expected_route,
            handler=_handler,
            options={
                "bulk_size": 1024,
                "bulk_flush_interval": 120,
                "headers": {**self.default_headers, **aditional_headers},
            },
        )
        self.assertEqual(expected_registry_entry, routes[0])
        self.assertEqual(42, await routes[0]["handler"](None))

    async def test_register_hander_on_route_registry(self):
        expected_route = ["/asgard/counts/ok"]
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(expected_route, type=RouteTypes.SSE)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(_handler, app.routes_registry[_handler]["handler"])
        self.assertEqual(
            42, await app.routes_registry[_handler]["handler"](None)
        )

    async def test_register_bulk_size(self):
        expected_bulk_size = 1024
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(
            ["my-queue"],
            type=RouteTypes.SSE,
            options={Options.BULK_SIZE: expected_bulk_size},
        )
        async def _handler(message):
            return 42

        routes = app.routes_registry.sse_routes
        self.assertEqual(len(routes), 1)
        self.assertEqual(expected_bulk_size, routes[0]["options"]["bulk_size"])
        self.assertEqual(42, await routes[0]["handler"](None))

    async def test_register_bulk_flush_timeout(self):
        expected_bulk_flush_interval = 120
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(
            ["my-queue"],
            type=RouteTypes.SSE,
            options={Options.BULK_FLUSH_INTERVAL: expected_bulk_flush_interval},
        )
        async def _handler(message):
            return 42

        routes = app.routes_registry.sse_routes
        self.assertEqual(len(routes), 1)
        self.assertEqual(
            expected_bulk_flush_interval,
            routes[0]["options"]["bulk_flush_interval"],
        )
        self.assertEqual(42, await routes[0]["handler"](None))

    async def test_register_default_bulk_size_and_default_bulk_flush_timeout(
        self
    ):
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(["my-queue"], type=RouteTypes.SSE)
        async def _handler(message):
            return 42

        routes = app.routes_registry.sse_routes
        self.assertEqual(len(routes), 1)
        self.assertEqual(
            DefaultValues.BULK_SIZE, routes[0]["options"]["bulk_size"]
        )
        self.assertEqual(
            DefaultValues.BULK_FLUSH_INTERVAL,
            routes[0]["options"]["bulk_flush_interval"],
        )
        self.assertEqual(42, await routes[0]["handler"](None))

    @unittest.skip("Decidir se teremos ON_SUCCESS Event")
    async def test_register_action_on_success(self):
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(
            ["my-queue"],
            type=RouteTypes.SSE,
            options={Events.ON_SUCCESS: Actions.REJECT},
        )
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(
            Actions.REJECT,
            app.routes_registry[_handler]["options"][Events.ON_SUCCESS],
        )

    @unittest.skip("Decidir se teremos ON_EXCEPTION Event")
    async def test_register_action_on_exception(self):
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(
            ["my-queue"],
            type=RouteTypes.SSE,
            options={Events.ON_EXCEPTION: Actions.ACK},
        )
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(
            Actions.ACK,
            app.routes_registry[_handler]["options"][Events.ON_EXCEPTION],
        )

    @unittest.skip("Decidir se teremos ON_SUCCESS/ON_EXCEPTION Event")
    async def test_test_register_default_actions(self):
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(["my-queue"], type=RouteTypes.SSE)
        async def _handler(message):
            return 42

        self.assertIsNotNone(app.routes_registry)
        self.assertEqual(
            Actions.ACK,
            app.routes_registry[_handler]["options"][Events.ON_SUCCESS],
        )
        self.assertEqual(
            Actions.REQUEUE,
            app.routes_registry[_handler]["options"][Events.ON_EXCEPTION],
        )

    async def test_instantiate_one_consumer_per_handler_one_handler_registered(
        self
    ):
        """
        Para cada handler registrado, teremos um Consumer. Esse Consumer conseguirá consumir múltiplas
        filas, se necessário.
        """
        app = App(connections=[SSEConnection(**self.connection_parameters)])

        @app.route(["/asgard/counts"], type=RouteTypes.SSE)
        async def _handler(message):
            return message

        await app.startup()
        consumers = app[RouteTypes.SSE]["consumers"]
        self.assertEqual(1, len(consumers))
        consumer = consumers[0]

        final_url = urljoin(self.connection_parameters["url"], "/asgard/counts")
        self.assertEqual([final_url], consumer.routes)
        self.assertEqual(final_url, consumer.url)
        self.assertEqual(self.connection_parameters["user"], consumer.username)
        self.assertEqual(
            self.connection_parameters["password"], consumer.password
        )

    @unittest.skip("Ainda a ser implementado")
    async def test_instantiate_one_consumer_per_handler_multiple_handlers_registered(
        self
    ):
        app = App(connections=[SSEConnection(**self.connection_parameters)])

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
        self.assertEqual(
            self.connection_parameters["host"],
            queue_connection_parameters["host"],
        )
        self.assertEqual(
            self.connection_parameters["user"],
            queue_connection_parameters["login"],
        )
        self.assertEqual(
            self.connection_parameters["password"],
            queue_connection_parameters["password"],
        )
        self.assertEqual(
            self.connection_parameters["prefetch_count"],
            consumers[0].queue.prefetch_count,
        )

        self.assertEqual(["asgard/counts/errors"], consumers[1].queue_name)
        self.assertEqual("fluentd", consumers[1].vhost)
        queue_connection_parameters = consumers[1].queue.connection_parameters
        self.assertEqual(
            self.connection_parameters["host"],
            queue_connection_parameters["host"],
        )
        self.assertEqual(
            self.connection_parameters["user"],
            queue_connection_parameters["login"],
        )
        self.assertEqual(
            self.connection_parameters["password"],
            queue_connection_parameters["password"],
        )
        self.assertEqual(
            self.connection_parameters["prefetch_count"],
            consumers[1].queue.prefetch_count,
        )
