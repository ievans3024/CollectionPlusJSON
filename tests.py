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
    args = ('links', 'items', 'queries', 'template')
    test_values = (None, '', {}, (), 1)
    for arg in args:
        for value in test_values:
            try:
                CollectionPlusJSON(**{arg: value})
            except TypeError:
                pass
            else:
                print(
                    'CollectionPlusJSON({arg}={value}) expected to raise TypeError but did not.'.format(
                        arg=arg, value=str(value)
                    )
                )
                return False
        if arg == 'template':
            try:
                CollectionPlusJSON(template=[])
            except TypeError:
                pass
            else:
                print('CollectionPlusJSON(template=[]) expected to raise TypeError but did not.')
                return False
    return True

assert default_init()
assert correct_standard_properties()
assert incorrect_standard_properties()