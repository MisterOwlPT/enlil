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
import shutil
import sys
from jinja2 import Template
from pkg_resources import resource_string


class Renderizer:
    """
    A class to render the final Docker Compose YAML file.

    Additionally a Dockerfile is also rendered for each package instance.

    Attributes
    ----------
    areas : dict
        placeholder for YAML data of entities of type "Area" referenced by their unique "id".

    direct_volumes : list
        contains a list of all the direct volumes used.

    global_images : dict
        placeholder for YAML data of entities of type "Global Images" referenced by their unique "id".

    images : dict
        placeholder for YAML data ofentities of type "Image" referenced by their unique "id".

    labeled_volumes : list
        contains a list of all the labeled volumes used.

    networks : list
        contains a list of all the networkd used.

    output_file_path : str
        the path in which to place the final Docker Compose YAML file.

    packages : dict
        placeholder for YAML data of entities of type "Package" referenced by their unique "id".

    robots : dict
        placeholder for YAML data of entities of type "Robot" referenced by their unique "id".
    """

    # initializes the data structures required for rendering
    def __init__(self, output_file_path, areas, robots, images, global_images, packages):
        """

        Parameters
        ----------
        output_file_path : str
            the path in which to place the final Docker Compose YAML file.

        areas : dict
            placeholder for all decoded entities of type "Area" referenced by their unique "id".

        robots : dict
            placeholder for all decoded entities of type "Robot" referenced by their unique "id".

        images : dict
            placeholder for all decoded entities of type "Image" referenced by their unique "id".

        global_images : dict
            placeholder for all decoded entities of type "Global Images" referenced by their unique "id".

        packages : dict
            placeholder for all decoded entities of type "Package" referenced by their unique "id".
        """
        self.output_file_path = output_file_path

        # Initialize class attributes.
        # Extract only the YAML data from the passed entities.
        self.areas = [area.yaml_data for _, area in areas.items()]
        self.global_images = [image.yaml_data for _, image in global_images.items()]
        self.images = [image.yaml_data for _, image in images.items()]
        self.packages = [package.yaml_data for _, package in packages.items()]
        self.robots = [robot.yaml_data for _, robot in robots.items()]

        # Join all volumes and networks used by all entities of type "image", "global_image" and "package"
        direct_volumes = []
        labeled_volumes = []
        networks = []

        for image in self.images:
            image_direct_volumes, image_labeled_volumes = self.__extract_volumes(image)
            direct_volumes += image_direct_volumes
            labeled_volumes += image_labeled_volumes

            networks += self.__extract_networks(image)

        for image in self.global_images:
            image_direct_volumes, image_labeled_volumes = self.__extract_volumes(image)
            direct_volumes += image_direct_volumes
            labeled_volumes += image_labeled_volumes

            networks += self.__extract_networks(image)

        for package in self.packages:
            package_direct_volumes, package_labeled_volumes = self.__extract_volumes(package)
            direct_volumes += package_direct_volumes
            labeled_volumes += package_labeled_volumes

            networks += self.__extract_networks(package)

        # Remove duplicates
        self.direct_volumes = list(dict.fromkeys(direct_volumes))
        self.labeled_volumes = list(dict.fromkeys(labeled_volumes))
        self.networks = list(dict.fromkeys(networks))

        # Render output files
        self.__render()

    def __tabs(self, number_tabs, tab_symbol='  '):
        return (f'{tab_symbol}' * number_tabs)

    def __stringify_service_robot(self, yaml_data, tabs=1):

        # ROS2 uses a distributed system and there is no master ROS node.
        if yaml_data['ros_version'] == 'ROS2':
            return ''

        final_str = f"{self.__tabs(tabs)}roscore-{yaml_data['id']}:\n"

        for field, value in yaml_data.items():

            if field not in ['area', 'images', 'packages', 'ros', 'ros_metadata', 'ros_version', 'vars']:

                type_data = type(value)

                if type_data in [bool, float, int, str]:

                    if field == 'id':
                        final_str += f"{self.__tabs(tabs + 1)}container_name: roscore-{value}\n"
                    elif field == 'ros_distro':
                        final_str += f"{self.__tabs(tabs + 1)}image: ros:{value}\n"
                    else:
                        final_str += f'{self.__tabs(tabs + 1)}{field}: {value}\n'

                elif type_data in [list]:
                    final_str += f'{self.__tabs(tabs + 1)}{field}:\n'
                    for entry in value:
                        final_str += f'{self.__tabs(tabs + 2)}- {entry}\n'

            # TODO: implement this mechanism for dictionaries
            # else:  # "dict"
            #     final_str += self.__stringify_service(field_value, tabs + f"['{field}']")

        return final_str

    def __stringify_service(self, yaml_data, tabs=1):

        final_str = f'{self.__tabs(tabs)}{yaml_data["id"]}:\n'

        for field, value in yaml_data.items():

            if field not in ['apt', 'command', 'files', 'git', 'git_cmds', 'ros', 'ssh', 'tag', 'vars']:

                type_data = type(value)

                if type_data in [bool, float, int, str]:

                    if field == 'id':
                        final_str += f"{self.__tabs(tabs + 1)}container_name: {value}\n"
                    elif field == 'image':  # an image
                        final_str += f"{self.__tabs(tabs + 1)}image: {value}:{yaml_data['tag']}\n"
                    elif field == 'path':
                        final_str += f"{self.__tabs(tabs + 1)}build: {value}{yaml_data['id']}\n"
                    else:
                        final_str += f'{self.__tabs(tabs + 1)}{field}: {value}\n'

                elif type_data in [list]:
                    if value:  # ensure the list is not empty
                        final_str += f'{self.__tabs(tabs + 1)}{field}:\n'
                        for entry in value:
                            final_str += f'{self.__tabs(tabs + 2)}- {entry}\n'

            # TODO: implement this mechanism for dictionaries
            # else:  # "dict"
            #     final_str += self.__stringify_service(field_value, tabs + f"['{field}']")

        return final_str

    def __extract_volumes(self, yaml_data):
        """Extract and filter all used volumes from an entity's YAML data.

        Parameters
        ----------
        yaml_data : dict
            An entity's YAML data.
        """

        direct_volumes = []
        labeled_volumes = []

        if 'volumes' in yaml_data:
            for volume in yaml_data['volumes']:
                parts = volume.split(':')
                if '/' in parts[0]:
                    direct_volumes.append(parts[0])
                else:  # labeled volume
                    labeled_volumes.append(parts[0])
        return direct_volumes, labeled_volumes

    def __extract_networks(self, yaml_data):
        """Extract all used networks from an entity's YAML data.

        Parameters
        ----------
        yaml_data : dict
            An entity's YAML data.
        """

        if 'networks' in yaml_data:
            return yaml_data['networks']
        return []

    def _create_folder(self, path):
        """ Create a folder to place Dockerfiles in case it does not exist already.

        Parameters
        ----------
        path : str
            Path where folder is to be created.
        """

        if not os.path.exists(path):
            os.makedirs(path)

    def __render(self):
        """  Renders the final Docker Compose YAMl file as well as all required Dockerfiles.
        """

        # Open template of Dockerfile.
        dockerfile_template = resource_string(__name__, 'templates/dockerfile.j2').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        # Create folder to place the Dockerfile for each package.
        path = '/'.join(self.output_file_path.split('/')[:-1])
        packages_path = f'{path}/packages'
        self._create_folder(packages_path)

        for package in self.packages:

            # Create a separate folder for each package.
            self._create_folder(f'{packages_path}/{package["id"]}/')

            # Create folder for SSH related files if specified.
            if 'ssh' in package:
                ssh_folder = f'{packages_path}/{package["id"]}/ssh/'
                self._create_folder(ssh_folder)
                for ssh_path in package['ssh']:
                    try:
                        file_name = ssh_path.split('/')[-1]
                        shutil.copyfile(ssh_path, ssh_folder + file_name)
                    except FileNotFoundError:
                        print(f'SSH file "{ssh_path}" was not found.')
                        sys.exit(1)

            if 'files' in package:

                # Create folder for files if specified.
                files_folder = f'{packages_path}/{package["id"]}/files/'
                self._create_folder(files_folder)

                if 'volumes' in package:
                    volumes = package["volumes"]
                else:
                    volumes = []

                for file_path in package['files']:

                    try:
                        external_file_path, internal_file_path = file_path.split(':')
                    except ValueError:
                        print(f'Invalid file declaration "{file_path}"')
                        sys.exit(1)

                    try:
                        # Make a copy of the file
                        file_name = external_file_path.strip().split('/')[-1]
                        shutil.copyfile(external_file_path, files_folder + file_name)
                    except FileNotFoundError as e:
                        print(f'File "{external_file_path}" was not found.')
                        sys.exit(1)

                    # Create a volume for the copied file
                    volumes.append(f"{files_folder + file_name}:{internal_file_path}")

                package["volumes"] = volumes

            # Render Dockerfile for each package
            with open(f'{packages_path}/{package["id"]}/Dockerfile', 'w+') as out:
                out.write(dockerfile_templater.render(package=package))

        # Open template of Docker Compose YAML file.
        compose_yaml_template = resource_string(__name__, 'templates/docker_compose.j2').decode('utf-8')
        compose_yaml_templater = Template(compose_yaml_template)

        # Render final Docker Compose YAML file
        with open(self.output_file_path, 'w+') as output_file:
            output_file.write(compose_yaml_templater.render(
                areas=self.areas,
                direct_volumes=self.direct_volumes,
                labeled_volumes=self.labeled_volumes,
                networks=self.networks,
                stringified_global_images=[self.__stringify_service(image) for image in self.global_images],
                stringified_images=[self.__stringify_service(image) for image in self.images],
                stringified_packages=[self.__stringify_service(package) for package in self.packages],
                stringified_robots=[self.__stringify_service_robot(robot) for robot in self.robots]
            ))
