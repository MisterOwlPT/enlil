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
from pipeline.loader.entities.package import Package


class TestEntityPackage(unittest.TestCase):

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

    @mock.patch.object(Package, '_Package__parse_yaml_data')
    def test_parsing_package(self, mock):
        """ Test if the same provided data is the one being parsed.
        """
        yaml_data = {'dummy': 'dummy'}
        package = Package(yaml_data, self.__robot_ros1)
        mock.assert_called_once_with(yaml_data, self.__robot_ros1)
        self.assertEqual(package.yaml_data, yaml_data)

    def test_loading_package_without_id(self):
        """ Test if execution is terminated if provided data has no required field "id".
        """
        yaml_data = {'dummy': 'dummy'}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_invalid_id(self):
        """ Test if execution is terminated if provided data has an empty "id" field.
        """
        yaml_data = {'id': ''}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_without_path(self):
        """ Test if execution is terminated if provided data has no required field "path".
        """
        yaml_data = {'id': 'dummy_package', 'command': 'dummy_command'}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_invalid_path(self):
        """ Test if execution is terminated if provided data has an empty "path" field.
        """
        yaml_data = {'id': 'dummy_package', 'path': '', 'command': 'dummy_command'}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_without_command(self):
        """ Test if execution is terminated if provided data has no required field "command".
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path'}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_invalid_command(self):
        """ Test if execution is terminated if provided data has an empty "path" field.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': ''}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_id(self):
        """ Test if "id" is set properly.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package_id = yaml_data['id']
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(package.id, f"{self.__robot_ros1.id}-{package_id}")

    def test_loading_package_no_content(self):
        """ Test if execution is terminated if any of the field "apt", "git" and "rosinstall" are not declared.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command'}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_empty_git(self):
        """ Test if execution is terminated if field "git" is declared but not set.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': []}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_no_git(self):
        """ Test if no "git clone" command is added when "git" field is not declared.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'apt': ['dummt_apt']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertTrue('git_cmds' not in package.yaml_data)

    def test_loading_package_git_default_branch(self):
        """ Test if "git clone" command are properly added when no branch is specified.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_git']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(len(package.yaml_data['git_cmds']), 1)
        self.assertEqual(
            package.yaml_data['git_cmds'][0],
            f"git -C /ros_workspace/src clone -b {self.__robot_ros1_data['ros'].split(':')[0]} {yaml_data['git'][0]}"
        )

    def test_loading_package_git_branch(self):
        """ Test if "git clone" command are properly added.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_git:branch']}
        git_repo, git_branch = yaml_data['git'][0].split(':')
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(len(package.yaml_data['git_cmds']), 1)
        self.assertEqual(
            package.yaml_data['git_cmds'][0],
            f"git -C /ros_workspace/src clone -b {git_branch} {git_repo}"
        )

    def test_loading_package_empty_apt(self):
        """ Test if execution is terminated if field "apt" is declared but not set.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'apt': []}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_empty_rosinstall(self):
        """ Test if execution is terminated if field "rosinstall" is declared but not set.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'rosinstall': []}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros1)
        self.assertEqual(exception.exception.code, 1)

    def test_loading_package_ros1_environment_variables(self):
        """ Test if default environment variables are set properly for ROS1 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(len(package.yaml_data['environment']), 2)
        self.assertTrue(f"ROS_HOSTNAME={yaml_data['id']}" in package.yaml_data['environment'])
        self.assertTrue('ROS_MASTER_URI=http://roscore-{{ROBOT_ID}}:{{ROBOT_ROS_PORT}}' in package.yaml_data['environment'])

    def test_loading_package_ros2_environment_variables(self):
        """ Test if default environment variables are set properly for ROS2 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros2)
        self.assertEqual(len(package.yaml_data['environment']), 1)
        self.assertTrue('ROS_DOMAIN_ID={{ROBOT_ROS_DOMAIN}}' in package.yaml_data['environment'])

    def test_loading_package_ros(self):
        """ Test if field "ros" is set properly.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(package.yaml_data['ros'], '{{ROBOT_ROS_DISTRO}}')

    def test_loading_package_ros1_networks(self):
        """ Test if default networks are properly set for ROS1 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(len(package.yaml_data['networks']), 1)
        self.assertTrue(f"{self.__robotic_area['id']}-network" in package.yaml_data['networks'])

    def test_loading_package_ros2_networks(self):
        """ Test if default networks are properly set for ROS2 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros2)
        self.assertEqual(len(package.yaml_data['networks']), 1)
        self.assertTrue(f"{self.__robotic_area['id']}-network" in package.yaml_data['networks'])

    def test_loading_package_ros1_depends_on(self):
        """ Test if field "depends_on" is properly set for ROS1 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(len(package.yaml_data['depends_on']), 1)
        self.assertTrue(f"roscore-{self.__robot_ros1.yaml_data['id']}" in package.yaml_data['depends_on'])

    def test_loading_package_ros2_depends_on(self):
        """ Test if field "depends_on" is not set for ROS2 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros2)
        self.assertEqual(len(package.yaml_data['depends_on']), 0)

    def test_loading_package_ros1_restart_default(self):
        """ Test if field "restart" is properly set to default for ROS1 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(package.yaml_data['restart'], 'always')

    def test_loading_package_ros1_restart(self):
        """ Test if field "restart" is properly set when specified for ROS1 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros1)
        self.assertEqual(package.yaml_data['restart'], yaml_data['restart'])

    def test_loading_package_ros2_restart_default(self):
        """ Test if field "restart" is properly set to default for ROS2 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros2)
        self.assertEqual(package.yaml_data['restart'], 'always')

    def test_loading_package_ros2_restart(self):
        """ Test if field "restart" is properly set when specified for ROS1 packages.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo']}
        package = Package(yaml_data, self.__robot_ros2)
        self.assertEqual(package.yaml_data['restart'], yaml_data['restart'])

    def test_ssh_empty(self):
        """ Test if execution finishes if field "ssh" is declared empty
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo'], 'ssh': []}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros2)
        self.assertEqual(exception.exception.code, 1)

    def test_ssh_not_list(self):
        """ Test if execution finishes if field "ssh" is not a list.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo'], 'ssh': 'random_path'}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros2)
        self.assertEqual(exception.exception.code, 1)

    def test_ssh_not_list_of_files(self):
        """ Test if execution finishes if field "ssh" is not a list of files.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo'], 'ssh': [[], 'dummy']}
        with self.assertRaises(SystemExit) as exception:
            Package(yaml_data, self.__robot_ros2)
        self.assertEqual(exception.exception.code, 1)

    def test_ssh_value_set(self):
        """ Test if field "ssh" is properly set when defined.
        """
        yaml_data = {'id': 'dummy_package', 'path': 'dummy_path', 'command': 'dummy_command', 'git': ['dummy_repo'], 'ssh': ['random_path']}
        package = Package(yaml_data, self.__robot_ros2)
        self.assertEqual(package.yaml_data['ssh'], yaml_data['ssh'])


if __name__ == '__main__':
    unittest.main()
