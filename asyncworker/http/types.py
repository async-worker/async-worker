from typing import Generic, TypeVar, Type

from asyncworker.http.wrapper import RequestWrapper

T = TypeVar("T")


class PathParam(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value

    @classmethod
    async def from_request(
        cls, request: RequestWrapper, arg_name: str, arg_type: Type
    ) -> "PathParam":
        val = request.http_request.match_info[arg_name]
        return cls(arg_type(val))

    def unpack(self) -> T:
        return self._value
