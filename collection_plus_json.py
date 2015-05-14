__author__ = 'Ian S. Evans'
__version__ = '0.0.4'

from json import dumps, JSONEncoder, loads
from collections import UserList

MIMETYPE = "application/vnd.collection+json"


class Comparable(object):
    """
    An object that needs to be comparable.
    Stolen shamelessly from Ricardo Kirkner's bindings
    See https://github.com/ricardokirkner/collection-json.python
    """

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


class CollectionField(object):

    def __init__(self, cls, truthy=False, nullable=True):
        # have to double on type call to catch meta classes
        if isinstance(cls, type):
            raise TypeError("Parameter 'cls' must be a class. type(type(cls)) -> {cls}".format(cls=str(type(cls))))
        self.cls = cls
        self.truthy = truthy
        if not truthy:
            self.nullable = nullable
        else:
            self.nullable = False

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return instance.__dict__.get(self.get_own_name(owner))

    def __set__(self, instance, value):
        if (not value) and self.truthy:
            raise ValueError("Value must be truthy (cannot evaluate to False.)")
        if value is None:
            if not self.nullable:
                raise ValueError("Value cannot be None.")
        elif not isinstance(value, self.cls):
            raise TypeError("Value must be an instance of {cls}.".format(cls=self.cls.__name__))
        instance.__dict__[self.get_own_name(type(instance))] = value

    def __delete__(self, instance):
        if not self.nullable:
            raise ValueError("{name} cannot be deleted.".format(name=self.get_own_name(type(instance))))
        del instance.__dict__[self.get_own_name(type(instance))]

    def get_own_name(self, owner):
        for attr in dir(owner):
            if getattr(owner, attr) is self:
                return attr


class CollectionArrayField(CollectionField):

    def __init__(self, cls, contains=object, truthy=False, nullable=True):
        super().__init__(cls, truthy=truthy, nullable=nullable)
        if isinstance(contains, type):
            raise TypeError("Parameter 'contains' must be a class.")
        self.contains = contains

    def __set__(self, instance, value):
        if (not value) and self.truthy:
            raise ValueError("Value must be truthy (cannot evaluate to False.)")
        if value is None:
            if not self.nullable:
                raise ValueError("Value cannot be None.")
        elif not isinstance(value, self.cls):
            raise TypeError("Value must be an instance of {cls}.".format(cls=self.cls.__name__))
        if not all([isinstance(i, self.contains) for i in value]):
            raise TypeError("Value must contain instances of {cls}".format(cls=self.contains.__name__))
        instance.__dict__[self.get_own_name(type(instance))] = value


class RequiresProperties(object):
    """
    Abstract class for classes that require certain properties to exist and be of certain types.
    """
    # TODO: delete me once descriptors prove bug-free

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
    """
    An object that needs to be JSON serializable.
    """

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
    """
    A serializable, comparable list-like object that contains objects of a certain type.
    See: http://amundsen.com/media-types/collection/format/#arrays
    """

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

    def get(self, **kwargs):
        """
        Find the first contained object that matches certain criteria
        :param kwargs: Keyword arguments for property name:value pairs to match
        :returns: object The first contained object found to match all the criteria, None if no match.
        """
        for obj in self.data:
            matches = all([v == obj.__dict__.get(k) for k, v in kwargs.items()])
            if matches:
                return obj
        return None

    def get_serializable(self):
        data = []
        for item in self.data:
            if isinstance(item, Serializable):
                data.append(item.get_serializable())
            else:
                data.append(item)
        return data

    def search(self, operator, *args, **kwargs):
        """
        Search for all contained objects that match certain criteria
        :param operator: Which logical operation to apply to search criteria (e.g. "and", "or")
        :param args: Arguments for property names to match (regardless of value)
        :param kwargs: Keyword arguments for property name:value pairs to match
        :returns: tuple All of the objects that match the criteria
        """
        operations = {
            "and": all,
            "or": any
        }

        if str(operator).lower() in operations:
            op = operations[operator]

        results = []
        for obj in self.data:
            has_props = op([k in obj.__dict__ for k in args])
            has_items = op([v == obj.__dict__.get(k) for k, v in kwargs.items()])
            if has_props or has_items:
                results.append(obj)
        return tuple(results)


