__author__ = 'Ian S. Evans'
__version__ = '0.0.4'

from json import dumps, JSONEncoder, loads
from collections import UserList


class Comparable(object):
    # Stolen shamelessly from Ricardo Kirkner's bindings
    # See https://github.com/ricardokirkner/collection-json.python

    def __init__(self, *args, **kwargs):
        super(Comparable, self).__init__()

    def __eq__(self, other):
        if type(self) == type(other) and self.__dict__ == other.__dict__:
            return True
        return False

    def __ne__(self, other):
        if type(self) != type(other) or self.__dict__ != other.__dict__:
            return True
        return False


class RequiresProperties(object):
    """
    Abstract class for classes that require certain properties to exist and be of certain types.
    """

    __should__ = {}

    def __setattr__(self, key, value):
        if key in self.__should__:
            if not isinstance(value, self.__should__[key]["type"]):
                raise TypeError(
                    "The value of {k} must be a {type}.".format(
                        cls=self.__class__.__name__, k=key, type=self.__should__[key]["type"].__name__
                    )
                )
            if self.__should__[key]["truthy"]:
                if not value:
                    raise TypeError(
                        "The value of {k} cannot evaluate to False.".format(cls=self.__class__.__name__, k=key)
                    )
        super(RequiresProperties, self).__setattr__(key, value)


class Serializable(object):

    class Encoder(JSONEncoder):
        def default(self, o):
            if isinstance(o, Serializable):
                return o.get_serializable()
            return JSONEncoder.default(self, o)

    def __init__(self, *args, **kwargs):
        super(Serializable, self).__init__()

    def __repr__(self):
        value = " ".join(["{k}={v}".format(k=k, v=repr(v)) for k, v in self.__dict__.items()])
        return "<{classname} {value}>".format(classname=self.__class__.__name__, value=value)

    def __str__(self):
        return dumps(self, cls=self.Encoder)

    def get_serializable(self):
        serializable = {}
        for k, v in self.__dict__.items():
            if v:
                if isinstance(v, Serializable):
                    serializable[k] = v.get_serializable()
                else:
                    serializable[k] = v
        return serializable


class Array(Serializable, Comparable, UserList):

    def __init__(self, iterable=[], cls=object, *args, **kwargs):
        super(Array, self).__init__(self, iterable, *args, **kwargs)
        self.required_class = cls
        for item in iterable:
            if isinstance(item, cls):
                self.data.append(item)
            else:
                self.data.append(cls(**item))

    def __add__(self, other):
        if type(self) is type(other):
            if self.required_class == other.required_class:
                merged = self.data + other.data
                return Array(merged, self.required_class)
            else:
                raise TypeError(
                    "unsupported operand type(s) for +: 'Array[{self_type}]' and 'Array[{other_type}]'".format(
                        self_type=self.required_class.__name__, other_type=other.required_class.__name__
                    )
                )
        else:
            raise TypeError(
                "unsupported operand type(s) for +: 'Array' and '{other_type}'".format(other_type=type(other).__name__)
            )

    def __sub__(self, other):
        if type(self) is type(other):
            if self.required_class == other.required_class:
                modified = []
                for self_item in self.data:
                    if self_item not in other.data:
                        modified.append(self_item)
                return Array(modified, self.required_class)
            else:
                raise TypeError(
                    "unsupported operand type(s) for -: 'Array[{self_type}] and Array[{other_type}]'".format(
                        self_type=self.required_class.__name__, other_type=other.required_class.__name__
                    )
                )
        else:
            raise TypeError(
                "unsupported operand type(s) for -: 'Array' and '{other_type}'".format(other_type=type(other).__name__)
            )

    def __eq__(self, other):
        if type(self) == type(other) and \
                self.required_class == other.required_class and \
                self.data == other.data:
            return True
        return False

    def __ne__(self, other):
        if type(self) != type(other) or \
                self.required_class != other.required_class or \
                self.data != other.data:
            return True
        return False

    def __repr__(self):
        return UserList.__repr__(self)

    def append(self, item):
        if isinstance(item, self.required_class):
            super(Array, self).append(item)
        else:
            raise TypeError("item must be an instance of {type}".format(type=self.required_class.__name__))

    def get_serializable(self):
        data = []
        for item in self.data:
            if isinstance(item, Serializable):
                data.append(item.get_serializable())
            else:
                data.append(item)
        return data


