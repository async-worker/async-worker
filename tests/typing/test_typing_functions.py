from typing import Generic, TypeVar

from asynctest import TestCase

from asyncworker.typing import get_args, get_origin

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
