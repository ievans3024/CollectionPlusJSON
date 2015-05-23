__author__ = 'Ian S. Evans'

import json

from collection_plus_json import Array, Collection, Data, Error, Item, Link, Query, Template
from unittest import TestCase, TestSuite

# TODO: write tests
# TODO: write messages for assertions

# Array tests
class ArrayTests(TestCase):

    def test_comparison(self):
        """Testing several comparison scenarios involving Arrays"""

        type1_array_1 = Array(['foo', 'bar', 'baz'], str)
        type1_array_2 = Array(['foo', 'bor', 'biz'], str)
        type2_array_1 = Array([1, 2, 3], int)

        # Array(Type1) == Array(Type1) should be true if both
        # contain the same type of objects and their contents are the same
        self.assertEqual(type1_array_1.required_class, Array(['foo', 'bar', 'baz'], str).required_class)
        self.assertEqual(type1_array_1.data, Array(['foo', 'bar', 'baz'], str).data)
        self.assertTrue(type1_array_1 == Array(['foo', 'bar', 'baz'], str))
        self.assertEqual(type1_array_1, Array(['foo', 'bar', 'baz'], str))

        # Array() != Array() should be True if
        #   1) each array contains a different type of object
        #   2) both arrays contain the same type of objects and
        #      their contents are not equal
        self.assertNotEqual(type1_array_1.required_class, type2_array_1.required_class)
        self.assertNotEqual(type1_array_1.data, type1_array_2.data)
        self.assertNotEqual(type1_array_1.data, type2_array_1.data)
        self.assertTrue(type1_array_1 != type1_array_2)
        self.assertTrue(type1_array_1 != type2_array_1)
        self.assertNotEqual(type1_array_1, type1_array_2)
        self.assertNotEqual(type1_array_1, type2_array_1)

    def test_addition(self):
        """Testing several addition scenarios involving Arrays"""

        type1_array_1 = Array(['foo', 'bar', 'baz'], str)
        type1_array_2 = Array(['foo', 'bor', 'biz'], str)
        type1_array_1_2 = Array(['foo', 'bar', 'baz', 'foo', 'bor', 'biz'], str)
        type1_array_2_1 = Array(['foo', 'bor', 'biz', 'foo', 'bar', 'baz'], str)
        type2_array_1 = Array([1, 2, 3], int)

        # What should be successful addition should not raise any errors:
        try:
            type1_array_1 + type1_array_2
        except BaseException as e:
            self.fail(
                "What should be successful Array addition failed with exception: {x}".format(x=e)
            )

        # Successful addition needs to return an Array
        self.assertIsInstance((type1_array_1 + type1_array_2), Array)

        # Successful addition needs to return an Array
        #    containing all the values of the added Arrays
        self.assertEqual(
            (type1_array_1 + type1_array_2),
            type1_array_1_2
        )

        # Assure order is maintained by flipping addition
        #    and the expected result
        self.assertEqual(
            (type1_array_2 + type1_array_1),
            type1_array_2_1
        )

        # Addition should return a new object, not a modified existing object
        self.assertIsNot((type1_array_1 + type1_array_2), type1_array_1)
        self.assertIsNot((type1_array_1 + type1_array_2), type1_array_2)

        # Array[Type1] + Array[Type2] should raise a TypeError
        with self.assertRaises(TypeError):
            type1_array_1 + type2_array_1

        # Array + NonArray should raise a TypeError
        with self.assertRaises(TypeError):
            type1_array_1 + "this should fail"
            
    def test_subtraction(self):
        """Testing several subtraction scenarios involving Arrays"""

        type1_array_1 = Array(['foo', 'bar', 'baz'], str)
        type1_array_2 = Array(['foo', 'bor', 'biz'], str)
        type1_array_1_2 = Array(['bar', 'baz'], str)
        type1_array_2_1 = Array(['bor', 'biz'], str)
        type2_array_1 = Array([1, 2, 3], int)

        # What should be successful subtraction should not raise any errors:
        try:
            type1_array_1 - type1_array_2
        except BaseException as e:
            self.fail(
                "What should be successful Array subtraction failed with exception: {x}".format(x=e)
            )

        # Successful subtraction needs to return an Array
        self.assertIsInstance((type1_array_1 - type1_array_2), Array)

        # Successful subtraction needs to return an Array
        #    containing all the values of the subtracted Arrays
        self.assertEqual(
            (type1_array_1 - type1_array_2),
            type1_array_1_2
        )

        # Assure order is maintained by flipping subtraction
        #    and the expected result
        self.assertEqual(
            (type1_array_2 - type1_array_1),
            type1_array_2_1
        )

        # Subtraction should return a new object, not a modified existing object
        self.assertIsNot((type1_array_1 - type1_array_2), type1_array_1)
        self.assertIsNot((type1_array_1 - type1_array_2), type1_array_2)

        # Array[Type1] - Array[Type2] should raise a TypeError
        with self.assertRaises(TypeError):
            type1_array_1 - type2_array_1

        # Array - NonArray should raise a TypeError
        with self.assertRaises(TypeError):
            type1_array_1 - "this should fail"

    def test_serializable(self):
        """
        Array.get_serializable() should return an object
        that can be dumped into a string with json.dumps.
        """

        foo_array = Array(['foo', 'bar', 'baz'], str)

        try:
            json.dumps(foo_array.get_serializable())
        except (ValueError, TypeError) as e:
            self.fail(e)

    def test_string(self):
        """
        Array.__str__ must return a string formatted in a predictable way.
        """

        foo_array = Array(['foo', 'bar', 'baz'], str)

        self.assertEqual(str(foo_array), '["foo", "bar", "baz"]')


# Data tests


# Error tests


# Item tests


# Link tests


# Query tests


# Template tests


# Collection tests


def test_all():
    test_suite = TestSuite()
    test_suite.addTest(ArrayTests('test_comparison'))
    test_suite.addTest(ArrayTests('test_addition'))
    test_suite.addTest(ArrayTests('test_subtraction'))
    test_suite.addTest(ArrayTests('test_serializable'))
    test_suite.addTest(ArrayTests('test_string'))
    return test_suite
