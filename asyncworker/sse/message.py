from typing import List, Dict, Union


class SSEMessage:
    def __init__(self, event_name: str, event_body: Union[Dict, List]) -> None:
        self.name = event_name
        self.body = event_body