class Collection(Serializable, RequiresProperties, Comparable):
    """
    { error, href, items, links, queries, template, version }
    """

    __mimetype = "application/vnd.collection+json"
    __should__ = {
        "href": {"type": str, "truthy": True},
        "version": {"type": str, "truthy": True}
    }

    @property
    def mimetype(self):
        return self.__mimetype

    def __init__(self, href=None, version="1.0", error=None, items=[],
                 links=[], queries=[], template=None, **kwargs):
        super(Collection, self).__init__()
        if not kwargs.get("from_json"):
            # Process like normal, apply restrictions to properties
            # from the standard, allow non-standard properties

            self.href = href
            self.version = version

            if error and not isinstance(error, Error):
                error = Error(**error)  # let the class raise exceptions if something's amiss
                self.error = error

            if template and not isinstance(template, Template):
                template = Template(**template)
                self.template = template

            if items and not isinstance(items, Array):
                items = Array(items, cls=Item)
            self.items = items

            if links and not isinstance(links, Array):
                links = Array(links, cls=Link)
            self.links = links

            if queries and not isinstance(queries, Array):
                queries = Array(queries, cls=Query)
            self.queries = queries

            for k, v in kwargs.items():
                # let the user set whatever non-standard data
                # no warranty, express or implied that non-standard
                # data will behave correctly or as expected
                self.__setattr__(k, v)

        else:
            # TODO: allow any kind of TextIO?
            from_json = kwargs.get("from_json")
            if isinstance(from_json, str):
                self.__init__(**loads(kwargs.get("from_json")))

    def __setattr__(self, key, value):

        if key == "error":
            if not isinstance(value, Error):
                value = Error(**value)

        elif key == "template":
            if not isinstance(value, Template):
                value = Template(**value)

        elif key == "items":
            if not isinstance(value, Array):
                value = Array(value, cls=Item)

        elif key == "links":
            if not isinstance(value, Array):
                value = Array(value, cls=Link)

        elif key == "queries":
            if not isinstance(value, Array):
                value = Array(value, cls=Query)

        super(Collection, self).__setattr__(key, value)

    def get_serializable(self):
        return {"collection": super(Collection, self).get_serializable()}


class Data(Serializable, RequiresProperties, Comparable):
    """
    { name, prompt, value }
    """

    __should__ = {"name": {"type": str, "truthy": True}}

    def __init__(self, name=None, prompt=None, value=None, **kwargs):

        super(Data, self).__init__()

        self.name = name
        self.prompt = prompt
        self.value = value

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Error(Serializable, Comparable):
    """
    { code, message, title }
    """
    def __init__(self, code=None, message=None, title=None, **kwargs):

        super(Error, self).__init__()

        self.code = code
        self.message = message
        self.title = title

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Item(Serializable, RequiresProperties, Comparable):
    """
    { data, href, links }
    """

    __should__ = {"href": {"type": str, "truthy": True}}

    def __init__(self, href=None, data=[], links=[], **kwargs):

        super(Item, self).__init__()

        self.href = href

        if not isinstance(data, Array):
            data = Array(data, cls=Data)
        self.data = data

        if not isinstance(links, Array):
            links = Array(links, cls=Link)
        self.links = links

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Link(Serializable, RequiresProperties, Comparable):
    """
    { href, name, prompt, rel, render }
    """

    __should__ = {
        "href": {"type": str, "truthy": True},
        "rel": {"type": str, "truthy": True}
    }

    def __init__(self, href=None, rel=None, name=None, prompt=None, render=None, **kwargs):

        super(Link, self).__init__()

        self.href = href
        self.rel = rel
        self.name = name
        self.prompt = prompt
        self.render = render

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Query(Serializable, RequiresProperties, Comparable):
    """
    { data, href, name, prompt, rel }
    """

    __should__ = {
        "href": {"type": str, "truthy": True},
        "rel": {"type": str, "truthy": True}
    }

    def __init__(self, href=None, rel=None, data=None, name=None, prompt=None, **kwargs):

        super(Query, self).__init__()

        self.href = href
        self.rel = rel
        self.name = name
        self.prompt = prompt

        if not isinstance(data, Array):
            data = Array(data, cls=Data)
        self.data = data

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Template(Serializable, RequiresProperties, Comparable):
    """
    { data }
    """

    __should__ = {"data": {"type": (list, UserList), "truthy": False}}

    def __init__(self, data=[], **kwargs):

        super(Template, self).__init__()

        if not isinstance(data, Array):
            data = Array(data, cls=Data)
        self.data = data

        for k, v in kwargs.items():
            self.__setattr__(k, v)

