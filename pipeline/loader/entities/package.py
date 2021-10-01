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

import sys
from distutils.util import strtobool


class Package:
    """
    A class used to represent an entity of type "Package".
    Each entity of this type holds information about a ROS node that is to be containerized
    at run-time.

    ...

    Attributes
    ----------
    id : str
        an unique identifier for the entity.

    required_fields : list
        the required fields for an entity of this type to be considered valid.

    yaml_data : dict
        the complete YAML data for the entity obtained from the input configuration file.
    """

    # WARNING: if adding more required fields ensure that field "id" is always the first.
    required_fields = ['id', 'path', 'command']

    # flake8: noqa: C901
    def __parse_yaml_data(self, yaml_data, robot):
        """Parses the YAML data for a given entity of type "Package".

        In order to be considered valid, the passed YAML data must contain a non-empty entry for each required field.

        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.

        robot : object
            The robotic agent where the ROS node represented by the entity will be run.
        """

        # Ensure the provided YAML data contains all the required fields
        for field in self.required_fields:

            if field not in yaml_data:
                print(f'A package was declared without required field "{field}" .')
                sys.exit(1)

            # Ensure provided id is not empty.
            if not yaml_data[field]:
                print(f'A package was declared with an empty "{field}"')
                sys.exit(1)

            elif field == 'id':

                # Since a same entity of type "Package" may be used several times within distinct robots,
                # it is crucial to ensure that each instance of a same entity has a unique "id".
                # An unique "id" is then obtained by joining the "id" of the "Robot" with the own entity's "id".

                self.id = '{}-{}'.format(robot.id, yaml_data['id'])
                self.yaml_data['id'] = self.id

        # If "git" field is present then add a list of the required "git clone" commands do the package YAML data.
        # This commands will later be used while rendering the package's Dockerfile, ensuring required repos are cloned.
        if 'git' in self.yaml_data:

            if not self.yaml_data['git']:
                print(f'Package "{self.id}" was declared with an empty value for "git"')
                sys.exit(1)

            git_cmds = []
            for entry in self.yaml_data['git']:
                parts = entry.split(':', 2)
                if len(parts) == 1:  # verify if "default" branch is to be used
                    git_cmds.append(f"git -C /ros_workspace/src clone -b {robot.yaml_data['ros'].split(':')[0]} {parts[0]}")
                else:
                    git_cmds.append(f"git -C /ros_workspace/src clone -b {parts[-1]} {':'.join(parts[:-1])}")
            self.yaml_data['git_cmds'] = git_cmds

        declared_fields = set(list(self.yaml_data.keys()))

        # Ensure that at least one of the fields "apt", "git" or "rosinstall" was selected.
        # There is no point in declaring an entity of this type if no ROS package is to be caontainerized.
        # NOTE: For "empty" containers entities of type "image" should be used instead.
        if not [field for field in ['apt', 'git', 'rosinstall'] if field in declared_fields]:
            print(f'Package "{self.id}" was declared without any ROS package.')
            sys.exit(1)

        # Ensure that fields "apt" and "rosinstall" are not empty, if selected.
        if 'apt' in self.yaml_data:
            if not self.yaml_data['apt']:
                print(f'Package "{self.id}" was declared with an empty value for "apt"')
                sys.exit(1)

        if 'rosinstall' in self.yaml_data:
            if not self.yaml_data['rosinstall']:
                print(f'Package "{self.id}" was declared with an empty value for "rosinstall"')
                sys.exit(1)

        # Ensure that field "files" is not empty, if selected 
        # Ensure that field "files" if a list of files
        if 'files' in self.yaml_data:
            
            if not self.yaml_data['files']:
                print(f'Package "{self.id}" was declared with an empty value for "files"')
                sys.exit(1)

            if not isinstance(self.yaml_data['files'], list):
                print(f'Field "files" of package "{self.id}" is not of type list')
                sys.exit(1)

            for filename in self.yaml_data['files']:
                if not isinstance(filename, str):
                    print(f'Field "files" of package "{self.id}" is not a list of files')
                    sys.exit(1)

        # Ensure that field "ssh" is not empty, if selected
        # Ensure that field "ssh" if a list of files
        if 'ssh' in self.yaml_data:
            if not self.yaml_data['ssh']:
                print(f'Package "{self.id}" was declared with an empty value for "ssh"')
                sys.exit(1)

            if not isinstance(self.yaml_data['ssh'], list):
                print(f'Field "ssh" of package "{self.id}" is not of type list')
                sys.exit(1)

            for filename in self.yaml_data['ssh']:
                if not isinstance(filename, str):
                    print(f'Field "ssh" of package "{self.id}" is not a list of files')
                    sys.exit(1)

        # Process declared environmental variables.
        # Add default environmental variables based on ROS version of the passed robot.
        # ROS1 distributions require the set of variables ROS_HOSTNAME and ROS_MASTER_URI.
        # ROS2 distributions require only the variable ROS_DOMAIN_ID to be set.
        environment = []
        if 'environment' in self.yaml_data:
            environment = self.yaml_data['environment']
        if robot.yaml_data['ros_version'] == "ROS1":
            environment.append(f'ROS_HOSTNAME={self.id}')
            environment.append('ROS_MASTER_URI=http://roscore-{{ROBOT_ID}}:{{ROBOT_ROS_PORT}}')
        else:
            environment.append('ROS_DOMAIN_ID={{ROBOT_ROS_DOMAIN}}')
        self.yaml_data['environment'] = environment

        # Copy the passed robot's ROS version to this instance's YAML data to later ease the
        # rendering of the package Dockerfile.
        self.yaml_data['ros'] = '{{ROBOT_ROS_DISTRO}}'

        # All packages must be automatically connected to the same area network as their robot.
        networks = []
        if 'networks' in yaml_data:
            networks = yaml_data['networks']
        networks.append(f"{robot.yaml_data['area']}-network")
        self.yaml_data['networks'] = networks

        # All ROS1 packages must depend on the container running the master ROS node.
        depends_on = []
        if 'depends_on' in yaml_data:
            depends_on = yaml_data['depends_on']
        if robot.yaml_data['ros_version'] == 'ROS1':
            depends_on.append(f"roscore-{robot.id}")
        self.yaml_data['depends_on'] = depends_on

        # The default value for "restart" is "no".
        # Unless some other value is specified set default to "always".
        if 'restart' not in yaml_data:
            self.yaml_data['restart'] = 'always'

    def __init__(self, yaml_data, robot):
        """
        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.

        robot : object
            The robotic agent where the ROS node represented by the entity will be run.
        """
        self.yaml_data = yaml_data
        self.__parse_yaml_data(yaml_data, robot)
