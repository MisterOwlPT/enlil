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

import os
import sys
import yaml

from .entities.area import Area
from .entities.image import Image
from .entities.package import Package
from .entities.robot import Robot


class EntityLoader():
    """
    A class used to parse an input configuration file and instantiate all entities accordingly.

    ...

    Attributes
    ----------
    areas : dict
        placeholder for all declared entities of type "Area" referenced by their unique "id".

    global_images : dict
        placeholder for all declared entities of type "Global Images" referenced by their unique "id".

    images : dict
        placeholder for all declated entities of type "Image" referenced by their unique "id".

    packages : dict
        placeholder for all declated entities of type "Package" referenced by their unique "id".

    robots : dict
        placeholder for all declated entities of type "Robot" referenced by their unique "id".

    yaml_data : dict
        the complete YAML data contained in the input configuration file.
    """

    areas = {}
    global_images = {}
    images = {}
    packages = {}
    robots = {}

    # Contains all used values of the "port" field (ROS1 robots)
    __used_ports = []

    # Contains all used values of the "domain" field (ROS2 robots)
    __used_domains = []

    def __init__(self, configuration_file_path):
        """
        Parameters
        ----------
        configuration_file_path : str
            The path for an YAML configuration input file.
        """

        self._load_data(configuration_file_path)

    # Load all entities
    # flake8: noqa: C901
    def _load_data(self, configuration_file_path):
        """Loads the contents of an YAML configuration input file.

            Parameters
            ----------
            configuration_file_path : str
                Path for the YAML configuration file to load.
            """

        # Open configuration file and ensure proper extension file.
        _, extension = os.path.splitext(configuration_file_path)
        with open(configuration_file_path, 'r') as configuration_file:
            if extension in ['.yaml', '.yml']:
                self.yaml_data = yaml.safe_load(configuration_file)
            else:
                print(f'Unsupported type "{extension}" for configuration file')
                sys.exit(1)

        # Entities are loaded hierarchically according to the following order:
        # - Areas
        #   - Robots
        #       - Packages
        #       - Images
        # - Global Images
        try:
            # Ensure that at least one entity of type "Area" is declared.
            for area in self.yaml_data['areas']:
                self._add_entity_area(area)
                try:
                    for robot_id in area['robots']:
                        # Load all declared robots within an area.
                        # NOTE: robots belonging to unknown areas will be ignored.
                        for robot in self.yaml_data['robots']:
                            if robot['id'] == robot_id:
                                self._add_entity_robot(robot, area)
                except KeyError:
                    print(f'Robot "{robot_id}" was listed but not declared.')
                    sys.exit(1)

        except KeyError:
            print('No robotic areas were declared')
            sys.exit(1)

        # Load all declared global images
        if 'globals' in self.yaml_data:
            for global_image in self.yaml_data['globals']:
                self._add_entity_image(global_image, None)

    def _add_entity_area(self, yaml_data):
        """Loads a new entity of type "Area".

        Ensures that each loaded area has an unique "id" value.

        Parameters
        ----------
        yaml_data : dict
            YAML data of the entity to be loaded.
        """

        # Load entity of type "Area".
        area = Area(yaml_data)

        # Ensures all entities have an unique "id".
        if area.id in self.areas:
            print(f'Found multiple areas with same id "{area.id}"')
            sys.exit(1)
        else:
            self.areas[area.id] = area

    # Load an entity of type 'Robot'
    # flake8: noqa: C901
    def _add_entity_robot(self, yaml_data, area):
        """Loads a new entity of type "Robot".

        For each robot loaded it triggers the loading of associated entities.
        Besides that a verification is done to ensure that:
         - each loaded robot has an unique "id" value.
         - each robot running ROS uses a different "port".
         - each robot running ROS2 uses a different "domain".

        Parameters
        ----------
        yaml_data : dict
            YAML data of the entity to be loaded.

        area : dict
            The area where the robot operates.
        """

        # Load entity of type "Robot".
        robot = Robot(yaml_data, area)

        # Ensures all entities have an unique "id".
        if robot.id in self.robots:
            print(f'Found multiple robots with same id "{robot.id}"')
            sys.exit(1)
        else:

            # Ensure unique values for "port".
            if robot.yaml_data['ros_version'] == 'ROS1':
                port = robot.yaml_data['ros_metadata']
                if port in self.__used_ports:
                    print(f'Multiple ROS robots using port "{port}"')
                    sys.exit(1)
                self.__used_ports.append(port)

            # Ensure unique values for "domain".
            if robot.yaml_data['ros_version'] == 'ROS2':
                domain = robot.yaml_data['ros_metadata']
                if domain in self.__used_domains:
                    print(f'Multiple ROS2 robots using domain "{domain}"')
                    sys.exit(1)
                self.__used_domains.append(domain)

            self.robots[robot.id] = robot

        try:
            # Load an entity of type "Package" for all packages associated with the loaded robot.
            for package in self.yaml_data['packages']:
                if f"{robot.id}-{package['id']}" in robot.yaml_data['packages']:
                    self._add_entity_package(package, robot)
        except KeyError:
            pass

        try:
            # Load an entity of type "Image" for all images associated with the loaded robot.
            for image in self.yaml_data['images']:
                if f"{robot.id}-{image['id']}" in robot.yaml_data['images']:
                    self._add_entity_image(image, robot)
        except KeyError:
            pass

    # Load an entity of type 'Image'
    def _add_entity_image(self, yaml_data, robot):
        """Loads a new entity of either type "Image" or type "Global Image".

        Besides that a verification is done to ensure that:
         - each loaded global image has an unique "id" value;
         - each loaded image has an unique "id" value.

        Parameters
        ----------
        yaml_data : dict
            YAML data of the entity to be loaded.

        robot : object
            The robotic agent where the ROS node represented by the entity will be run.
            Disambiguation between entities of type "Image" and "Global Image" is done by setting
            this parameter to None (in case an instance of the latter is to be considered).
        """

        # Load entity.
        image = Image(yaml_data, robot)

        # Select the place to store the loaded entity based on its type.
        if robot:  # storing an entity of type "Image"
            if image.id in self.images:
                print(f'Found multiple images with same id "{image.id}"')
                sys.exit(1)
            self.images[image.id] = image
        else:  # storing an entity of type "Global Image"
            if image.id in self.global_images:
                print(f'Found multiple global images with same id "{image.id}"')
                sys.exit(1)
            self.global_images[image.id] = image

    # Load an entity of type 'Package'
    def _add_entity_package(self, yaml_data, robot):
        """Loads a new entity of type "Package".

        Besides that a verification is done to ensure that:
         - each loaded package has an unique "id" value.

        Parameters
        ----------
        yaml_data : dict
            YAML data of the entity to be loaded.

        robot : object
            The robotic agent where the ROS node represented by the entity will be run.
        """

        # Load entity of type "Package".
        package = Package(yaml_data, robot)

        # Ensure that each loaded package has an unique "id".
        if package.id in self.packages:
            print(f'Found multiple packages with same id "{package.id}"')
            sys.exit(1)
        else:
            self.packages[package.id] = package
