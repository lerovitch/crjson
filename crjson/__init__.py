'''
Iterative JSON parser.

Main API:

- ``crjson.parse``: iterator returning parsing events with the object tree context,
  see ``crjson.common.parse`` for docs.

- ``crjson.items``: iterator returning Python objects found under a specified prefix,
  see ``crjson.common.items`` for docs.

Top-level ``crjson`` module tries to automatically find and import a suitable
parsing backend. You can also explicitly import a required backend from
``crjson.backends``.
'''

from crjson.common import JSONError, IncompleteJSONError, ObjectBuilder
from crjson.backends import YAJLImportError

import crjson.backends.yajl2 as backend


basic_parse = backend.basic_parse
parse = backend.parse
items = backend.items
