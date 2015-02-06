CollectionPlusJSON
====
Version: **0.0.4**

A module for packaging data as the Collection+JSON hypermedia type, for use in RESTful APIs.

This module provides a few classes and tools for structuring data to be packaged in JSON following the specification
proposed by Mike Amundsen and registered with IANA.

Some parts are copied from or based on ideas found in [Ricardo Kirkner's bindings](https://github.com/ricardokirkner/collection-json.python)

For more information on the hypermedia type, see Mike Amundsen's [Collection+JSON page](http://amundsen.com/media-types/collection/)

Changelog
====

0.0.4
----

* Removed support for python 2 because subclassing list is harder than subclassing UserList

0.0.3
----

* Complete rewrite based on some ideas from [Ricardo Kirkner's bindings](https://github.com/ricardokirkner/collection-json.python)

0.0.2
----

* Some bug fixes
* Added `page` parameter back to `.paginate()` to get a specific page.

0.0.1
----

* initial