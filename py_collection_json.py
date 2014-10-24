__author__ = 'Ian S. Evans'
__version__ = '0.0.1'

import json
from collections import UserDict
from math import ceil as _ceil

MIMETYPE = 'application/vnd.collection+json'


class CollectionPlusJSON(UserDict):
    """
    A class for organizing data to package in the Collection+JSON hypermedia type.
    """

    mimetype = MIMETYPE

    class CollectionPlusJSONEncoder(json.JSONEncoder):
        """
        A custom extension for encoding CollectionPlusJSON data via the json module.
        """

        def default(self, o):
            if isinstance(o, (
                    CollectionPlusJSON.BaseCollectionItem,
                    CollectionPlusJSON.Error,
                    CollectionPlusJSON.Item,
                    CollectionPlusJSON.Link,
                    CollectionPlusJSON.Query,
                    CollectionPlusJSON.Template
            )):
                return o.get_serializable()
            return json.JSONEncoder.default(self, o)

    class BaseCollectionItem(object):
        """
        A base class for CollectionPlusJSON data, common methods
        """

        def __init__(self):
            pass

        def __str__(self):
            return json.dumps(self.__dict__)

        def __repr__(self):
            return self.__str__()

        def get_serializable(self):
            """
            Get a json-serializable representation of this data.
            """
            return self.__dict__

    class Error(BaseCollectionItem):
        """
        A class for storing data representing the Collection+JSON error property.
        """

        def __init__(self, title=None, code=None, message=None):
            if title is not None:
                self.title = title
            if code is not None:
                self.code = code
            if message is not None:
                self.message = message
            try:
                # Python 3
                super().__init__()
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.BaseCollectionItem, self).__init__()

    class Item(UserDict, BaseCollectionItem):
        """
        A class for storing data representing an individual Collection+JSON Item (stored in the items property)
        """

        def __init__(self, uri=None, links=None, **kwargs):
            if uri is not None:
                self.href = uri
            if links is not None:
                self.links = links
            try:
                # Python 3
                super().__init__(**kwargs)
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.Item, self).__init__(**kwargs)

        def __str__(self):
            return json.dumps(self.get_serializable())

        def get_serializable(self):
            """
            Get this Item's data in a json serializable format
            """
            item_dict = dict(**self.__dict__)
            if self.data:
                data_list = []
                for k, v in self.data.items():
                    to_append = {"name": k}
                    if hasattr(v, '__getitem__') and not isinstance(v, str):
                        try:
                            to_append["value"] = v[0]
                            to_append["prompt"] = v[1]
                        except IndexError:
                            # TODO: debug and fix this
                            raise IndexError(str(v) + " causing IndexError in Item.get_serializable.")
                    else:
                        to_append["value"] = v
                    data_list.append(to_append)
                item_dict["data"] = data_list
            return item_dict

    class Link(BaseCollectionItem):
        """
        A class for storing data representing an individual Collection+JSON Link (stored in the links property)
        """

        def __init__(self, uri, rel, name=None, render=None, prompt=None):
            self.uri = uri
            self.rel = rel
            if name is not None:
                self.name = name
            if render is not None:
                self.render = render
            if prompt is not None:
                self.prompt = prompt
            try:
                # Python 3
                super().__init__()
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.BaseCollectionItem, self).__init__()

    class Query(Item):
        """
        A class for storing data representing an individual Collection+JSON Query (stored in the queries property)
        """

        def __init__(self, uri, rel=None, prompt=None, **kwargs):
            self.uri = uri
            if rel is not None:
                self.rel = rel
            if prompt is not None:
                self.prompt = prompt
            try:
                # Python 3
                super().__init__(**kwargs)
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.Query, self).__init__(**kwargs)

    class Template(Item):
        """
        A class for storing data representing the Collection+JSON template property
        """

        def __init__(self, **kwargs):
            try:
                # Python 3
                super().__init__(**kwargs)
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.Template, self).__init__(**kwargs)

    def __init__(self, version: str="1.0", href: str="/api/", **kwargs):
        """
        CollectionPlusJSON constructor.
        :type href: str
        :type version: str
        :param version: The CollectionPlusJSON standard being used, defaults to "1.0"
        :param href: The api base URI, defaults to "/api/"
        :param kwargs: Other properties to add, may include standard optional properties or extensions.
        :return:
        """
        collection = {
            'version': version,
            'href': href,
        }
        try:
            # Python 3
            super().__init__(**collection)
        except TypeError:
            # Python 2
            super(CollectionPlusJSON, self).__init__(**collection)
        # Using this method to invoke custom __setitem__ to verify types
        for k, v in kwargs.items():
            self[k] = v

    def __str__(self):
        return json.dumps({'collection': self.data}, cls=CollectionPlusJSON.CollectionPlusJSONEncoder)

    def __repr__(self):
        return self.__str__()

    def __setitem__(self, key, value):
        type_map = {
            'links': list,
            'items': list,
            'queries': list,
            'template': self.Template,
            'error': self.Error
        }
        list_content_types = {
            'links': self.Link,
            'items': self.Item,
            'queries': self.Query
        }
        if key in type_map.keys():
            if not isinstance(value, type_map[key]):
                raise TypeError(
                    '{key} must be an instance of {classname}'.format(key=key, classname=str(type_map[key]))
                )
            if key in list_content_types.keys():
                for item in value:
                    if not isinstance(item, list_content_types[key]):
                        raise TypeError(
                            '{key}[{index}] is not an instance of {classname}'.format(
                                key=key,
                                index=value.index(item),
                                classname=str(list_content_types[key]))
                        )

        super().__setitem__(key, value)

    def append_item(self, item):
        """
        Append an item to this collection's 'items' property.
        :type item: CollectionPlusJSON.Item
        :param item: The Item to append.
        :return:
        """
        if not isinstance(item, self.Item):
            raise TypeError('item must be an instance of {classname}'.format(classname=str(self.Item)))
        else:
            if self.data.get('items') is not None:
                self.data.get('items').append(item)
            else:
                self.data['items'] = [item]

    def append_link(self, link):
        """
        Append a link to this collection's 'links' property.
        :type link: CollectionPlusJSON.Link
        :param link: The Link to append.
        :return:
        """
        if not isinstance(link, self.Link):
            raise TypeError('item must be an instance of {classname}'.format(classname=str(self.Link)))
        else:
            if self.data.get('links') is not None:
                self.data.get('links').append(link)
            else:
                self.data['links'] = [link]

    def append_query(self, query):
        """
        Append a query to this collection's 'queries' property.
        :type query: CollectionPlusJSON.Query
        :param query: The Query to append.
        :return:
        """
        if not isinstance(query, self.Query):
            raise TypeError('item must be an instance of {classname}'.format(classname=str(self.Query)))
        else:
            if self.data.get('queries') is not None:
                self.data.get('queries').append(query)
            else:
                self.data['queries'] = [query]

    def paginate(self, endpoint: str='', uri_template: str='{endpoint_uri}?page={page}&per_page={per_page}',
                 per_page: int=5, leading: int=2, trailing: int=2):
        """
        Paginate this collection into a list of collections representing "pages" of this collection.
        :type endpoint: str
        :type uri_template: str
        :type per_page: int
        :type leading: int
        :type trailing: int
        :param endpoint: The URI for this resource.
        :param uri_template: A string providing a template for paginated URI structure. May include the following keys:
            "{endpoint_uri}" - This will evaluate to the value of the 'endpoint' param.
            "{page}" - The page number will be inserted here.
            "{per_page}" - The number of items to display per page will be inserted here.
        :param per_page: The number of items per page for this representation.
        :param leading: The number of leading pages before a page to add to its "links".
        :param trailing: The number of trailing pages after a page to add to its "links".
        :return list: A list of CollectionPlusJSON instances representing this collection
        """

        # TODO: re-add ability to get specific page
        # TODO: page 2 links are first, prev, 2, 1, self, next, last; page 3 are f, p, 3, 2, self, n, l; etc.

        if type(per_page) is not int:
            try:
                per_page = abs(int(per_page))
            except (ValueError, TypeError):
                per_page = 5
            if not per_page:
                per_page = 5

        pages = []
        page = 1
        number_of_pages = int(_ceil(len(self.data.get('items')) / per_page))

        while page <= number_of_pages:
            page_index_begin = ((page * per_page) - per_page)
            page_index_end = (page * per_page)
            new_page = CollectionPlusJSON(href=self.data.get('href'),
                                          items=self.data.get('items')[page_index_begin:page_index_end])

            if page > 1:
                new_page.append_link(new_page.Link(
                    uri_template.format(endpoint_uri=endpoint, page=1, per_page=per_page),
                    'first',
                    prompt='First'
                ))
    
                new_page.append_link(new_page.Link(
                    uri_template.format(endpoint_uri=endpoint, page=(page - 1), per_page=per_page),
                    'prev',
                    prompt='Previous'
                ))
    
                if page - leading > 0:
                    new_page.append_link(new_page.Link(
                        '',
                        'skip',
                        prompt='&hellip;'
                    ))
    
                for lead_page in range(leading):
                    page_num = page - lead_page
                    if page_num > 0:
                        new_page.append_link(new_page.Link(
                            uri_template.format(endpoint_uri=endpoint, page=page_num, per_page=per_page),
                            'more',
                            prompt=str(page_num)
                        ))
    
            new_page.append_link(new_page.Link(
                uri_template.format(endpoint_uri=endpoint, page=page, per_page=per_page),
                'self',
                prompt=str(page)
            ))
    
            if page < number_of_pages:
                for trail_page in range(1, trailing + 1):
                    page_num = page + trail_page
                    if page_num < number_of_pages:
                        new_page.append_link(new_page.Link(
                            uri_template.format(endpoint_uri=endpoint, page=page_num, per_page=per_page),
                            'more',
                            prompt=str(page_num)
                        ))
    
                if page + leading < number_of_pages:
                    new_page.append_link(new_page.Link(
                        '',
                        'skip',
                        prompt='&hellip;'
                    ))
    
                if page < number_of_pages:
                    new_page.append_link(new_page.Link(
                        uri_template.format(endpoint_uri=endpoint, page=page + 1, per_page=per_page),
                        'next',
                        prompt='Next'
                    ))
    
                    new_page.append_link(new_page.Link(
                        uri_template.format(endpoint_uri=endpoint, page=number_of_pages, per_page=per_page),
                        'last',
                        prompt='Last'
                    ))

            pages.append(new_page)
            page += 1

        return tuple(pages)