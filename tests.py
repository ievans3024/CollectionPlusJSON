__author__ = 'Ian S. Evans'

from collection_plus_json import Array, Collection, Data, Error, Item, Link, Query, Template
from unittest import TestCase, TestSuite

# TODO: write tests
# TODO: write messages for assertions

test_all = TestSuite()

# Array tests
class ArrayTests(TestCase):

    def test_comparison(self):

        type1_array_1 = Array(['foo', 'bar', 'baz'], str)
        type1_array_2 = Array(['foo', 'bor', 'biz'], str)
        type2_array_1 = Array([1, 2, 3], int)

        # Array(Type1) == Array(Type1) should be true if both
        # contain the same type of objects and their contents are the same
        self.assertEqual(type1_array_1.required_class, type1_array_2.required_class)
        self.assertEqual(type1_array_1.data, type1_array_2.data)
        self.assertTrue(type1_array_1 == type1_array_2)
        self.assertEqual(type1_array_1, type1_array_2)

        # Array() != Array() should be True if
        #   1) each array contains a different type of object
        #   2) both arrays contain the same type of objects and
        #   their contents are not equal
        self.assertNotEqual(type1_array_1.required_class, type2_array_1.required_class)
        self.assertNotEqual(type1_array_1.data, type2_array_1.data)
        self.assertTrue(type1_array_1 != type2_array_1)
        self.assertNotEqual(type1_array_1, type2_array_1)

    def test_addition(self):

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
        # containing all the values of the added Arrays
        self.assertEqual(
            (type1_array_1 + type1_array_2),
            type1_array_1_2
        )

        # Assure order is maintained by flipping addition
        # and the expected result
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
        # containing all the values of the subtracted Arrays
        self.assertEqual(
            (type1_array_1 - type1_array_2),
            type1_array_1_2
        )

        # Assure order is maintained by flipping subtraction
        # and the expected result
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


# Data tests


# Error tests


# Item tests


# Link tests


# Query tests


# Template tests


# Collection tests
