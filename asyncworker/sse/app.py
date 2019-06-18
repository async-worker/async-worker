from typing import Dict

from asyncworker.app import App
from asyncworker.signals.handlers.sse import SSE

SSE_DEFAULT_HEADERS = {"Accept": "text/event-stream"}


class SSEApplication(App):
    handlers = (SSE(),)

    def __init__(
        self,
        url: str,
        logger,
        user: str = None,
        password: str = None,
        headers: Dict[str, str] = SSE_DEFAULT_HEADERS,
    ) -> None:
        super(SSEApplication, self).__init__()
        self.url = url
        self.user = user
        self.password = password
        self.default_route_options["headers"] = headers
        self.logger = logger
