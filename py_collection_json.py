__author__ = 'Ian S. Evans'

import json
from collections import UserDict
from math import ceil

MIMETYPE = 'application/vnd.collection+json'

# TODO: Amend both classes to allow for easier conformity to Collection+JSON standard


class CollectionPlusJSON(UserDict):

    mimetype = MIMETYPE

    class Error(object):
        pass

    class Item(UserDict):

        # TODO: Needs name, value, prompt support for 'data' property

        def __init__(self, uri=None, links=None, **kwargs):
            if uri is not None:
                self.href = uri
            if links is not None:
                self.links = links
            for k, v in kwargs:
                if not isinstance(v, str):
                    if not hasattr(v, "__getitem__"):
                        raise TypeError("{key} must have ")

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

        def __repr__(self):
            return self.__str__()

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

    def append_item(self, uri, data):
        """
        Append an item to this collection's 'items' property.
        :param uri: A string representing this resource's URI.
        :param data: This resource representation's data, as a dict or
        :return:
        """
        item = self.CollectionPlusJSONItem(uri=uri, **data)
        if self.data.get('items') is not None:
            self.data.get('items').append(item)
        else:
            self.data['items'] = [item]

    def append_link(self, uri, rel, **kwargs):
        """
        Append a link to this collection's 'links' property.
        :param uri: A string representing the link's URI.
        :param rel: The link's relationship to this resource.
        :param prompt: The prompt to optionally display for this link.
        :return:
        """
        link = {'href': uri, 'rel': rel}
        link = dict(link, **kwargs)
        if self.data.get('links') is not None:
            self.data.get('links').append(link)
        else:
            self.data['links'] = [link]

    def append_query(self, uri, rel, prompt, data):
        query = {'href': uri, 'rel': rel, 'prompt': prompt, 'data': data}
        if self.data.get('query') is not None:
            self.data.get('query').append(query)
        else:
            self.data['query'] = [query]

    def error(self, title, code, message):
        """
        Set the error object for this collection.
        :param title: The title string for the error.
        :param code: The error code for the error.
        :param message: The long-form message explaining the error and/or its meaning.
        :return:
        """
        pass

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
