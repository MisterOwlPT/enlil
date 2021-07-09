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

import re
import sys

from copy import copy


class Decoder():
    """
    A class to decode values of template variables.

    Template variables consist of all information stored within the YAML data of entities and between curly braces.
    Similar to variables in a programming language, template variables work as placeholders for useful information
    that must be decoded before the rendering of the output files.
    Template variables allow for the reusage of entity definitions.
    There are two types of template variables:
        - the ones defined internally by the application itself;
        - the ones defined externally by developers at the configuration file level.
    User defined template variables are set using the field "vars".

    The decoding follow an hierarchical scheme, starting with the areas that contain the robotic agents.
    These are then decoded, followed by the packages and images they temselves contain.

    Entities of type "Global Image" pass inaltered through the decoding stage.
    ...

    Attributes
    ----------
    areas : dict
        placeholder for all decoded entities of type "Area" referenced by their unique "id".

    global_images : dict
        placeholder for all decoded entities of type "Global Images" referenced by their unique "id".

    images : dict
        placeholder for all decoded entities of type "Image" referenced by their unique "id".

    packages : dict
        placeholder for all decoded entities of type "Package" referenced by their unique "id".

    robots : dict
        placeholder for all decoded entities of type "Robot" referenced by their unique "id".
    """

    areas = {}
    global_images = {}
    images = {}
    packages = {}
    robots = {}

    # The mapping between template variable names and their value.
    # This structure is the one responsible for the atual decoding of template variables.
    __decoder_variables = {}

    def __init__(self, areas, robots, images, packages, global_images):
        """
        Parameters
        ----------
        areas : dict
            placeholder for all loaded entities of type "Area" referenced by their unique "id".

        robots : dict
            placeholder for all loaded entities of type "Robot" referenced by their unique "id".

        images : dict
            placeholder for all loaded entities of type "Image" referenced by their unique "id".

        packages : dict
            placeholder for all loaded entities of type "Package" referenced by their unique "id".

        global_images : dict
            placeholder for all loaded entities of type "Global Images" referenced by their unique "id".
        """

        self.areas = areas
        self.robots = robots
        self.images = images
        self.packages = packages
        self.global_images = global_images

        # Trigger the decoding of all loaded entities.
        self.__decode()

    # Decode YAML data using the template variables mechanism
    def __substitute_template_variable(self, data):
        """Looks for and decodes all existing template variables within a sample of data.

        Besides that a verification is done to ensure that:
         - all user defined template variables were defined in the input configuration file.

        Parameters
        ----------
        data : str
            A sample of data from an entity containing template variables.

        Returns
        -------
        str
            the provided sample of data decoded.
        """

        decoded = data

        # Make sure no whitespaces exist between variable name and curly brackets.
        # TODO: remove automatically as many spaces as required. Assuming at most only one whitespace.
        decoded = decoded.replace("{{ ", "{{")
        decoded = decoded.replace(" }}", "}}")

        # Look for all template variables in between {{...}}.
        matches = re.findall("{{[A-Z_]+}}", decoded)
        for match in matches:
            try:
                # Substitute template variables by their current value.
                decoded = decoded.replace(
                    match,
                    str(self.__decoder_variables[match])
                )
            except KeyError:  # an unspecified template variable was found.
                print(f'Invalid template variable "{match}" found while decoding an instance')
                sys.exit(1)

        return decoded

    def __traverse_yaml_data(self, yaml_data):
        """Traverse the entire YAML data of an entity and substitute all existent template variables.

        Parameters
        ----------
        yaml_data : dict
            The complete YAML data of a given loaded entity.
        """

        # NOTE: The traversal of the YAML data is done recursively by the auxiliar function __traverse_yaml_data_aux.
        # This function works as a wrapper for that function simplifying the passing of arguments.
        # Therefore make sure to always call this function instead of the auxiliary one.
        self.__traverse_yaml_data_aux(yaml_data, yaml_data)

    def __traverse_yaml_data_aux(self, complete_yaml_data, yaml_data, path=''):
        """Recursive funtion to traverse the entire YAML data of an entity and substitute all existent template variables.

        This function is an auxiliary function to "__traverse_yaml_data" and should never be called directly.

        Parameters
        ----------
        complete_yaml_data : dict
            The complete YAML data of a given loaded entity.

        yaml_data : dict
            The part of YAML data of a given loaded entity that is being decoded in the current recursive step.

        path : str
            An accumulator variable (default='').
        """

        type_data = type(yaml_data)

        # Case base - a leaf node has been reached and its data must be decoded.
        # Leaf nodes are all nodes that are not of type "list" or "dict".
        if type_data in [bool, float, int, str]:
            decoded_leaf_node = self.__substitute_template_variable(str(yaml_data))  # noqa: F841
            exec(f'complete_yaml_data{path} = decoded_leaf_node')

        elif type_data in [list]:  # "list"
            for i in range(len(yaml_data)):
                self.__traverse_yaml_data_aux(complete_yaml_data, yaml_data[i], path + f"[{i}]")

        else:  # "dict"
            for field, field_value in yaml_data.items():
                # The field 'vars' contains definitions of template variables that are to be passed
                # between entities and therefore must not be decoded within the same level they are declared.
                if field not in ['vars']:
                    self.__traverse_yaml_data_aux(complete_yaml_data, field_value, path + f"['{field}']")

    def __decode_area(self, area):
        """Decode the YAML data of a single entity of type "Area".

        Parameters
        ----------
        area : object
            The entity of type "Area" to be decoded.
        """

        # Entities of type "Area" are the top of the hierarchy created between entities.
        # Therefere, whenever the YAML data of a new entity of type "Area" starts being decoded it
        # is crucial to clear all information regarding previous decodings.
        self.__decoder_variables = {}

        # Set the global tempalte variables to be passed to all other entities.
        self.__decoder_variables['{{AREA_ID}}'] = area.id

        # Trigger the decoding of the robots within the area.
        self.areas[area.id] = area
        for robot_id in area.yaml_data['robots']:
            robot = self.robots[robot_id]
            self.__decode_robot(robot)

    # flake8: noqa: C901
    def __decode_robot(self, robot):
        """Decode the YAML data of a single entity of type "Robot".

        Parameters
        ----------
        robot : object
            The entity of type "Robot" to be decoded.
        """

        # Make sure to use make a copy of the "robot" instance
        # so that the same base information may be used in decoding multiple
        # instances of type "package" and "image".
        __robot = copy(robot)

        self.__traverse_yaml_data(__robot.yaml_data)
        self.robots[__robot.id] = __robot

        # Set the global template variables to be passed to instances of type "package" and "image".
        self.__decoder_variables['{{ROBOT_ID}}'] = __robot.id
        self.__decoder_variables['{{ROBOT_ROS_DISTRO}}'] = __robot.yaml_data['ros_distro']
        if __robot.yaml_data['ros_version'] == 'ROS1':
            self.__decoder_variables['{{ROBOT_ROS_PORT}}'] = __robot.yaml_data['ros_metadata']
        else:
            self.__decoder_variables['{{ROBOT_ROS_DOMAIN}}'] = __robot.yaml_data['ros_metadata']

        # Set the custom template variables to be passed to instances of type "package" and "image".
        if 'vars' in __robot.yaml_data:
            for entry in __robot.yaml_data['vars']:
                for var, value in entry.items():
                    self.__decoder_variables['{{' + var + '}}'] = value

        # Trigger decoding of entities of type "image" associated with the robot.
        if 'images' in __robot.yaml_data:
            for image_id in __robot.yaml_data['images']:
                try:
                    image = self.images[image_id]
                    self.__decode_image(image)
                except KeyError:
                    # TODO: pass this verification step to the first stage of the pipeline.
                    print(f'Image "{image_id}" was listed but not declared.')
                    sys.exit(1)

        # Trigger decoding of entities of type "package" associated with the robot.
        if 'packages' in __robot.yaml_data:
            for package_id in __robot.yaml_data['packages']:
                try:
                    package = self.packages[package_id]
                    self.__decode_package(package)
                except KeyError:
                    # TODO: pass this verification step to the first stage of the pipeline.
                    print(f'Image "{image_id}" was listed but not declared.')
                    sys.exit(1)

    def __decode_image(self, image, is_global=False):
        """Decode the YAML data of a single entity of type "Image".

        Parameters
        ----------
        image : object
            The entity of type "Image" to be decoded.
        """

        # Make sure to use make a copy of the original "image" instance
        # so that the same base information may be used in decoding multiple instances.
        __image = copy(image)

        # Decode all template variables.
        self.__traverse_yaml_data(__image.yaml_data)

        self.images[__image.id] = __image

    def __decode_package(self, package):
        """Decode the YAML data of a single entity of type "Package".

        Parameters
        ----------
        pacakge : object
            The entity of type "Package" to be decoded.
        """

        # Make sure to use make a copy of the original "package" instance
        # so that the same base information may be used in decoding multiple instances.
        __package = copy(package)

        # Replace all template variables
        self.__traverse_yaml_data(__package.yaml_data)
        self.packages[__package.id] = __package

    def __decode(self):
        """Decode the YAML data of all loaded entities.
        """

        for _, area in self.areas.items():
            self.__decode_area(area)
