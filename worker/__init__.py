import functools
import asyncio

def entrypoint(f):
    @functools.wraps(f)
    def _(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return _


class App:
    def __init__(self):
        self.routes_registry = {}

    def route(self, routes, vhost):
        def wrap(f):
            for route in routes:
                self.routes_registry[route] = {
                    "route": route,
                    "handler": f,
                    "options": {
                        "vhost": vhost,
                    }
                }
            return f
        return wrap
