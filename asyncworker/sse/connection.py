from typing import Optional

from asyncworker.connections import BaseConnection
from asyncworker.routes import RouteTypes


class SSEConnection(BaseConnection):
    url: str
    user: Optional[str] = None
    password: Optional[str] = None
    route_type = RouteTypes.SSE
