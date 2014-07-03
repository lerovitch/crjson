# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import unittest
from io import BytesIO
from decimal import Decimal
import threading
import contextlib
from importlib import import_module

from crjson import common
from crjson.backends import yajl2
from crjson.compat import IS_PY2
from crjson.utils import coroutine


JSON = b'''
{
  "docs": [
    {
      "string": "\\u0441\\u0442\\u0440\\u043e\\u043a\\u0430 - \xd1\x82\xd0\xb5\xd1\x81\xd1\x82",
      "null": null,
      "boolean": false,
      "integer": 0,
      "double": 0.5,
      "exponent": 1.0e+2,
      "long": 10000000000
    },
    {
      "meta": [[1], {}]
    },
    {
      "meta": {"key": "value"}
    },
    {
      "meta": null
    }
  ]
}
'''
SCALAR_JSON = b'0'
EMPTY_JSON = b''
INVALID_JSON = b'{"key": "value",}'
INCOMPLETE_JSON = b'"test'
STRINGS_JSON = br'''
{
    "str1": "",
    "str2": "\"",
    "str3": "\\",
    "str4": "\\\\"
}
'''
LIST_JSON = b'[{"id": 5}, {"id": 6}, {"id": 7}]'

class Parse(object):
    '''
    Base class for parsing tests that is used to create test cases for each
    available backends.
    '''

    @coroutine
    def sink(self, rs):
        try:
            while True:
                data = (yield)
                rs.append(data)
        except GeneratorExit:
            pass

    def test_basic_parse(self):
        events = []
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                parser.send(BytesIO(JSON).read())
        
        reference = [
            ('start_map', None),
                ('map_key', 'docs'),
                ('start_array', None),
                    ('start_map', None),
                        ('map_key', 'string'),
                        ('string', 'строка - тест'),
                        ('map_key', 'null'),
                        ('null', None),
                        ('map_key', 'boolean'),
                        ('boolean', False),
                        ('map_key', 'integer'),
                        ('number', 0),
                        ('map_key', 'double'),
                        ('number', Decimal('0.5')),
                        ('map_key', 'exponent'),
                        ('number', Decimal('100')),
                        ('map_key', 'long'),
                        ('number', 10000000000),
                    ('end_map', None),
                    ('start_map', None),
                        ('map_key', 'meta'),
                        ('start_array', None),
                            ('start_array', None),
                                ('number', 1),
                            ('end_array', None),
                            ('start_map', None),
                            ('end_map', None),
                        ('end_array', None),
                    ('end_map', None),
                    ('start_map', None),
                        ('map_key', 'meta'),
                        ('start_map', None),
                            ('map_key', 'key'),
                            ('string', 'value'),
                        ('end_map', None),
                    ('end_map', None),
                    ('start_map', None),
                        ('map_key', 'meta'),
                        ('null', None),
                    ('end_map', None),
                ('end_array', None),
            ('end_map', None),
        ]
        for e, r in zip(events, reference):
            self.assertEqual(e, r)

    def test_basic_parse_threaded(self):
        thread = threading.Thread(target=self.test_basic_parse)
        thread.start()
        thread.join()


    def test_scalar(self):
        events = []
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                parser.send(BytesIO(SCALAR_JSON).read())
        self.assertEqual(events, [('number', 0)])

    def test_strings(self):
        events = []
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                parser.send(BytesIO(STRINGS_JSON).read())
        strings = [value for event, value in events if event == 'string']
        self.assertEqual(strings, ['', '"', '\\', '\\\\'])

    def test_empty(self):
        events = []
        with self.assertRaises(common.IncompleteJSONError):
            with contextlib.closing(self.sink(events)) as sink_cr:
                with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                    parser.send(EMPTY_JSON)

    def test_i_items(self):
        events = []
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(self.backend.items('item', sink_cr)) as parser:
                parser.send(LIST_JSON[:len(LIST_JSON) / 2])
                self.assertEqual([{'id': 5}], events)
                parser.send(LIST_JSON[len(LIST_JSON) / 2:])
            self.assertEqual([{'id': 5}, {'id': 6}, {'id': 7}], events)

    def test_incomplete(self):
        events = []
        with self.assertRaises(common.IncompleteJSONError):
            with contextlib.closing(self.sink(events)) as sink_cr:
                with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                    parser.send(INCOMPLETE_JSON)

    def test_invalid(self):
        events = []
        with self.assertRaises(common.JSONError):
            with contextlib.closing(self.sink(events)) as sink_cr:
                with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                    parser.send(INVALID_JSON)
 
    def test_utf8_split(self):
        events = []
        buf_size = JSON.index(b'\xd1') + 1
        try:
            with contextlib.closing(self.sink(events)) as sink_cr:
                with contextlib.closing(self.backend.basic_parse(sink_cr)) as parser:
                    parser.send(JSON[:buf_size])
                    parser.send(JSON[buf_size:])
        except UnicodeDecodeError:
            self.fail('UnicodeDecodeError raised')


# Generating real TestCase classes for each importable backend
#for name in ['python', 'yajl']:
for name in ['yajl2', 'yajl']:
    try:
        classname = '%sParse' % name.capitalize()
        if IS_PY2:
            classname = classname.encode('ascii')
        locals()[classname] = type(
            classname,
            (unittest.TestCase, Parse),
            {'backend': import_module('crjson.backends.%s' % name)},
        )
    except ImportError:
        pass


class Common(unittest.TestCase):
    '''
    Backend independent tests. They all use basic_parse imported explicitly from
    the python backend to generate parsing events.
    '''

    @coroutine
    def sink(self, rs):
        try:
            while True:
                data = (yield)
                rs.append(data)
        except GeneratorExit:
            pass

    def test_object_builder(self):
        builder = common.ObjectBuilder()

        events = []
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(yajl2.basic_parse(sink_cr)) as parser:
                parser.send(BytesIO(JSON).read())

        for event, value in events:
            builder.event(event, value)
        self.assertEqual(builder.value, {
            'docs': [
                {
                   'string': 'строка - тест',
                   'null': None,
                   'boolean': False,
                   'integer': 0,
                   'double': Decimal('0.5'),
                   'exponent': Decimal('100'),
                   'long': 10000000000,
                },
                {
                    'meta': [[1], {}],
                },
                {
                    'meta': {'key': 'value'},
                },
                {
                    'meta': None,
                },
            ],
        })

    def test_scalar_builder(self):
        events = []
        builder = common.ObjectBuilder()
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(yajl2.basic_parse(sink_cr)) as parser:
                parser.send(SCALAR_JSON)

        for event, value in events:
            builder.event(event, value)
        self.assertEqual(builder.value, 0)

    def test_parse(self):
        events = []
        builder = common.ObjectBuilder()
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(yajl2.parse(sink_cr)) as parser:
                parser.send(JSON)

        events = [value
            for prefix, event, value in events
            if prefix == 'docs.item.meta.item.item'
        ]
        self.assertEqual(events, [1])

    def test_items(self):
        events = []
        with contextlib.closing(self.sink(events)) as sink_cr:
            with contextlib.closing(yajl2.items('docs.item.meta', sink_cr)) as parser:
                parser.send(JSON)

        self.assertEqual(events, [
            [[1], {}],
            {'key': 'value'},
            None,
        ])

 
if __name__ == '__main__':
    unittest.main()
