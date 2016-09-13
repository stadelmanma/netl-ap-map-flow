#!/usr/bin/env python3
r"""
Script designed to take a TIF stack and produce a flattened aperture map
from it.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
from PIL import Image
import os
import scipy as sp
from ApertureMapModelTools import _get_logger, set_main_logger_level

#
desc_str = r"""
Description: Generates a 2-D aperture map based on a binary CT image stack.

Written By: Matthew stadelman
Date Written: 2016/09/13
Last Modfied: 2016/09/13
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

parser.add_argument('aperture_map_name', nargs='?', default=None,
                    help='name to save the aperture map under')

def apm_generate_aperture_map():
    r"""
    Driver function to generate an aperture map from a TIF image.
    """
    # parsing commandline args
    namespace = parser.parse_args()
    if namespace.verbose:
        set_main_logger_level('debug')

    # checking path to prevent accidental overwritting
    if not namespace.aperture_map_name:
        map_name = os.path.basename(namespace.image_file)
        map_name = map_name.replace( os.path.splitext(map_name)[1], '-aperture-map.txt')
        namespace.aperture_map_name = map_name

    #
    map_path = os.path.join(namespace.output_dir, namespace.aperture_map_name)
    if os.path.exists(map_path) and not namespace.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(map_path))

    # loading image data
    data_array = load_image_data(namespace.image_file, namespace.invert)
    data_array = data_array.astype(sp.int8)

    # summing data array down into a 2-D map
    logger.info('creating 2-D aperture map...')
    aperture_map = sp.sum(data_array, axis=1, dtype=int)

    # saving map
    logger.info('saving aperture map as {}'.format(map_path))
    sp.savetxt(map_path, aperture_map.T, fmt='%d', delimiter='\t')

def load_image_data(image_file, invert):
    r"""
    Loads an image from a *.tiff stack and creates an array from it. The
    fracture is assumed to be black and the solid is white.
    """
    logger.info('loading image...')
    img_data = Image.open(image_file)
    #
    # creating full image array
    logger.info('creating image array...')
    data_array = []
    for frame in range(img_data.n_frames):
        img_data.seek(frame)
        frame = sp.array(img_data, dtype=bool).transpose()
        if invert:
            frame = ~frame  # beacuse fracture is black, solid is white
        data_array.append(frame)
    #
    data_array = sp.stack(data_array, axis=2)
    logger.debug('    image dimensions: {} {} {}'.format(*data_array.shape))
    #
    return data_array

#
if __name__ == '__main__':
    apm_generate_aperture_map()