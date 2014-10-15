__author__ = 'Ian S. Evans'

import json
from collections import UserDict
from math import ceil

MIMETYPE = 'application/vnd.collection+json'


class CollectionPlusJSON(UserDict):

    mimetype = MIMETYPE

    class BaseCollectionItem(object):

        def __init__(self, *args, **kwargs):
            pass

        def __str__(self):
            return json.dumps(self.__dict__)

        def __repr__(self):
            return self.__str__()

    class Error(BaseCollectionItem):

        def __init__(self, title=None, code=None, message=None):
            if title is not None:
                self.title = title
            if code is not None:
                self.code = code
            if message is not None:
                self.message = message

    class Item(UserDict, BaseCollectionItem):

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
            item_dict = dict(self.__dict__)
            if self.data:
                data_list = []
                for k, v in self.data.items():
                    to_append = {"name": k}
                    if not isinstance(v, str):
                        to_append["value"] = v[0]
                        to_append["prompt"] = v[1]
                    else:
                        to_append['value'] = v
                    data_list.append(to_append)
                item_dict['data'] = data_list
            return json.dumps(item_dict)

    class Link(BaseCollectionItem):

        def __init__(self, uri, rel, name=None, render=None, prompt=None):
            self.uri = uri
            self.rel = rel
            if name is not None:
                self.name = name
            if render is not None:
                self.render = render
            if prompt is not None:
                self.prompt = prompt

    class Query(Item):

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

        def __init__(self, **kwargs):
            try:
                # Python 3
                super().__init__(**kwargs)
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.Template, self).__init__(**kwargs)

    def __init__(self, version=1.0, href='/api/', **kwargs):
        collection = {
            'version': str(version),
            'href': href,
        }
        collection = dict(collection, **kwargs)  # zip together standard collection + extended properties
        try:
            # Python 3
            super().__init__(**collection)
        except TypeError:
            # Python 2
            super(CollectionPlusJSON, self).__init__(**collection)

    def __str__(self):
        return json.dumps({'collection': self.data})

    def __repr__(self):
        return self.__str__()

    def __setitem__(self, key, value):
        type_map = {
            'links': self.Link,
            'items': self.Item,
            'queries': self.Query,
            'template': self.Template,
            'error': self.Error
        }
        if key in type_map.keys():
            if not isinstance(value, type_map[key]):
                raise TypeError(
                    '{key} must be an instance of {classname}'.format(key=key, classname=str(type_map[key]))
                )
            if key in {'links', 'items', 'queries'}:
                self.data[key].append(value)
            else:
                self.data[key] = value
        else:
            self.data[key] = value

    def paginate(self, endpoint='', uri_template='{endpoint_uri}?page={page}&per_page={per_page}', page=1, per_page=5,
                 leading=2, trailing=2):
        """
        Paginate this collection, automatically trimming items and adding appropriate links for navigation.
        :param endpoint: The URI for this resource.
        :param uri_template: A string providing a template for paginated URI structure. May include the following keys:
        "{endpoint_uri}" - This will evaluate to the value of the 'endpoint' param.
        "{page}" - The page number will be inserted here.
        "{per_page}" - The number of items to display per page will be inserted here.
        :param page: The desired page for this representation.
        :param per_page: The number of items per page for this representation.
        :param leading: The number of leading pages before "this" page to add to this collection's "links".
        :param trailing: The number of trailing pages after "this" page to add to this collection's "links".
        :return:
        """
        if (type(page) is not int) or (type(per_page) is not int):

            try:
                page = abs(int(page))
            except (ValueError, TypeError):
                page = 1

            try:
                per_page = abs(int(per_page))
            except (ValueError, TypeError):
                per_page = 5

            if not page:
                page = 1
            if not per_page:
                per_page = 5

        number_of_pages = int(ceil(len(self.data.get('items')) / per_page))

        if page > number_of_pages:
            page = number_of_pages

        page_index_begin = ((page * per_page) - per_page)
        page_index_end = (page * per_page)

        self.data['items'] = self.data.get('items')[page_index_begin:page_index_end]

        if page > 1:
            self.append_link(
                uri_template.format(endpoint_uri=endpoint, page=1, per_page=per_page),
                'first',
                'First'
            )

            self.append_link(
                uri_template.format(endpoint_uri=endpoint, page=(page - 1), per_page=per_page),
                'prev',
                'Previous'
            )

            if page - leading > 0:
                self.append_link(
                    '',
                    'skip',
                    '&hellip;'
                )

            for lead_page in range(leading):
                page_num = page - lead_page
                if page_num > 0:
                    self.append_link(
                        uri_template.format(endpoint_uri=endpoint, page=page_num, per_page=per_page),
                        'more',
                        str(page_num)
                    )

        self.append_link(
            uri_template.format(endpoint_uri=endpoint, page=page, per_page=per_page),
            'self',
            str(page)
        )

        if page < number_of_pages:
            for trail_page in range(1, trailing + 1):
                page_num = page + trail_page
                if page_num < number_of_pages:
                    self.append_link(
                        uri_template.format(endpoint_uri=endpoint, page=page_num, per_page=per_page),
                        'more',
                        str(page_num)
                    )

            if page + leading < number_of_pages:
                self.append_link(
                    '',
                    'skip',
                    '&hellip;'
                )

            if page < number_of_pages:
                self.append_link(
                    uri_template.format(endpoint_uri=endpoint, page=page + 1, per_page=per_page),
                    'next',
                    'Next'
                )

                self.append_link(
                    uri_template.format(endpoint_uri=endpoint, page=number_of_pages, per_page=per_page),
                    'last',
                    'Last'
                )
