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

"""Automatically containerize ROS worskpaces using Docker.
Usage:
  enlil <configuration_file> [<output_file>]
  enlil (-h | --help)
"""
import sys
from docopt import docopt
from os import path

from pipeline.decoder.decoder import Decoder
from pipeline.loader.entity_loader import EntityLoader
from pipeline.renderizer.renderizer import Renderizer


# Application entry point
def main():

    # Parse command line arguments
    arguments = docopt(__doc__)
    config_file = arguments['<configuration_file>']
    output_file = arguments['<output_file>']
    if not output_file:  # by default output file goes to current directory
        output_file = './docker-compose.yml'

    # Verify is specified configuration file exists
    if not path.isfile(config_file):
        print(f'Input configuration file "{config_file}" does not exist.')
        sys.exit(1)

    # Load all entities
    loader = EntityLoader(config_file)

    # Decode all entities
    decoder = Decoder(
        loader.areas,
        loader.robots,
        loader.images,
        loader.packages,
        loader.global_images
    )

    # Render final output file
    Renderizer(
        output_file,
        decoder.areas,
        decoder.robots,
        decoder.images,
        decoder.global_images,
        decoder.packages,
    )


if __name__ == '__main__':
    main()
