from aiohttp import web
from asyncworker.signals.handlers.base import SignalHandler

from asyncworker.conf import settings


class HTTPServer(SignalHandler):
    async def startup(self, app):
        http_routes = app.routes_registry.http_routes
        if not http_routes:
            return

        app["http_app"] = web.Application()
        for route in http_routes:
            app["http_app"].router.add_route(**route)

        app["http_runner"] = web.AppRunner(app["http_app"])
        await app["http_runner"].setup()
        app["http_site"] = web.TCPSite(
            runner=app["http_runner"],
            host=settings.HTTP_HOST,
            port=settings.HTTP_PORT,
        )
        await app["http_site"].start()

    async def shutdown(self, app):
        if "http_runner" in app:
            await app["http_runner"].cleanup()
