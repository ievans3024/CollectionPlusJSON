__author__ = 'Ian S. Evans'

from py_collection_json import CollectionPlusJSON


def default_init():
    """
    Test that a CollectionPlusJSON object will successfully init with no arguments.
    :return: True if successfully instantiated, False otherwise.
    """
    try:
        CollectionPlusJSON()
    except:
        return False
    else:
        return True


def correct_standard_properties():
    """
    Test that a CollectionPlusJSON object will init successfully with all correct types in standard optional arguments.
    :return: True if successfully instantiated, False if a TypeError is thrown
    """
    try:
        CollectionPlusJSON(links=[], items=[], queries=[], template=CollectionPlusJSON.Template(),
                           error=CollectionPlusJSON.Error())
    except TypeError:
        return False
    else:
        return True


def incorrect_standard_properties():
    """
    Test that a CollectionPlusJSON object will not init successfully with any of the standard optional arguments
    set to a number of basic incorrect types.
    :return: True if not successfully instantiated, False if a TypeError is thrown
    """
    to_return = False
    try:
        CollectionPlusJSON(links=None)
        CollectionPlusJSON(links='')
        CollectionPlusJSON(links={})
        CollectionPlusJSON(links=())
        CollectionPlusJSON(links=1)        
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(items=None)
        CollectionPlusJSON(items='')
        CollectionPlusJSON(items={})
        CollectionPlusJSON(items=())
        CollectionPlusJSON(items=1)
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(queries=None)
        CollectionPlusJSON(queries='')
        CollectionPlusJSON(queries={})
        CollectionPlusJSON(queries=())
        CollectionPlusJSON(queries=1)
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(template=None)
        CollectionPlusJSON(template='')
        CollectionPlusJSON(template={})
        CollectionPlusJSON(template=())
        CollectionPlusJSON(template=1)
        CollectionPlusJSON(template=[])
    except TypeError:
        to_return = True
    try:
        CollectionPlusJSON(error=None)
        CollectionPlusJSON(error='')
        CollectionPlusJSON(error={})
        CollectionPlusJSON(error=())
        CollectionPlusJSON(error=1)
        CollectionPlusJSON(error=[])
    except TypeError:
        to_return = True
    return to_return

assert default_init()
assert correct_standard_properties()
assert incorrect_standard_properties()