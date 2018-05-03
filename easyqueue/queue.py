import abc
import json
from typing import Dict, Tuple, Any

from easyqueue.exceptions import UndecodableMessageException


Message = Tuple[Dict, int]


class DeliveryModes:
    NON_PERSISTENT = 1
    PERSISTENT = 2


class BaseQueue(metaclass=abc.ABCMeta):
    def __init__(self,
                 host: str,
                 username: str,
                 password: str,
                 virtual_host: str = '/',
                 heartbeat: int = 60):
        self.host = host
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.heartbeat = heartbeat

    @abc.abstractmethod
    def serialize(self, body: Any, **kwargs) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, body: str) -> Any:
        raise NotImplementedError

    def _parse_message(self, content) -> Dict[str, Any]:
        """
        Gets the raw message body as an input, handles deserialization and
        outputs
        :param content: The raw message body
        """
        try:
            return self.deserialize(content)
        except TypeError:
            return self.deserialize(content.decode())
        except json.decoder.JSONDecodeError as e:
            raise UndecodableMessageException('"{content}" can\'t be decoded as JSON'
                                              .format(content=content))


class BaseJsonQueue(BaseQueue):
    content_type = 'application/json'

    def serialize(self, body: Any, **kwargs) -> str:
        return json.dumps(body, **kwargs)

    def deserialize(self, body: str) -> Any:
        return json.loads(body)

