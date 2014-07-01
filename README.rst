=====
ijson
=====

Ijson is an iterative JSON parser using Python couroutines interface.

It is a fork from  `Ivan Sagalaev <https://github.com/isagalaev>` library that justs rethinks the 
flow from a generator library to a coroutine library.

The main point of it is to allowing better integration with long results


Usage
=====

All usage example will be using a JSON document describing geographical
objects::

    {
      "earth": {
        "europe": [
          {"name": "Paris", "type": "city", "info": { ... }},
          {"name": "Thames", "type": "river", "info": { ... }},
          // ...
        ],
        "america": [
          {"name": "Texas", "type": "state", "info": { ... }},
          // ...
        ]
      }
    }

Most common usage is having ijson yield native Python objects out of a JSON
stream located under a prefix. Here's how to process all European cities::

    import ijson
    import contextlib

    @ijson.util    
    def sink(rs):
        try:
            while True:
                data = (yield)
                rs.append(data)
        except GeneratorExit:
            pass

    def reader(fp, target):
        while True:
            data = fp.read()
            if not data:
                break
            target.send(data)

    objects = []

    from io import BytesIO
    f = BytesIO(b'''    {
              "earth": {
                "europe": [
            {"name": "Paris", "type": "city", "info": { "more": 1}},
            {"name": "Thames", "type": "river", "info": { "more": 2}}
                ],
                "america": [
            {"name": "Texas", "type": "state", "info": { "more": 3}}
                ]
              }
            }
        ''')

    with contextlib.closing(sink(objects)) as sink_cr:
        with contextlib.closing(ijson.items('earth.europe.item', sink_cr)) as parser:
            reader(f, parser)

    cities = (o for o in objects if o['type'] == 'city')
        for city in cities:
            print city


Backends
========

Ijson provides several implementations of the actual parsing in the form of
backends located in ijson/backends:

- ``yajl2``: wrapper around `YAJL <http://lloyd.github.com/yajl/>`_ version 2.x
- ``yajl``: wrapper around `YAJL <http://lloyd.github.com/yajl/>`_ version 1.x

You can import a specific backend and use it in the same way as the top level
library::

    import ijson.backends.yajl as ijson

    for item in ijson.items(...):
        # ...

Importing the top level library as ``import ijson`` tries to import all backends
in order, so it either finds an appropriate version of YAJL.


Acknowledgements
================

Python parser in ijson is relatively simple thanks to `Douglas Crockford
<http://www.crockford.com/>`_ who invented a strict, easy to parse syntax.

The `YAJL <http://lloyd.github.com/yajl/>`_ library by `Lloyd Hilaiel
<http://lloyd.io/>`_ is the most popular and efficient way to parse JSON in an
iterative fashion.

Ijson was inspired by `yajl-py <http://pykler.github.com/yajl-py/>`_ wrapper by
`Hatem Nassrat <http://www.nassrat.ca/>`_. Though ijson borrows almost nothing
from the actual yajl-py code it was used as an example of integration with yajl
using ctypes.
