
from asyncworker import BaseApp
from asyncworker.options import Options, Defaultvalues


SSE_DEFAULT_HEADERS = {
    "Accept": "text/event-stream",
}


class SSEApplication(BaseApp):
    def __init__(self, url, user, password, headers=SSE_DEFAULT_HEADERS):
        self.routes_registry = {}
        self.url = url
        self.user = user
        self.password = password
        self.headers = headers

    def route(self, routes, headers={}, options={}):
        def wrap(f):
            self.routes_registry[f] = {
                "routes": routes,
                "handler": f,
                "options": {
                    "bulk_size": options.get(Options.BULK_SIZE, Defaultvalues.BULK_SIZE),
                    "bulk_flush_interval": options.get(Options.BULK_FLUSH_INTERVAL, Defaultvalues.BULK_FLUSH_INTERVAL),
                    "headers": {
                        **self.headers,
                        **headers,
                    },
                }
            }
            return f
        return wrap

