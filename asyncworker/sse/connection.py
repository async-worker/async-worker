from dataclasses import dataclass
from typing import Optional

from asyncworker.routes import RouteTypes


@dataclass
class SSEConnection:
    url: str
    user: Optional[str] = None
    password: Optional[str] = None
    route_type = RouteTypes.SSE
