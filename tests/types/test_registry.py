from typing import List

from asynctest import TestCase

from asyncworker.types.registry import TypesRegistry


class TypesRegistryTest(TestCase):
    async def setUp(self):
        self.registry = TypesRegistry()

    async def test_simple_set_get_object(self):
        class SomeObject:
            pass

        instance = SomeObject()
        self.registry.set(instance)
        self.assertEqual(instance, self.registry.get(SomeObject))

    async def test_get_object_not_found(self):
        class OtherObject:
            pass

        self.assertIsNone(self.registry.get(OtherObject))

    async def test_simple_coroutine_with_typehint(self):
        class MyClass:
            pass

        async def my_coro(p: MyClass):
            return p

        instance = MyClass()
        self.assertTrue(instance)

    async def test_register_a_new_type_with_its_name(self):
        """
        Um parametro registrado apenas com o tipo é diferente de um
        parametro registrado com tipo e nome
        """

        class MyClass:
            async def my_coro(self, obj_id: int):
                return obj_id

        self.registry.set(42, param_name="obj_id")
        self.registry.set(10)
        self.assertEqual(42, self.registry.get(int, param_name="obj_id"))

    async def test_register_returns_None_when_name_not_found(self):
        """
        Lança uma exception quando tentamos buscar um parametro pelo
        tipo e pelo nome mas ele não é encontrado.
        """

        class MyClass:
            async def my_coro(self, obj_id: int):
                return obj_id

        self.registry.set(42, param_name="obj_id")
        self.assertEqual(None, self.registry.get(str, param_name="obj_id"))
