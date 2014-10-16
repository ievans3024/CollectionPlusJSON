__author__ = 'Ian S. Evans'

from py_collection_json import CollectionPlusJSON


def test_correct_standard_properties():
    try:
        CollectionPlusJSON(links=[], items=[], )
    except TypeError:
        return False
    else:
        return True