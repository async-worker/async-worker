import os
from functools import wraps

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from asyncworker import App


def http_client(app: App):
    def decorator(handler, *args, **kwargs):
        @wraps(handler)
        async def inner_deco(*args, **kwargs):

            routes = app.routes_registry.http_routes
            http_app = web.Application()

            for route in routes:
                for route_def in route.aiohttp_routes():
                    route_def.register(http_app.router)

            server = TestServer(
                http_app, port=os.getenv("TEST_ASYNCWORKER_HTTP_PORT")
            )
            client = TestClient(server)
            await server.start_server()

            try:
                return await handler(client, *args, **kwargs)
            except Exception as e:
                raise e
            finally:
                await server.close()
                await client.close()

        return inner_deco

    return decorator
