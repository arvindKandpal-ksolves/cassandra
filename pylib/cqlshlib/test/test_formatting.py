# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from collections import OrderedDict
from cqlshlib.displaying import NO_COLOR_MAP
from cqlshlib.formatting import (
    format_value_text,
    format_value_list,
    format_value_set,
    format_value_tuple,
    format_value_map,
    format_value_utype,
    CqlType
)


class _MockUDT:
    """Mimics the driver's UDT shape without namedtuple identifier restrictions."""
    def __init__(self, items):
        self._items = items

    def _asdict(self):
        return OrderedDict(self._items)


class TestBackslashEscaping(unittest.TestCase):
    """
    Tests for CASSANDRA-21131: format_value_text was doubling backslashes
    unconditionally. escape_backslash=False must suppress that for CSV export.
    """

    def setUp(self):
        self.fmt_kwargs = {
            'encoding': 'utf-8',
            'colormap': NO_COLOR_MAP,
            'date_time_format': None,
            'float_precision': 3,
            'nullval': 'null',
            'decimal_sep': '.',
            'thousands_sep': ',',
            'boolean_styles': None
        }

    def test_text_backslash_terminal_display(self):
        """Terminal display doubles backslashes so they are visible in SELECT output."""
        self.assertEqual(
            format_value_text('V\\S', encoding='utf-8', colormap=NO_COLOR_MAP),
            'V\\\\S'
        )

    def test_text_backslash_csv_export(self):
        """CSV export must not double backslashes — csv.writer handles escaping."""
        self.assertEqual(
            format_value_text('V\\S', encoding='utf-8', colormap=NO_COLOR_MAP,
                              escape_backslash=False),
            'V\\S'
        )

    def test_text_multiple_backslashes_terminal(self):
        """Multiple backslashes are all doubled for terminal display."""
        self.assertEqual(
            format_value_text('a\\\\b', encoding='utf-8', colormap=NO_COLOR_MAP),
            'a\\\\\\\\b'
        )

    def test_text_multiple_backslashes_csv(self):
        """Multiple backslashes are preserved as-is for CSV export."""
        self.assertEqual(
            format_value_text('a\\\\b', encoding='utf-8', colormap=NO_COLOR_MAP,
                              escape_backslash=False),
            'a\\\\b'
        )

    def test_text_backslash_at_start_csv(self):
        """Backslash at start of string preserved for CSV export."""
        self.assertEqual(
            format_value_text('\\hello', encoding='utf-8', colormap=NO_COLOR_MAP,
                              escape_backslash=False),
            '\\hello'
        )

    def test_text_backslash_at_end_csv(self):
        """Backslash at end of string preserved for CSV export."""
        self.assertEqual(
            format_value_text('hello\\', encoding='utf-8', colormap=NO_COLOR_MAP,
                              escape_backslash=False),
            'hello\\'
        )

    def test_text_no_backslash_unaffected(self):
        """Plain text without backslashes is unaffected in both modes."""
        self.assertEqual(
            format_value_text('Hello World', encoding='utf-8', colormap=NO_COLOR_MAP),
            'Hello World'
        )
        self.assertEqual(
            format_value_text('Hello World', encoding='utf-8', colormap=NO_COLOR_MAP,
                              escape_backslash=False),
            'Hello World'
        )

    def test_text_empty_string(self):
        """Empty string passes through cleanly in both modes."""
        self.assertEqual(
            format_value_text('', encoding='utf-8', colormap=NO_COLOR_MAP),
            ''
        )
        self.assertEqual(
            format_value_text('', encoding='utf-8', colormap=NO_COLOR_MAP,
                              escape_backslash=False),
            ''
        )

    def test_list_backslash_terminal(self):
        """List element backslashes are doubled for terminal display."""
        list_val = ['V\\S', 'a\\\\b']
        cql_type = CqlType('list<text>')
        self.assertEqual(
            format_value_list(list_val, cqltype=cql_type, **self.fmt_kwargs),
            "['V\\\\S', 'a\\\\\\\\b']"
        )

    def test_list_backslash_csv_export(self):
        """escape_backslash=False propagates into list element formatters."""
        list_val = ['V\\S', 'a\\\\b']
        cql_type = CqlType('list<text>')
        self.assertEqual(
            format_value_list(list_val, cqltype=cql_type,
                              escape_backslash=False, **self.fmt_kwargs),
            "['V\\S', 'a\\\\b']"
        )

    def test_set_backslash_csv_export(self):
        """escape_backslash=False propagates into set element formatters."""
        set_val = ['V\\S']
        cql_type = CqlType('set<text>')
        self.assertEqual(
            format_value_set(set_val, cqltype=cql_type,
                             escape_backslash=False, **self.fmt_kwargs),
            "{'V\\S'}"
        )

    def test_tuple_backslash_csv_export(self):
        """escape_backslash=False propagates into tuple element formatters."""
        tuple_val = ('V\\S', 'hello')
        cql_type = CqlType('tuple<text, text>')
        self.assertEqual(
            format_value_tuple(tuple_val, cqltype=cql_type,
                               escape_backslash=False, **self.fmt_kwargs),
            "('V\\S', 'hello')"
        )

    def test_map_backslash_csv_export(self):
        """escape_backslash=False propagates through map key and value formatters."""
        map_val = {'k\\1': 'v\\1'}
        cql_type = CqlType('map<text, text>')
        self.assertEqual(
            format_value_map(map_val, cqltype=cql_type,
                             escape_backslash=False, **self.fmt_kwargs),
            "{'k\\1': 'v\\1'}"
        )

    def test_udt_backslash_csv_export(self):
        """escape_backslash=False propagates through UDT field value formatters."""
        udt_val = _MockUDT([('field_a', 'V\\S'), ('field_b', 'hello')])
        cql_type = CqlType('text')
        cql_type.sub_types = [CqlType('text'), CqlType('text')]
        self.assertEqual(
            format_value_utype(udt_val, cqltype=cql_type,
                               escape_backslash=False, **self.fmt_kwargs),
            "{field_a: 'V\\S', field_b: 'hello'}"
        )

    def test_udt_field_name_backslash_csv(self):
        """escape_backslash=False must also apply to UDT field names, not just values."""
        udt_val = _MockUDT([('field\\a', 'value')])
        cql_type = CqlType('text')
        cql_type.sub_types = [CqlType('text')]
        self.assertEqual(
            format_value_utype(udt_val, cqltype=cql_type,
                               escape_backslash=False, **self.fmt_kwargs),
            "{field\\a: 'value'}"
        )


if __name__ == '__main__':
    unittest.main()
