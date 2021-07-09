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


class Area:
    """
    A class used to represent an entity of type "Area".
    Each entity of this type holds information about a physical area where several
    robotic agents may operate simultaneously.

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
    required_fields = ['id', 'robots']

    def __parse_yaml_data(self, yaml_data):
        """Parses the YAML data for a given entity of type "Area".

        In order to be considered valid, the passed YAML data must contain a non-empty entry for each required field.
        Besides that a verification is done to ensure that:
         - at least one robot is being declared;
         - no same robotic agent is being declared multiple times.

        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.
        """

        # Ensure the provided YAML data is not empty.
        if not len(yaml_data):
            print('An area was declared with empty data')
            sys.exit(1)

        # Ensure the provided YAML data contains all the required fields.
        for field in self.required_fields:

            if field not in yaml_data:
                print(f'An area was declared without required field "{field}"')
                sys.exit(1)

            elif field == 'id':
                # Ensure provided id is not empty.
                if not yaml_data['id']:
                    print('An area was declared with an empty "id"')
                    sys.exit(1)
                self.id = yaml_data['id']

            elif field == 'robots':
                # Ensure that a robot was not declared multiple times within a same area.
                robots = []
                for robot in yaml_data['robots']:
                    if robot in robots:
                        print(f'Robot "{robot}" was declared multiple times within area "{self.id}"')
                        sys.exit(1)
                    robots.append(robot)

                # Ensure at least one robot was declared
                if not robots:
                    print(f'Area "{self.id}" was declared without robots')
                    sys.exit(1)

    def __init__(self, yaml_data):
        """
        Parameters
        ----------
        yaml_data : dict
            The complete YAML data for the entity obtained from the input configuration file.
        """

        self.__parse_yaml_data(yaml_data)
        self.yaml_data = yaml_data
