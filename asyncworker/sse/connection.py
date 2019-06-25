from dataclasses import dataclass
from typing import Any

from asyncworker.routes import RouteTypes


@dataclass
class SSEConnection:
    url: str
    user: str = None
    password: str = None
    route_type = RouteTypes.SSE
    logger: Any = None  # fixme: shouldn't be here
