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

from pipeline.loader.entities.robot import Robot
from pipeline.loader.entities.image import Image


class TestEntityImage(unittest.TestCase):

    __robotic_area = {
        'id': 'dummy_area',
        'robots': ['dummy_ros1_robot', 'dummy_ros2_robot']
    }

    __robot_ros1_data = {
        'id': 'dummy_ros1_robot',
        'ros': 'melodic:11311',
        'images': ['dummy_image']
    }

    __robot_ros2_data = {
        'id': 'dummy_ros2_robot',
        'ros': 'foxy:42',
        'images': ['dummy_image']
    }

    __robot_ros1 = Robot(__robot_ros1_data, __robotic_area)
    __robot_ros2 = Robot(__robot_ros2_data, __robotic_area)

    @mock.patch.object(Image, '_Image__parse_yaml_data')
    def test_parsing_image(self, mock):
        """ Test if the same provided data is the one being parsed.
        """
        yaml_data = {'dummy': 'dummy'}
        image = Image(yaml_data, self.__robot_ros1)
        mock.assert_called_once_with(yaml_data, self.__robot_ros1)
        self.assertEqual(image.yaml_data, yaml_data)

    def test_loading_image_without_id(self):
        """ Test if execution is terminated if provided data has no required field "id".
        """
        yaml_data = {'dummy': 'dummy'}
        with self.assertRaises(SystemExit) as exception:
            Image(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_image_invalid_id(self):
        """ Test if execution is terminated if provided data has an empty "id" field.
        """
        yaml_data = {'id': ''}
        with self.assertRaises(SystemExit) as exception:
            Image(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_image_without_docker_image(self):
        """ Test if execution is terminated if provided data has no required field "image".
        """
        yaml_data = {'id': 'dummy_image'}
        with self.assertRaises(SystemExit) as exception:
            Image(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_image_ros1_id(self):
        """ Test if field "id" is properly set for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image_id = yaml_data['id']
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(image.yaml_data['id'], f"{self.__robot_ros1.id}-{image_id}")

    def test_loading_image_ros2_id(self):
        """ Test if field "id" is properly set for ROS2 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image_id = yaml_data['id']
        image = Image(yaml_data, self.__robot_ros2)
        self.assertEqual(image.yaml_data['id'], f"{self.__robot_ros2.id}-{image_id}")

    def test_loading_gobal_image_id(self):
        """ Test if field "id" is properly set for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image_id = yaml_data['id']
        image = Image(yaml_data, None)
        self.assertEqual(image.yaml_data['id'], f'{image_id}')

    def test_loading_image_default_docker_image_tag(self):
        """ Test if default tag is properly set.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(image.yaml_data['tag'], '{{ROBOT_ROS_DISTRO}}')

    def test_loading_global_image_default_docker_image_tag(self):
        """ Test if default tag is properly set for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, None)
        self.assertEqual(image.yaml_data['tag'], 'latest')

    def test_loading_image_docker_image_tag(self):
        """ Test if tag is properly set.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image:dummy_tagas'}
        tag = yaml_data['image'].split(':')[-1]
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(image.yaml_data['tag'], tag)

    def test_loading_image_ros1_environment_variables(self):
        """ Test if default environment variables are set properly for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(len(image.yaml_data['environment']), 2)
        self.assertTrue(f"ROS_HOSTNAME={yaml_data['id']}" in image.yaml_data['environment'])
        self.assertTrue('ROS_MASTER_URI=http://roscore-{{ROBOT_ID}}:{{ROBOT_ROS_PORT}}' in image.yaml_data['environment'])

    def test_loading_image_ros2_environment_variables(self):
        """ Test if default environment variables are set properly for ROS2 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros2)
        self.assertEqual(len(image.yaml_data['environment']), 1)
        self.assertTrue('ROS_DOMAIN_ID={{ROBOT_ROS_DOMAIN}}' in image.yaml_data['environment'])

    def test_loading_global_image_no_environment_variables(self):
        """ Test if no environment variables are set by default for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, None)
        self.assertEqual(len(image.yaml_data['environment']), 0)

    def test_loading_image_ros1_networks(self):
        """ Test if default networks are properly set for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(len(image.yaml_data['networks']), 1)
        self.assertTrue(f"{self.__robotic_area['id']}-network" in image.yaml_data['networks'])

    def test_loading_image_ros2_networks(self):
        """ Test if default networks are properly set for ROS2 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros2)
        self.assertEqual(len(image.yaml_data['networks']), 1)
        self.assertTrue(f"{self.__robotic_area['id']}-network" in image.yaml_data['networks'])

    def test_loading_global_image_no_networks(self):
        """ Test if no default networks are set for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, None)
        self.assertTrue('networks' not in image.yaml_data)

    def test_loading_image_ros1_depends_on(self):
        """ Test if field "depends_on" is properly set for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(len(image.yaml_data['depends_on']), 1)
        self.assertTrue(f"roscore-{self.__robot_ros1.yaml_data['id']}" in image.yaml_data['depends_on'])

    def test_loading_image_ros2_depends_on(self):
        """ Test if field "depends_on" is not set for ROS2 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros2)
        self.assertEqual(len(image.yaml_data['depends_on']), 0)

    def test_loading_global_image_no_depends_on(self):
        """ Test if field "depends_on" is not set for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, None)
        self.assertTrue('depends_on' not in image.yaml_data)

    def test_loading_image_ros1_restart_default(self):
        """ Test if field "restart" is properly set to default for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(image.yaml_data['restart'], 'always')

    def test_loading_image_ros1_restart(self):
        """ Test if field "restart" is properly set when specified for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image', 'restart': 'dummy'}
        image = Image(yaml_data, self.__robot_ros1)
        self.assertEqual(image.yaml_data['restart'], yaml_data['restart'])

    def test_loading_image_ros2_restart_default(self):
        """ Test if field "restart" is properly set to default for ROS2 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, self.__robot_ros2)
        self.assertEqual(image.yaml_data['restart'], 'always')

    def test_loading_image_ros2_restart(self):
        """ Test if field "restart" is properly set when specified for ROS1 images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image', 'restart': 'dummy'}
        image = Image(yaml_data, self.__robot_ros2)
        self.assertEqual(image.yaml_data['restart'], yaml_data['restart'])

    def test_loading_global_image_restart_default(self):
        """ Test if field "restart" is properly set to default for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image'}
        image = Image(yaml_data, None)
        self.assertEqual(image.yaml_data['restart'], 'always')

    def test_loading_global_image_restart(self):
        """ Test if field "restart" is properly set when specified for global images.
        """
        yaml_data = {'id': 'dummy_image', 'image': 'dummy_docker_image', 'restart': 'dummy'}
        image = Image(yaml_data, None)
        self.assertEqual(image.yaml_data['restart'], yaml_data['restart'])


if __name__ == '__main__':
    unittest.main()