class Data(Serializable, Comparable):
    """
    A dict-like object that contains some objects representing information about another object.
    Usually contained in an Array.
    See: http://amundsen.com/media-types/collection/format/#arrays-data
    """

    name = CollectionField(str, truthy=True)
    prompt = CollectionField(str)
    value = CollectionField(object)

    '''
    __should__ = {"name": {"type": str, "truthy": True}}
    '''

    def __init__(self, name=None, prompt=None, value=None, **kwargs):

        super(Data, self).__init__()

        self.name = name
        self.prompt = prompt
        self.value = value

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Error(Serializable, Comparable):
    """
    A dict-like object containing error information.
    See: http://amundsen.com/media-types/collection/format/#objects-error
    """

    code = CollectionField(str)
    message = CollectionField(str)
    title = CollectionField(str)

    def __init__(self, code=None, message=None, title=None, **kwargs):

        super(Error, self).__init__()

        self.code = code
        self.message = message
        self.title = title

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Link(Serializable, Comparable):
    """
    A dict-like object containing information representing something as related to something else.
    Usually contained in an Array.
    See: http://amundsen.com/media-types/collection/format/#arrays-links
    """

    href = CollectionField(str, truthy=True)
    rel = CollectionField(str, truthy=True)
    name = CollectionField(str)
    prompt = CollectionField(str)
    render = CollectionField(str)

    '''
    __should__ = {
        "href": {"type": str, "truthy": True},
        "rel": {"type": str, "truthy": True}
    }
    '''

    def __init__(self, href=None, rel=None, name=None, prompt=None, render=None, **kwargs):

        super(Link, self).__init__()

        self.href = href
        self.rel = rel
        self.name = name
        self.prompt = prompt
        self.render = render

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Query(Serializable, Comparable):
    """
    A dict-like object containing a form template related to the type of objects in the collection.
    Usually contained in an Array.
    See: http://amundsen.com/media-types/collection/format/#arrays-queries
    """

    href = CollectionField(str, truthy=True)
    rel = CollectionField(str, truthy=True)
    name = CollectionField(str)
    prompt = CollectionField(str)

    '''
    __should__ = {
        "href": {"type": str, "truthy": True},
        "rel": {"type": str, "truthy": True}
    }
    '''

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


class Item(Serializable, Comparable):
    """
    A dict-like object containing information representing something.
    http://amundsen.com/media-types/collection/format/#arrays-items
    """

    href = CollectionField(str, truthy=True)
    data = CollectionArrayField(Array, contains=Data)
    links = CollectionArrayField(Array, contains=Link)

    '''
    __should__ = {"href": {"type": str, "truthy": True}}
    '''

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


class Template(Serializable, Comparable):
    """
    A dict-like object containing a template for objects in the containing collection.
    See: http://amundsen.com/media-types/collection/format/#objects-template
    """

    data = CollectionArrayField(Array, contains=Data)

    '''
    __should__ = {"data": {"type": (list, UserList), "truthy": False}}
    '''

    def __init__(self, data=[], **kwargs):

        super(Template, self).__init__()

        if not isinstance(data, Array):
            data = Array(data, cls=Data)
        self.data = data

        for k, v in kwargs.items():
            self.__setattr__(k, v)


class Collection(Serializable, Comparable):
    """
    A dict-like object that contains a collection of information.
    See: http://amundsen.com/media-types/collection/format/#objects-collection
    """

    __mimetype = MIMETYPE

    href = CollectionField(str, truthy=True)
    version = CollectionField(str, truthy=True)
    error = CollectionField(Error)
    template = CollectionField(Template)
    items = CollectionArrayField(Array, contains=Item)
    links = CollectionArrayField(Array, contains=Link)
    queries = CollectionArrayField(Array, contains=Query)
    '''
    __should__ = {
        "href": {"type": str, "truthy": True},
        "version": {"type": str, "truthy": True}
    }
    '''

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
        # Let folks supply dicts or lists when setting collection attributes

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
        return {"collection": self.get_serializable()}

