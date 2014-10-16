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

assert test_correct_standard_properties()