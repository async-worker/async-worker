from typing import Optional

from asynctest import TestCase

from asyncworker.routes import Model


class MyModel(Model):
    field: Optional[int]


class RouteModelTest(TestCase):
    async def test_set_item_field_exist(self):

        model = MyModel()
        model["field"] = 42
        self.assertEqual(42, model["field"])

    async def test_set_item_field_does_not_exist(self):
        model = MyModel()
        with self.assertRaises(KeyError):
            model["not_found"] = 10

    async def test_eq_compare_with_dict(self):
        model = MyModel(field=55)
        self.assertTrue(model == {"field": 55})

    async def test_eq_compare_with_other_model(self):
        model = MyModel(field=99)
        self.assertTrue(model == model)

    async def test_len(self):
        model = MyModel(field=100)
        self.assertEqual(1, len(model))

    async def test_keys(self):
        model = MyModel()
        self.assertEqual(["field"], list(model.keys()))
