__author__ = 'Ian S. Evans'

from py_collection_json import CollectionPlusJSON


def incorrect_standard_properties():
    """
    Test that a CollectionPlusJSON object will not init successfully with any of the standard optional arguments
    set to a number of basic incorrect types.
    :raises AssertionError: If arg values that should be considered invalid do not raise a TypeError
    :return:
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

# Correct types in arguments should not raise errors
CollectionPlusJSON(links=[], items=[], queries=[], template=CollectionPlusJSON.Template(),
                   error=CollectionPlusJSON.Error())

# Incorrect types in arguments should raise errors
incorrect_standard_properties()

# Instance should accept mutable-iterable-style item getting, setting and deleting
collection = CollectionPlusJSON()
collection['test'] = 'test'
collection['test']
del collection['test']

# Inner classes should be appear to be the same in an instance or direct from class.
assert CollectionPlusJSON.BaseCollectionItem == collection.BaseCollectionItem
assert CollectionPlusJSON.Error == collection.Error
assert CollectionPlusJSON.Item == collection.Item
assert CollectionPlusJSON.Link == collection.Link
assert CollectionPlusJSON.Query == collection.Query
assert CollectionPlusJSON.Template == collection.Template

# repr of CollectionPlusJSON instance should not raise a TypeError from json.dumps
collection['links'] = [collection.Link(uri="/items/%d" % i, rel="more") for i in range(20)]
repr(collection)
del collection['links']

# Instance str and repr should appear to be the same
assert str(collection) == repr(collection), """str and repr methods should return the same string"""

# Paginate method should not have first, prev links on first page; next, last links on last page
collection['items'] = [collection.Item() for i in range(1, 20)]
collection_pages = collection.paginate()
for page in collection_pages:
    if collection_pages.index(page) == 0:
        # First page should not have first or previous links
        link_rels = [link.rel for link in page['links']]
        if "first" in link_rels or "prev" in link_rels:
            raise AssertionError("CollectionPlusJSON.paginate: First page has links before self")
    if page == collection_pages[-1]:
        # Last page should not have next or last links
        link_rels = [link.rel for link in page['links']]
        if "next" in link_rels or "last" in link_rels:
            raise AssertionError("CollectionPlusJSON.paginate: Last page has links after self")