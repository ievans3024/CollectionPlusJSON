__author__ = 'Ian S. Evans'

import json


from math import ceil

COLLECTION_JSON = 'application/vnd.collection+json'


class CollectionPlusJSONItem(dict):

    def __contains__(self, item):
        if item in self.data:
            return True
        else:
            return False

    def __delitem__(self, key):
        del self.data[key]

    def __getitem__(self, item):
        return self.data[item]

    def __init__(self, uri=None, **kwargs):
        if uri is not None:
            self.href = uri
        self.data = kwargs
        super(CollectionPlusJSONItem, self).__init__(self.__dict__)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        return json.dumps(self)

    __repr__ = __str__

    def get(self, k, d=None):
        if k in self.data:
            return self.data[k]
        else:
            return d


class CollectionPlusJSON(dict):

    # TODO: Make this subclass a collection type with some fancy extras?

    mimetype = COLLECTION_JSON
    __CollectionPlusJSONItem = CollectionPlusJSONItem

    def __contains__(self, item):
        if item in self.collection:
            return True
        else:
            return False

    def __delitem__(self, key):
        del self.collection[key]

    def __getitem__(self, key):
        return self.collection[key]

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
                 }):
        # TODO: accept params to specify in collection?
        self.collection = {
            'version': str(version),
            'href': href,
            'items': items,
            'links': links,
            'queries': queries,
            'template': template,
            'error': error
        }
        super(CollectionPlusJSON, self).__init__(collection=self.collection)

    def __setitem__(self, key, value):
        self.collection[key] = value

    def __str__(self):
        return json.dumps(self.__dict__)

    __repr__ = __str__

    def append_item(self, item):
        if not (isinstance(item, CollectionPlusJSON.__CollectionPlusJSONItem)):
            raise TypeError('item must be a CollectionPlusJSONItem instance!')
        self.collection.get('items').append(item)

    def append_link(self, uri, rel, prompt):
        self.collection.get('links').append({'href': uri, 'rel': rel, 'prompt': prompt})

    def get(self, k, d=None):
        if k in self.collection:
            return self.collection[k]
        else:
            return d

    def paginate(self, uri_template='{endpoint_uri}?page={page}&per_page={per_page}', page=1, per_page=5, leading=2,
                 trailing=2):
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

        number_of_pages = int(ceil(len(self.collection.get('items')) / per_page))

        if page > number_of_pages:
            page = number_of_pages

        page_index_begin = ((page * per_page) - per_page)
        page_index_end = (page * per_page)

        self.collection['items'] = self.collection.get('items')[page_index_begin:page_index_end]

        if page > 1:
            self.append_link(
                uri_template.format(endpoint_uri=self.collection.get('href'), page=1, per_page=per_page),
                'first',
                'First'
            )

            self.append_link(
                uri_template.format(endpoint_uri=self.collection.get('href'), page=(page - 1),
                                    per_page=per_page),
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
                        uri_template.format(endpoint_uri=self.collection.get('href'), page=page_num,
                                            per_page=per_page),
                        'more',
                        str(page_num)
                    )

        self.append_link(
            uri_template.format(endpoint_uri=self.collection.get('href'), page=page,
                                per_page=per_page),
            'self',
            str(page)
        )

        if page < number_of_pages:
            for trail_page in range(1, trailing + 1):
                page_num = page + trail_page
                if page_num < number_of_pages:
                    self.append_link(
                        uri_template.format(endpoint_uri=self.collection.get('href'), page=page_num,
                                            per_page=per_page),
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
                    uri_template.format(endpoint_uri=self.collection.get('href'), page=page + 1,
                                        per_page=per_page),
                    'next',
                    'Next'
                )

                self.append_link(
                    uri_template.format(endpoint_uri=self.collection.get('href'), page=number_of_pages,
                                        per_page=per_page),
                    'last',
                    'Last'
                )

    def remove_links(self, operator='and', **kwargs):
        if operator.lower() == 'or':
            if self.collection.get('links') is not None:
                self.collection['links'] = [
                    link for link in self.collection.get('links') if not bool(
                        set(kwargs.items()).intersection(set(link.items()))
                    )
                ]
        elif operator.lower() == 'and':
            if self.collection.get('links') is not None:
                self.collection['links'] = [
                    link for link in self.collection.get('links') if not all(
                        link.get(k) == v for k, v in kwargs.items() if k in link
                    )
                ]
        else:
            raise ValueError('operator must be "and" or "or"')
