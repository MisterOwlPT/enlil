# Enlil
#
# Copyright © 2021 Pedro Pereira, Rafael Arrais
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest
from unittest import mock

from pipeline.loader.entities.area import Area


class TestEntityArea(unittest.TestCase):

    @mock.patch.object(Area, '_Area__parse_yaml_data')
    def test_parsing_area(self, mock):
        """ Test if the same provided data is the one being parsed.
        """
        yaml_data = {'dummy': 'dummy'}
        area = Area(yaml_data)
        mock.assert_called_once_with(yaml_data)
        self.assertEqual(area.yaml_data, yaml_data)

    def test_loading_area_empty_data(self):
        """ Test if execution is terminated if empty data is provided.
        """
        with self.assertRaises(SystemExit) as exception:
            Area({})
        self.assertEqual(exception.exception.code, 1)

    def test_loading_area_without_id(self):
        """ Test if execution is terminated if provided data has no required field "id".
        """
        yaml_data = {'dummy': 'dummy'}
        with self.assertRaises(SystemExit) as exception:
            Area(yaml_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_area_invalid_id(self):
        """ Test if execution is terminated if provided data has an empty "id" field.
        """
        yaml_data = {'id': ''}
        with self.assertRaises(SystemExit) as exception:
            Area(yaml_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_area_without_robots(self):
        """ Test if execution is terminated if provided data has no required field "robots".
        """
        yaml_data = {'id': 'dummy_area'}
        with self.assertRaises(SystemExit) as exception:
            Area(yaml_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_empty_area(self):
        """ Test if execution is terminated if provided data has an empty "robots" field.
        """
        yaml_data = {'id': 'dummy_area', 'robots': []}
        with self.assertRaises(SystemExit) as exception:
            Area(yaml_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_area_with_same_robots(self):
        """ Test if execution is terminated if a same robot is declared multiple times within an area.
        """
        yaml_data = {'id': 'dummy_area', 'robots': ['dummy_robot', 'dummy_robot']}
        with self.assertRaises(SystemExit) as exception:
            Area(yaml_data)
        self.assertEqual(exception.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
