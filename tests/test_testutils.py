import unittest

from tests.utils import typed_any


class TypedAnyTests(unittest.TestCase):
    def test_instances_of_the_same_classes_are_equal(self):
        self.assertEqual(5, typed_any(int))
        self.assertEqual('abc', typed_any(str))
        self.assertEqual(Exception(), typed_any(ValueError))

    def test_isntances_of_different_calsses_arent_equal(self):
        self.assertNotEqual(5, typed_any(str))
        self.assertNotEqual('abc', typed_any(int))
        self.assertNotEqual(ValueError(), typed_any(Exception))
