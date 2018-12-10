from aiohttp import web
from asyncworker.signals.handlers.base import SignalHandler
from asyncworker.options import RouteTypes
from asyncworker.conf import settings


class HTTPServer(SignalHandler):
    async def startup(self, app):
        app[RouteTypes.HTTP] = {}
        http_routes = app.routes_registry.http_routes
        if not http_routes:
            return

        app[RouteTypes.HTTP]["http_app"] = http_app = web.Application()
        for route in http_routes:
            http_app.router.add_route(**route)

        app[RouteTypes.HTTP]["http_runner"] = web.AppRunner(http_app)
        await app[RouteTypes.HTTP]["http_runner"].setup()
        app[RouteTypes.HTTP]["http_site"] = web.TCPSite(
            runner=app[RouteTypes.HTTP]["http_runner"],
            host=settings.HTTP_HOST,
            port=settings.HTTP_PORT,
        )
        await app[RouteTypes.HTTP]["http_site"].start()

    async def shutdown(self, app):
        if "http_runner" in app[RouteTypes.HTTP]:
            await app[RouteTypes.HTTP]["http_runner"].cleanup()
