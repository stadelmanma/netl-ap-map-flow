r"""
Description: Generates 2-D data maps from OpenFoam data saved by paraview
as a CSV file. The data has to be saved as point data and the following fields
are expected p, points:0->2, u:0->2. An aperture map is the second main input
and is used to generate the interpolation coordinates as well as convert
the flow velocities into volumetic flow rates. This script assumes the OpenFoam
simulation was performed on a geometry symmetric about the X-Z plane.

For usage information run: ``apm_process_paraview_data -h``

| Written By: Matthew stadelman
| Date Written: 2016/09/29
| Last Modfied: 2017/04/23

|

"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import scipy as sp
import numpy as np
from scipy.interpolate import griddata
from apmapflow import _get_logger, set_main_logger_level, DataField


# setting up logger
set_main_logger_level('info')
logger = _get_logger('apmapflow.scripts')

# setting a few convenience globals
avg_fact = None
voxel_size = None
base_name = None

# creating arg parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs file to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('--rho', type=float, default=1000,
                    help='fluid density for kinematic pressure conversion')

parser.add_argument('data_file', type=os.path.realpath,
                    help='paraview CSV data file')

parser.add_argument('map_file', type=os.path.realpath,
                    help='matching aperture map used for OpenFoam simulation')

parser.add_argument('voxel_size', type=float,
                    help='voxel to meter conversion factor of aperture map')

parser.add_argument('avg_fact', type=float,
                    help='''horizontal averaging factor of aperture map''')

parser.add_argument('base_name', nargs='?', default=None,
                    help='''base name to save fields as, i.e. base_name + "-p-map.txt",
                    defaults to the name of the CSV file''')


def main():
    r"""
    Processes commandline args and runs script
    """
    global avg_fact, voxel_size, base_name
    #
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')
    #
    # these will be command-line args
    para_infile = args.data_file
    aper_infile = args.map_file
    avg_fact = args.avg_fact
    voxel_size = args.voxel_size
    #
    base_name = args.base_name
    if base_name is None:
        base_name = os.path.basename(para_infile).split('.')[0]
    base_name = os.path.join(args.output_dir, base_name)
    #
    aper_map, data_dict = read_data_files(para_infile, aper_infile)
    map_coords, data_coords = generate_coordinate_arrays(aper_map, data_dict)
    save_data_maps(map_coords, data_coords, aper_map, data_dict, args.rho)


def read_data_files(para_file, map_file):
    r"""
    Reads in the paraview data file and aperture map file.
    """
    #
    # reading aperture map
    logger.info('reading aperture map...')
    aper_map = DataField(map_file)
    #
    # reading first line of paraview file to get column names
    logger.info('reading paraview data file')
    with open(para_file, 'r') as file:
        cols = file.readline()
        cols = cols.strip().replace('"', '').lower()
        cols = cols.split(',')

    #
    # reading entire dataset and splitting into column vectors
    data = np.loadtxt(para_file, delimiter=',', dtype=float, skiprows=1)
    data_dict = {}
    for i, col in enumerate(cols):
        data_dict[col] = data[:, i]
    #
    return aper_map, data_dict


def generate_coordinate_arrays(aper_map, para_data_dict):
    r"""
    Generates the coordinate arrays to use in data interpolation for coverting
    paraview point data into a 2-D data map.
    """
    #
    # generating XYZ coordinates from map to interpolate to
    logger.info('calculating aperture map cell center coordinates...')
    temp = np.arange(aper_map.data_map.size, dtype=int)
    temp = np.unravel_index(temp, aper_map.data_map.shape[::-1])
    map_coords = np.zeros((aper_map.data_map.size, 3), dtype=float)
    #
    # half voxel added to make map points be cell centers
    map_coords[:, 0] = temp[0] * avg_fact * voxel_size + voxel_size/2.0
    map_coords[:, 2] = temp[1] * avg_fact * voxel_size + voxel_size/2.0
    #
    # pulling XYZ coordinates from the data file
    logger.info('processing data file data for coordinates...')
    data_coords = np.zeros((para_data_dict['points:0'].shape[0], 3))
    data_coords[:, 0] = para_data_dict['points:0']
    data_coords[:, 1] = para_data_dict['points:1']
    data_coords[:, 2] = para_data_dict['points:2']
    #
    return map_coords, data_coords


def save_data_maps(map_coords, data_coords, aper_map, data_dict, density):
    r"""
    Converts the raw paraview point data into a 2-D data distribution and
    saves the file by appending to the base_name.
    """
    #
    # generating p field
    logger.info('generating and saving pressure field...')
    field = data_dict['p'] * density  # openFoam outputs kinematic pressure
    field = griddata(data_coords, field, map_coords, method='nearest')
    field = np.reshape(field, aper_map.data_map.shape[::-1])
    np.savetxt(base_name+'-p-map.txt', field.T, delimiter='\t')
    #
    # generating Ux -> Qx field
    logger.info('generating and saving Qx field...')
    field = data_dict['u:0']
    field = griddata(data_coords, field, map_coords, method='nearest')
    field = np.reshape(field, aper_map.data_map.shape[::-1])
    field = field * aper_map.data_map.T * voxel_size**2
    np.savetxt(base_name+'-qx-map.txt', field.T, delimiter='\t')
    #
    # generating Uz -> Qz field
    logger.info('generating and saving Qz field...')
    field = data_dict['u:2']
    field = griddata(data_coords, field, map_coords, method='nearest')
    field = np.reshape(field, aper_map.data_map.shape[::-1])
    field = field * aper_map.data_map.T * voxel_size**2
    np.savetxt(base_name+'-qz-map.txt', field.T, delimiter='\t')
    #
    # generating Um -> Qm field
    logger.info('generating and saving Q magnitude field...')
    field = np.lib.scimath.sqrt(data_dict['u:0'] ** 2 + data_dict['u:2'] ** 2)
    field = griddata(data_coords, field, map_coords, method='nearest')
    field = np.reshape(field, aper_map.data_map.shape[::-1])
    field = field * aper_map.data_map.T * voxel_size**2
    np.savetxt(base_name+'-qm-map.txt', field.T, delimiter='\t')
