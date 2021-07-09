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

# List of supported ROS and ROS2 distros.
# NOTE: probably more distros are supported - list
# only the distros that were actually tested.
ROS1_DISTROS = ['melodic', 'noetic']
ROS2_DISTROS = ['foxy']


class Robot:
    """
    A class used to represent an entity of type "Robot".
    Each entity of this type holds information about a robotic agents.

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
    # Depending on the value of required field "ros" some other fields are also required ("port" and "domain").
    # The logic that ensures these extra required fields are present is already implemented
    # in inside function "__parse_yaml_data". Therefore don't add such fields to this list.
    required_fields = ['id', 'ros']

    # flake8: noqa: C901
    def __parse_yaml_data(self, yaml_data):
        """Parses the YAML data for a given entity of type "Robot".

        In order to be considered valid, the passed YAML data must contain a non-empty entry for each required field.
        Besides that a verification is done to ensure that:
         - at least a package or an image is being declared (all existent robots must run at least one ROS node);
         - no package or image is being declared multiple times;
         - a supported ROS distribution is being selected.

        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.
        """

        # Ensure the provided YAML data contains all the required fields.
        for field in self.required_fields:

            if field not in yaml_data:
                print(f'A robot was declared without required field "{field}" .')
                sys.exit(1)

            elif field == 'id':
                # Ensure provided id is not empty
                if not yaml_data['id']:
                    print('A robot was declared with an empty "id"')
                    sys.exit(1)
                self.id = yaml_data['id']

            elif field == 'ros':

                parts = self.yaml_data['ros'].split(':')

                if not parts[0]:
                    print(f'Robot "{self.id}" was declared an empty ROS distribution.')
                    sys.exit(1)

                # The attribute "ros_version" is added to the YAML data to avoid passing
                # the arrays of distributions to later phases of the pipeline, as this
                # disambiguation between ROS and ROS2 is crucial.
                if parts[0] in ROS1_DISTROS:
                    self.yaml_data['ros_version'] = 'ROS1'
                    self.yaml_data['ros_distro'] = parts[0]
                    # Robots using ROS1 must also declare a "port".
                    if len(parts) == 1:  # use default value
                        self.yaml_data['ros_metadata'] = 11311
                    else:  # use passed value
                        if parts[-1]:
                            try:
                                self.yaml_data['ros_metadata'] = int(parts[-1])
                            except ValueError:
                                print(f'Robot "{self.id}" was declared with an invalid value for port "{parts[-1]}"')
                                sys.exit(1)
                        else:  # and invalid value for "port" was passed
                            print(f'Robot "{self.id}" was declared without a value for port')
                            sys.exit(1)

                elif parts[0] in ROS2_DISTROS:
                    self.yaml_data['ros_version'] = 'ROS2'
                    self.yaml_data['ros_distro'] = parts[0]
                    # Robots using ROS2 must also declare a "domain".
                    if len(parts) == 1:  # use default value
                        self.yaml_data['ros_metadata'] = 42
                    else:  # use passed value
                        if parts[-1]:
                            try:
                                self.yaml_data['ros_metadata'] = int(parts[-1])
                            except ValueError:
                                print(f'Robot "{self.id}" was declared with an invalid value for domain "{parts[-1]}"')
                                sys.exit(1)
                        else:
                            print(f'Robot "{self.id}" was declared without a value for domain')
                            sys.exit(1)

                # Ensure a supported ROS distribution was selected.
                else:
                    print(f'Found invalid or unsupported ROS distribution "{parts[0]}"')
                    sys.exit(1)

        environment = []
        if 'environment' in self.yaml_data:
            environment = self.yaml_data['environment']
        if yaml_data['ros_version'] == "ROS1":
            environment.append(f'ROS_HOSTNAME=roscore-{self.id}')
            environment.append(f"ROS_MASTER_URI=http://roscore-{self.id}:{yaml_data['ros_metadata']}")
        else:
            environment.append(f"ROS_DOMAIN_ID={yaml_data['ros_metadata']}")
        self.yaml_data['environment'] = environment

        # Automatically export ports so that nodes may be able to communicate with the master node.
        # This is only required for ROS1 robots.
        if yaml_data['ros_version'] == "ROS1":
            self.yaml_data['ports'] = [f"{yaml_data['ros_metadata']}:{yaml_data['ros_metadata']}"]
            self.yaml_data['command'] = f"roscore --port {yaml_data['ros_metadata']}"

        # Since a same entity of type "Package" and "Image" may be used several times
        # within distinct robots, it is crucial to ensure that each instance of a same entity has a unique "id".
        # An unique "id" is then obtained by joining the "id" of the "Robot" with the own entity's "id".

        images = []
        if 'images' in yaml_data:
            for image in yaml_data['images']:
                if not image:
                    print(f'An image with no identifier was passed within robot "{self.id}"')
                    sys.exit(1)
                # Ensure no image was declared multiple times.
                image_id = f'{self.id}-{image}'
                if image_id in images:
                    print(f'A same image "{image}" was declared multiple times within robot "{self.id}"')
                    sys.exit(1)
                images.append(image_id)
        self.yaml_data['images'] = images

        packages = []
        if 'packages' in yaml_data:
            for package in yaml_data['packages']:
                if not package:
                    print(f'A package with no identifier was passed within robot "{self.id}"')
                    sys.exit(1)
                # Ensure no package was declared multiple times.
                package_id = f'{self.id}-{package}'
                if package_id in packages:
                    print(f'A same package "{package}" was declared multiple times within robot "{self.id}"')
                    sys.exit(1)
                packages.append(package_id)
        self.yaml_data['packages'] = packages

        # Ensure that at least a package or an image is being declared.
        if not images and not packages:
            print(f'Robot "{self.id}" was declared without images or packages.')
            sys.exit(1)

        # Prepare robot networks. Even if no network is specified, all robots must be
        # automatically connected to their area's network.
        networks = []
        if 'networks' in yaml_data:
            networks = yaml_data['networks']
        networks = [f"{yaml_data['area']}-network"]
        self.yaml_data['networks'] = networks

        # The default value for "restart" is "no".
        # Unless some other value is specified set default to "always".
        if 'restart' not in yaml_data:
            self.yaml_data['restart'] = 'always'

    def __init__(self, yaml_data, area):
        """
        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.

        area : dict
            The area where the robot operates.
        """

        self.yaml_data = yaml_data
        self.yaml_data['area'] = area['id']

        self.__parse_yaml_data(yaml_data)
