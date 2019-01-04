from aiohttp import web
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.options import RouteTypes
from asyncworker.conf import settings


class HTTPServer(SignalHandler):
    async def startup(self, app):
        app[RouteTypes.HTTP] = {}
        routes = app.routes_registry.http_routes
        if not routes:
            return

        app[RouteTypes.HTTP]["app"] = http_app = web.Application()
        for route in routes:
            http_app.router.add_route(**route)

        app[RouteTypes.HTTP]["runner"] = web.AppRunner(http_app)
        await app[RouteTypes.HTTP]["runner"].setup()
        app[RouteTypes.HTTP]["site"] = web.TCPSite(
            runner=app[RouteTypes.HTTP]["runner"],
            host=settings.HTTP_HOST,
            port=settings.HTTP_PORT,
        )
        await app[RouteTypes.HTTP]["site"].start()

    async def shutdown(self, app):
        if RouteTypes.HTTP in app and "runner" in app[RouteTypes.HTTP]:
            await app[RouteTypes.HTTP]["runner"].cleanup()
