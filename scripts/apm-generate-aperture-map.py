#!/usr/bin/env python3
r"""
Script designed to take a TIF stack and produce a flattened aperture map
from it.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import scipy as sp
from ApertureMapModelTools import _get_logger, set_main_logger_level
from ApertureMapModelTools import FractureImageStack

#
desc_str = r"""
Description: Generates a 2-D aperture map based on a binary CT image stack. You
can add the format descriptor {image_file} in the aperture_map_name and it will
be automatically replaced by the basename of the image file used.

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

parser.add_argument('aperture_map_name', nargs='?',
                    default='{image_file}-aperture-map.txt',
                    help='name to save the aperture map under (default: %(default)s)')


def apm_generate_aperture_map():
    r"""
    Driver function to generate an aperture map from a TIF image.
    """
    # parsing commandline args
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')

    # checking path to prevent accidental overwriting
    image_file = os.path.basename(args.image_file)
    image_file = os.path.splitext(image_file)[0]
    if not args.aperture_map_name:
        args.aperture_map_name = '{image_file}-aperture-map.txt'
    args.aperture_map_name = args.aperture_map_name.format(image_file=image_file)
    #
    map_path = os.path.join(args.output_dir, args.aperture_map_name)
    if os.path.exists(map_path) and not args.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(map_path))
    os.makedirs(os.path.split(map_path)[0], exist_ok=True)

    # loading image data
    logger.info('loading image...')
    img_data = FractureImageStack(args.image_file)
    if args.invert:
        logger.debug('inverting image data')
        img_data = ~img_data
    logger.debug('image dimensions: {} {} {}'.format(*img_data.shape))

    # summing data array down into a 2-D map
    logger.info('creating 2-D aperture map...')
    aperture_map = img_data.create_aperture_map()

    # saving map
    logger.info('saving aperture map as {}'.format(map_path))
    sp.savetxt(map_path, aperture_map, fmt='%d', delimiter='\t')

#
if __name__ == '__main__':
    apm_generate_aperture_map()
