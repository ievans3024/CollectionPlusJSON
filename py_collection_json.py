__author__ = 'Ian S. Evans'

import json
from collections import UserDict
from math import ceil

MIMETYPE = 'application/vnd.collection+json'


class CollectionPlusJSON(UserDict):

    mimetype = MIMETYPE

    class CollectionPlusJSONItem(UserDict):

        def __init__(self, uri=None, **kwargs):
            if uri is not None:
                self.href = uri
            try:
                # Python 3
                super().__init__(**kwargs)
            except TypeError:
                # Python 2
                super(CollectionPlusJSON.CollectionPlusJSONItem, self).__init__(**kwargs)

        def __str__(self):
            return json.dumps(self.__dict__)

        __repr__ = __str__

    def __init__(self, version=1.0, href='/api/', items=[], links=[], error={},
                 queries=[
                     {
                         'href': '/api/search/',
                         'rel': 'search',
                         'prompt': 'Find a specific entry',
                         'data': [{'name': 'query', 'value': ''}]
                     }
                 ],
                 template={
                     'data': []
                 }, **kwargs):
        collection = {
            'version': str(version),
            'href': href,
            'items': items,
            'links': links,
            'queries': queries,
            'template': template,
            'error': error
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

    __repr__ = __str__

    def append_item(self, uri, data):
        """
        Append an item to this collection's 'items' property.
        :param uri: A string representing this resource's URI.
        :param data: This resource representation's data, as a dict or
        :return:
        """
        item = CollectionPlusJSON.CollectionPlusJSONItem(uri=uri, **data)
        self.data.get('items').append(item)

    def append_link(self, uri, rel, prompt):
        """
        Append a link to this collection's 'links' property.
        :param uri: A string representing the link's URI.
        :param rel: The link's relationship to this resource.
        :param prompt: The prompt to optionally display for this link.
        :return:
        """
        self.data.get('links').append({'href': uri, 'rel': rel, 'prompt': prompt})

    def paginate(self, endpoint='', uri_template='{endpoint_uri}?page={page}&per_page={per_page}', page=1, per_page=5,
                 leading=2, trailing=2):
        """
        Paginate this collection, automatically trimming items and adding appropriate links for navigation.
        :param uri_template: A string providing a template for paginated URI structure. May include the following keys:
        "{endpoint_uri}" - This will evaluate to the value of the 'endpoint' param.
        "{page}" - The page number will be inserted here.
        "{per_page}" - The number of items to display per page will be inserted here.
        :param endpoint: The URI for this resource.
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

    def remove_links(self, operator='and', **kwargs):
        if operator.lower() == 'or':
            if self.data.get('links') is not None:
                self.data['links'] = [
                    link for link in self.data.get('links') if not bool(
                        set(kwargs.items()).intersection(set(link.items()))
                    )
                ]
        elif operator.lower() == 'and':
            if self.data.get('links') is not None:
                self.data['links'] = [
                    link for link in self.data.get('links') if not all(
                        link.get(k) == v for k, v in kwargs.items() if k in link
                    )
                ]
        else:
            raise ValueError('operator must be "and" or "or"')
