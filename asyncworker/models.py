from collections import UserDict
from typing import Callable, Coroutine, Dict

from yarl import cached_property


Route = Callable[[], Coroutine]


class Routes(UserDict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}

    @cached_property
    def amqp_routes(self) -> Dict[Route, Dict]:
        routes = {}
        for handler, route in self.items():
            if route['type'] == 'amqp':
                routes[handler] = dict(**route)
                routes[handler].pop('type')
        return routes
