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


class Image:
    """
    A class used to represent entities of both types "Image" and "Global Image".
    Each entity of type "Image" holds information about an existing Docker image that runs a ROS node and is
    associated with a robotic agent.
    Each entity of type "Global Image" holds information about an existing Docker image, that is not ROS related
    and is not associated with a particual robotic agent.

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
    required_fields = ['id', 'image']

    # flake8: noqa: C901
    def __parse_yaml_data(self, yaml_data, robot):
        """Parses the YAML data for a given entity of type "Image".

        In order to be considered valid, the passed YAML data must contain a non-empty entry for each required field.

        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.

        robot : object
            The robotic agent where the ROS node represented by the entity will be run.
            Disambiguation between entities of type "Image" and "Global Image" is done by setting
            this parameter to None (in case an instance of the latter is to be considered).
        """

        # Ensure the provided YAML data contains all the required fields
        for field in self.required_fields:

            if field not in yaml_data:
                print(f'An image was declared without required field "{field}" .')
                sys.exit(1)

            elif field == 'id':

                # Ensure provided id is not empty.
                if not yaml_data['id']:
                    print('An image was declared with an empty "id"')
                    sys.exit(1)

                # Since a same entity of type "Image" may be used several times within distinct robots,
                # it is crucial to ensure that each instance of a same entity has a unique "id".
                # An unique "id" is then obtained by joining the "id" of the "Robot" with the own entity's "id".
                # For entities of type "Global Image" this care is not required.
                if robot:
                    self.id = '{}-{}'.format(robot.id, yaml_data['id'])
                else:
                    self.id = yaml_data['id']
                self.yaml_data['id'] = self.id

            elif field == 'image':
                # Verify if Docker image's tag was specified or not.
                # If not then use default value, which depends on whether the
                # image is global or not.
                parts = yaml_data['image'].split(':')
                if len(parts) == 1:
                    if robot:
                        self.yaml_data['tag'] = '{{ROBOT_ROS_DISTRO}}'
                    else:
                        self.yaml_data['tag'] = 'latest'
                else:  # use provided tag
                    image, tag = parts
                    self.yaml_data['image'] = image
                    self.yaml_data['tag'] = tag

        # Process declared environmental variables, for entities of type "Image".
        # Add default environmental variables based on ROS version of the passed robot.
        # ROS1 distributions require the set of variables ROS_HOSTNAME and ROS_MASTER_URI.
        # ROS2 distributions require only the variable ROS_DOMAIN_ID to be set.
        environment = []
        if 'environment' in self.yaml_data:
            environment = self.yaml_data['environment']
        if robot:
            if robot.yaml_data['ros_version'] == "ROS1":
                environment.append(f'ROS_HOSTNAME={self.id}')
                environment.append('ROS_MASTER_URI=http://roscore-{{ROBOT_ID}}:{{ROBOT_ROS_PORT}}')
            else:
                environment.append('ROS_DOMAIN_ID={{ROBOT_ROS_DOMAIN}}')
        self.yaml_data['environment'] = environment

        if robot:
            # All images must also be automatically connected to the same area network as their robot.
            networks = []
            if 'networks' in yaml_data:
                networks = yaml_data['networks']
            networks.append(f"{robot.yaml_data['area']}-network")
            self.yaml_data['networks'] = networks

            # All ROS1 images must depend on the container running the master ROS node.
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
