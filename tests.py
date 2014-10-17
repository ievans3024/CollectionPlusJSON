__author__ = 'Ian S. Evans'

from py_collection_json import CollectionPlusJSON


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
                raise AssertionError(
                    'CollectionPlusJSON({arg}={value}) expected to raise TypeError but did not.'.format(
                        arg=arg, value=str(value)
                    )
                )
        if arg == 'template':
            try:
                CollectionPlusJSON(template=[])
            except TypeError:
                pass
            else:
                raise AssertionError('CollectionPlusJSON(template=[]) expected to raise TypeError but did not.')

# Default init with no args, should not raise errors
CollectionPlusJSON()

# init with acceptable arg types, should not raise errors
CollectionPlusJSON(links=[], items=[], queries=[], template=CollectionPlusJSON.Template(),
                   error=CollectionPlusJSON.Error())

# incorrect types should throw errors
incorrect_standard_properties()