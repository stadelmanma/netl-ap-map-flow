r"""
Description: Generates a 2-D aperture map based on a binary image stack. You
can add the format descriptor {image_file} in the aperture_map_name and it will
be automatically replaced by the basename of the image file used.

For usage information run: ``apm_generate_aperture_map -h``

| Written By: Matthew stadelman
| Date Written: 2016/09/13
| Last Modfied: 2017/04/23

|

"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import numpy as np
from apmapflow import _get_logger, set_main_logger_level
from apmapflow import FractureImageStack

# setting up logger
set_main_logger_level('info')
logger = _get_logger('apmapflow.scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawDesc)

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

parser.add_argument('--gen-colored-stack', action='store_true',
                    help='create a copy of the tif stack colored by the apeture')

msg = 'name to save the aperture map under (default: %(default)s)'
parser.add_argument('aperture_map_name', nargs='?',
                    default='{image_file}-aperture-map.txt',
                    help=msg)


def main():
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
    np.savetxt(map_path, aperture_map, fmt='%d', delimiter='\t')

    # generating colored stack if desired
    if args.gen_colored_stack:
        image = gen_colored_image_stack(img_data, aperture_map)
        # save the image data
        filename = os.path.splitext(image_file)[0] + '-colored.tif'
        filename = os.path.join(args.output_dir, filename)
        #
        logger.info('saving image data to file' + filename)
        image.save(filename, overwrite=args.force)


def gen_colored_image_stack(img_data, aperture_map):
    r"""
    Handles producing a colored image
    """
    # transpose map so it matches image data orientation
    aperture_map = aperture_map.T
    aperture_map[aperture_map > 255] = 255

    # color each X-Z column of the image stack according to it's aperture
    logger.debug('creating colored image stack')
    x_coords, y_coords, z_coords = img_data.get_fracture_voxels(coordinates=True)
    img_data = np.zeros(img_data.shape, dtype=np.uint8)
    img_data[x_coords, y_coords, z_coords] = aperture_map[x_coords, z_coords]
    #
    return img_data.view(FractureImageStack)
