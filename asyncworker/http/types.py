from abc import abstractmethod
from typing import Generic, TypeVar, Type

from aiohttp.web import HTTPBadRequest

from asyncworker.http.wrapper import RequestWrapper

T = TypeVar("T")


class RequestParser(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value

    @classmethod
    @abstractmethod
    async def from_request(
        cls, request: RequestWrapper, arg_name: str, arg_type: Type
    ) -> "RequestParser[T]":
        raise NotImplementedError()

    async def unpack(self) -> T:
        return self._value


class PathParam(RequestParser[T]):
    @classmethod
    async def from_request(
        cls, request: RequestWrapper, arg_name: str, arg_type: Type
    ) -> "PathParam[T]":
        val = request.http_request.match_info[arg_name]
        try:
            return cls(arg_type(val))
        except ValueError as ve:
            raise HTTPBadRequest(reason=ve.args[0])
