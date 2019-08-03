import abc
from pydantic import BaseModel


class BaseConnection(BaseModel, abc.ABC):
    """
    Abstract Base Class for asyncworker's connections
    """
