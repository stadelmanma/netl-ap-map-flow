#!/usr/bin/env python3
r"""
Script designed to take a TIF stack and produce a colored tiff stack based on
aperture.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import scipy as sp
from ApertureMapModelTools import _get_logger, set_main_logger_level
from ApertureMapModelTools import FractureImageStack

#
desc_str = r"""
Description: Color a tiff stack by the fracture aperture, the maximum value is
255, anything greater is reduced.

Written By: Matthew stadelman
Date Written: 2016/09/13
Last Modfied: 2017/02/11
"""
# setting up logger
set_main_logger_level('info')
logger = _get_logger('ApertureMapModelTools.Scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-f', '--force', action='store_true',
                    help='allows program to overwrite existing files')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs files to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('-i', '--invert', action='store_true',
                    help='use this flag if your fracture is in black')

parser.add_argument('image_file', type=os.path.realpath,
                    help='binary TIF stack image to process')

parser.add_argument('colored_stack_name', nargs='?', default=None,
                    help='name to save the colored stack under')


def apm_color_stack_by_aperture():
    r"""
    Driver function to color the tif image.
    """
    # parsing commandline args
    namespace = parser.parse_args()
    if namespace.verbose:
        set_main_logger_level('debug')

    # checking path to prevent accidental overwritting
    if not namespace.colored_stack_name:
        filename = os.path.basename(namespace.image_file)
        filename = os.path.splitext(filename)[0]
        namespace.colored_stack_name = filename + '-colored.tif'

    #
    filename = os.path.join(namespace.output_dir, namespace.colored_stack_name)
    if os.path.exists(filename) and not namespace.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(filename))

    # create the aperture colored image
    image = gen_colored_map(namespace.image_file, namespace.invert)

    # saving map
    logger.info('saving image data to file' + filename)
    image.save(filename, overwrite=namespace.force)


def gen_colored_map(image_file, invert):
    r"""
    Handles producing a colored image
    """
    # loading image data
    logger.info('loading image...')
    image = FractureImageStack(image_file)
    if invert:
        logger.debug('inverting image data')
        image = ~image
    logger.debug('image dimensions: {} {} {}'.format(*image.shape))

    # summing data array down into a 2-D map
    logger.info('generating 2-D aperture map...')
    aperture_map = image.create_aperture_map(dtype=sp.uint8).T
    aperture_map[aperture_map > 255] = 255

    # mapping aperture data back to image stack
    x_coords, y_coords, z_coords = image.get_fracture_voxels(coordinates=True)
    image = sp.zeros(image.shape, dtype=sp.uint8)
    image[x_coords, y_coords, z_coords] = aperture_map[x_coords, z_coords]
    #
    return image.view(FractureImageStack)


if __name__ == '__main__':
    apm_color_stack_by_aperture()
