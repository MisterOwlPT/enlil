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


class TestEntityRobot(unittest.TestCase):

    __area_data = {'id': 'dummy_area'}

    @mock.patch.object(Robot, '_Robot__parse_yaml_data')
    def test_parsing_robot(self, mock):
        """ Test if the same provided data is the one being parsed.
        """
        yaml_data = {'dummy': 'dummy'}
        robot = Robot(yaml_data, self.__area_data)
        mock.assert_called_once_with(yaml_data)
        self.assertEqual(robot.yaml_data, yaml_data)

    def test_loading_robot_without_id(self):
        """ Test if execution is terminated if provided data has no required field "id".
        """
        yaml_data = {'dummy': 'dummy'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_invalid_id(self):
        """ Test if execution is terminated if provided data has an empty "id" field.
        """
        yaml_data = {'id': ''}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_without_ros(self):
        """ Test if execution is terminated if provided data has no required field "ros".
        """
        yaml_data = {'id': 'dummy_robot'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_invalid_distro(self):
        """ Test if execution is terminated if an invalid ROS distribuiton is specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'unknown'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_ros1_no_port(self):
        """ Test if execution is terminated if no port is specified for a ROS1 robot.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_ros1_invalid_port(self):
        """ Test if execution is terminated if an invalid port is specified for a ROS1 robot.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:port'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_ros1_port(self):
        """ Test if port for a ROS1 robot is properly sey when specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:13342', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        robot_port = int(yaml_data['ros'].split(':')[-1])
        self.assertEqual(robot.yaml_data['ros_metadata'], robot_port)

    def test_loading_robot_ros1_default_port(self):
        """ Test if port for a ROS1 robot is properly sey when specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        self.assertEqual(robot.yaml_data['ros_metadata'], 11311)

    def test_loading_robot_ros2_no_domain(self):
        """ Test if execution is terminated if no domain is specified for a ROS2 robot.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'foxy:'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_ros2_invalid_domain(self):
        """ Test if execution is terminated if an invalid somain is specified for a ROS2 robot.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'foxy:domain'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_ros2_domain(self):
        """ Test if domain for a ROS2 robot is properly set when specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'foxy:43', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        robot_domain = int(yaml_data['ros'].split(':')[-1])
        self.assertEqual(robot.yaml_data['ros_metadata'], robot_domain)

    def test_loading_robot_ros2_default_domain(self):
        """ Test if default domain for a ROS2 robot is used when no other is specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'foxy', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        self.assertEqual(robot.yaml_data['ros_metadata'], 42)

    def test_loading_robot_empty(self):
        """ Test if execution is terminated if a robot is specified without images or packages.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11311'}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_empty_image(self):
        """ Test if execution is terminated if a robot is specified with an empty image "id".
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11311', 'images': ['dummy_image', '']}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_multiple_images(self):
        """ Test if execution is terminated if an image is declared multiple times within a robot.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11311', 'images': ['dummy_image', 'dummy_image']}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_empty_package(self):
        """ Test if execution is terminated if a robot is specified with an empty package "id".
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11311', 'packages': ['dummy_package', '']}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_multiple_packages(self):
        """ Test if execution is terminated if a package is declared multiple times within a robot.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11311', 'packages': ['dummy_package', 'dummy_package']}
        with self.assertRaises(SystemExit) as exception:
            Robot(yaml_data, self.__area_data)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_robot_default_restart(self):
        """ Test if a default value for "restart" is properly set.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11311', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        self.assertEqual(robot.yaml_data['restart'], 'always')

    def test_loading_robot_ros1_default_environment_variables(self):
        """ Test if default environment variables for a ROS1 robot are properly set when no "port" is specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)

        robot_id = yaml_data['id']
        self.assertEqual(len(robot.yaml_data['environment']), 2)
        self.assertEqual(robot.yaml_data['environment'][0], f"ROS_HOSTNAME=roscore-{robot_id}")
        self.assertEqual(robot.yaml_data['environment'][1], f"ROS_MASTER_URI=http://roscore-{robot_id}:11311")

    def test_loading_robot_ros1_environment_variables(self):
        """ Test if default environment variables for a ROS1 robot are properly set.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11342', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)

        robot_id = yaml_data['id']
        robot_port = yaml_data['ros'].split(':')[-1]
        self.assertEqual(len(robot.yaml_data['environment']), 2)
        self.assertEqual(robot.yaml_data['environment'][0], f"ROS_HOSTNAME=roscore-{robot_id}")
        self.assertEqual(robot.yaml_data['environment'][1], f"ROS_MASTER_URI=http://roscore-{robot_id}:{robot_port}")

    def test_loading_robot_ros1_export_ports(self):
        """ Test if default "port" is exported automatically by all ROS1 robots if none other specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11312', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)

        robot_port = yaml_data['ros'].split(':')[-1]
        self.assertEqual(len(robot.yaml_data['ports']), 1)
        self.assertEqual(robot.yaml_data['ports'][0], f"{robot_port}:{robot_port}")

    def test_loading_robot_ros1_export_default_ports(self):
        """ Test if default "port" is exported automatically by all ROS1 robots if none other specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)

        self.assertEqual(len(robot.yaml_data['ports']), 1)
        self.assertEqual(robot.yaml_data['ports'][0], "11311:11311")

    def test_loading_robot_ros1_command(self):
        """ Test if default "port" is used automatically by all ROS1 robots if none other specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic:11312', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        robot_port = yaml_data['ros'].split(':')[-1]
        self.assertEqual(robot.yaml_data['command'], f"roscore --port {robot_port}")

    def test_loading_robot_ros1_default_command(self):
        """ Test if default "port" is used automatically by all ROS1 robots if none other specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        self.assertEqual(robot.yaml_data['command'], "roscore --port 11311")

    def test_loading_robot_ros2_default_environment_variables(self):
        """ Test if default environment variables for a ROS2 robot are properly set when no "port" is specified.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'foxy', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)
        self.assertEqual(len(robot.yaml_data['environment']), 1)
        self.assertEqual(robot.yaml_data['environment'][0], "ROS_DOMAIN_ID=42")

    def test_loading_robot_ros2_environment_variables(self):
        """ Test if default environment variables for a ROS2 robot are properly set.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'foxy:64', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)

        robot_domain = yaml_data['ros'].split(':')[-1]
        self.assertEqual(len(robot.yaml_data['environment']), 1)
        self.assertEqual(robot.yaml_data['environment'][0], f"ROS_DOMAIN_ID={robot_domain}")

    def test_loading_robot_networks(self):
        """ Test if networks for a robot are properly set.
        """
        yaml_data = {'id': 'dummy_robot', 'ros': 'melodic', 'packages': ['dummy_package']}
        robot = Robot(yaml_data, self.__area_data)

        self.assertEqual(len(robot.yaml_data['networks']), 1)
        self.assertEqual(robot.yaml_data['networks'][0], f"{self.__area_data['id']}-network")


if __name__ == '__main__':
    unittest.main()
