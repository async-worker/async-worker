from collections import UserDict
from typing import Callable, Coroutine, Dict, List, Any

from cached_property import cached_property

from asyncworker.conf import settings
from asyncworker.options import DefaultValues, Events, Options, RouteTypes

RouteHandler = Callable[[], Coroutine]
Route = Dict[str, Any]


class RoutesRegistry(UserDict):
    @cached_property
    def http_routes(self) -> List[Route]:
        routes = []
        for handler, route in self.items():
            if route["type"] is not RouteTypes.HTTP:
                continue
            for path in route["routes"]:
                for method in route["methods"]:
                    routes.append(
                        {"method": method, "path": path, "handler": handler}
                    )
        return routes

    @cached_property
    def amqp_routes(self) -> List[Dict]:
        routes = []
        for handler, route in self.items():
            if route["type"] is not RouteTypes.AMQP_RABBITMQ:
                continue
            options = route["options"]
            routes.append(
                {
                    "routes": route["routes"],
                    "handler": handler,
                    "options": {
                        "vhost": route.get(
                            "vhost", settings.AMQP_DEFAULT_VHOST
                        ),
                        "bulk_size": options.get(
                            Options.BULK_SIZE, DefaultValues.BULK_SIZE
                        ),
                        "bulk_flush_interval": options.get(
                            Options.BULK_FLUSH_INTERVAL,
                            DefaultValues.BULK_FLUSH_INTERVAL,
                        ),
                        Events.ON_SUCCESS: options.get(
                            Events.ON_SUCCESS, DefaultValues.ON_SUCCESS
                        ),
                        Events.ON_EXCEPTION: options.get(
                            Events.ON_EXCEPTION, DefaultValues.ON_EXCEPTION
                        ),
                    },
                }
            )
        return routes

    @cached_property
    def sse_routes(self) -> List[Route]:
        routes = []
        for handler, route in self.items():
            if route["type"] is not RouteTypes.SSE:
                continue

            options = route["options"]
            headers = route.pop("headers", {})
            default_headers = route["default_options"].get("headers", {})
            routes.append(
                {
                    "routes": route["routes"],
                    "handler": handler,
                    "options": {
                        "bulk_size": options.get(
                            Options.BULK_SIZE, DefaultValues.BULK_SIZE
                        ),
                        "bulk_flush_interval": options.get(
                            Options.BULK_FLUSH_INTERVAL,
                            DefaultValues.BULK_FLUSH_INTERVAL,
                        ),
                        "headers": {**headers, **default_headers},
                    },
                }
            )
        return routes
