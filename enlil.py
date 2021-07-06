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
