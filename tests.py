__author__ = 'Ian S. Evans'

from py_collection_json import CollectionPlusJSON


def test_correct_standard_properties():
    try:
        CollectionPlusJSON(links=[], items=[], queries=[], template=CollectionPlusJSON.Template(),
                           error=CollectionPlusJSON.Error())
    except TypeError:
        return False
    else:
        return True


def test_incorrect_standard_properties():
    to_return = False
    try:
        CollectionPlusJSON(links=None, items=[], queries=[], template=CollectionPlusJSON.Template(),
                           error=CollectionPlusJSON.Error())
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(links=[], items=None, queries=[], template=CollectionPlusJSON.Template(),
                           error=CollectionPlusJSON.Error())
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(links=[], items=[], queries=None, template=CollectionPlusJSON.Template(),
                           error=CollectionPlusJSON.Error())
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(links=[], items=[], queries=[], template=None, error=CollectionPlusJSON.Error())
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(links=[], items=[], queries=[], template=CollectionPlusJSON.Template(), error=None)
    except TypeError:
        to_return = True
    return to_return

assert test_correct_standard_properties()
assert test_incorrect_standard_properties()