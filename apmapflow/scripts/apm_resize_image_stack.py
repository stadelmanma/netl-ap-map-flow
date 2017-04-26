#!/usr/bin/env python3
r"""
Script designed to take a TIF stack and produce a colored tiff stack based on
aperture.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
from apmapflow import _get_logger, set_main_logger_level
from apmapflow import FractureImageStack

#
desc_str = r"""
Description: Reduces the y-axis dimension of an image stack.

Written By: Matthew stadelman
Date Written: 2016/09/13
Last Modfied: 2017/04/23
"""
# setting up logger
set_main_logger_level('info')
logger = _get_logger('apmapflow.Scripts')

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

parser.add_argument('outfile_name', nargs='?', default=None,
                    help='name to save the aperture map under')


def main():
    r"""
    Driver function to color the tif image.
    """
    # parsing commandline args
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')

    # checking path to prevent accidental overwritting
    if not args.outfile_name:
        filename = os.path.basename(args.image_file)
        filename = os.path.splitext(filename)[0]
        args.outfile_name = filename + '-resized.tif'

    #
    filename = os.path.join(args.output_dir, args.outfile_name)
    if os.path.exists(filename) and not args.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(filename))
    os.makedirs(os.path.split(filename)[0], exist_ok=True)

    # create the aperture colored image
    image = resize_image(args.image_file, args.invert)

    # saving map
    logger.info('saving image data to file' + filename)
    image.save(filename, overwrite=args.force)


def resize_image(image_file, invert):
    r"""
    Handles resizing the image y-axis
    """
    # loading image data
    logger.info('loading image...')
    image = FractureImageStack(image_file)
    if invert:
        logger.debug('inverting image data')
        image = ~image
    logger.debug('image dimensions: {} {} {}'.format(*image.shape))
    #
    x_coords, y_coords, z_coords = image.get_fracture_voxels(coordinates=True)
    y_min = max(0, y_coords.min() - 10)
    y_max = min(image.ny, y_coords.max() + 10)
    image = image[:, y_min:y_max, :]
    logger.debug(' new image dimensions: {} {} {}'.format(*image.shape))
    #
    return image
