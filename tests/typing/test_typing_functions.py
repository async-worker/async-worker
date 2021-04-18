from typing import Generic, TypeVar

from asynctest import TestCase

from asyncworker.decorators import wraps
from asyncworker.typing import (
    get_args,
    get_origin,
    get_handler_original_typehints,
)

T = TypeVar("T")
K = TypeVar("K")


class MyGeneric(Generic[T]):
    pass


class MyGenericTwoArguments(Generic[K, T]):
    pass


class MyObject:
    pass


class TestTypingFunctions(TestCase):
    async def setUp(self):
        pass

    async def test_get_args_generic_type(self):
        self.assertEqual((MyObject,), get_args(MyGeneric[MyObject]))
        self.assertEqual(
            (int, MyObject), get_args(MyGenericTwoArguments[int, MyObject])
        )

    async def test_get_args_concrete_type(self):
        self.assertIsNone(get_args(MyObject))

    async def test_get_origin_generic_type(self):
        self.assertEqual(MyGeneric, get_origin(MyGeneric[MyObject]))
        self.assertEqual(
            MyGenericTwoArguments,
            get_origin(MyGenericTwoArguments[int, MyObject]),
        )

    async def test_get_origin_concrete_type(self):
        self.assertIsNone(get_origin(MyObject))


class TestGetOriginalHandlerTypeHints(TestCase):
    async def test_does_not_have_attribute(self):
        def func(a: int, b: bool):
            pass

        self.assertEqual(
            get_handler_original_typehints(func), {"a": int, "b": bool}
        )
        self.assertFalse(hasattr(func, "asyncworker_original_annotations"))

    async def test_has_attribute(self):
        def simple_deco(handler):
            @wraps(handler)
            async def _wrapper():
                return await handler()

            return _wrapper

        def other_deco(handler):
            @wraps(handler)
            async def _wrap():
                return get_handler_original_typehints(handler)

            return _wrap

        @other_deco
        @simple_deco
        async def handler(a: bool, s: str):
            return 42

        result = await handler()
        self.assertEqual(result, {"a": bool, "s": str})
        self.assertTrue(hasattr(handler, "asyncworker_original_annotations"))
