#!/usr/bin/env python3
r"""
Script designed to read in multiple data maps ans subtract them for comparison.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import scipy as sp
from ApertureMapModelTools import _get_logger, set_main_logger_level, DataField
from ApertureMapModelTools.DataProcessing import Percentiles

#
desc_str = r"""
Description: Reads in an aperture map and then two data maps to subtract
them. Any region of zero aperture is set to zero for the comparisons. The
data maps can be normalized both before and after if desired and the final
calculated data map is output.

Written By: Matthew stadelman
Date Written: 2016/10/27
Last Modfied: 2016/10/27
"""

# setting up logger
set_main_logger_level('info')
logger = _get_logger('ApertureMapModelTools.Scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help="prints debug messages (default: %(default)s)")
parser.add_argument('-f', '--force', action='store_true',
                    help="can overwrite existing files (default: %(default)s)")
parser.add_argument('-pn', '--pre-normalize', action='store_true',
                    help="normalizes data maps before subtraction")
parser.add_argument('-on', '--post-normalize', action='store_true',
                    help="normalizes processed data map after subtraction")
parser.add_argument('-abs', '--post-abs', action='store_true',
                    help="takes the absolute value of the map after subtraction")
parser.add_argument('map_file', type=os.path.realpath,
                    help='corresponding aperture map for data maps')

parser.add_argument('data_file1', type=os.path.realpath,
                    help='paraview CSV data file')

parser.add_argument('data_file2', type=os.path.realpath,
                    help='paraview CSV data file')

parser.add_argument('out_name',
                    help='the name of the processed map being output')
#
########################################################################


def apm_subtract_data_maps():
    r"""
    Parses command line arguments and delegates tasks to helper functions
    for actual data processing
    """
    args = parser.parse_args()
    args.perc = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    #
    if args.verbose:
        set_main_logger_level('debug')
    #
    # testing output map path
    if os.path.exists(args.out_name) and not args.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(args.out_name))
    #
    aper_map, data_map1, data_map2 = prepare_maps(args)
    result = process_maps(aper_map, data_map1, data_map2, args)
    #
    # writing out resultant data map
    sp.savetxt(args.out_name, result.data_map, delimiter='\t')


def prepare_maps(args):
    r"""
    loads the aperture map and data maps and then masks zero aperture zones
    as well as performs pre-subtraction normalization if desired.
    """
    #
    # loading files
    aper_map = DataField(args.map_file)
    data_map1 = DataField(args.data_file1)
    data_map2 = DataField(args.data_file2)
    #
    # generating percentiles of each data field
    msg = 'Percentiles of data map: '
    print(msg + os.path.basename(args.data_file1))
    output_percentile_set(data_map1, args)
    #
    print(msg + os.path.basename(args.data_file2))
    output_percentile_set(data_map2, args)
    #
    # masking zero aperture zones
    data_map1 = data_map1.data_vector
    data_map2 = data_map2.data_vector
    data_map1[sp.where(aper_map.data_vector == 0)] = 0
    data_map2[sp.where(aper_map.data_vector == 0)] = 0
    #
    # normalizing data maps if desired
    if args.pre_normalize:
        data_map1 = data_map1/sp.amax(sp.absolute(data_map1))
        data_map2 = data_map1/sp.amax(sp.absolute(data_map2))
    #
    # reshaping data maps back into 2-D arrays

    data_map1 = sp.reshape(data_map1, aper_map.data_map.shape)
    data_map2 = sp.reshape(data_map2, aper_map.data_map.shape)
    #
    #
    return aper_map, data_map1, data_map2


def process_maps(aper_map, data_map1, data_map2, args):
    r"""
    subtracts the data maps and then calculates percentiles of the result
    before outputting a final map to file.
    """
    #
    # creating resultant map from clone of aperture map
    result = aper_map.clone()
    result.data_map = data_map1 - data_map2
    result.data_vector = sp.ravel(result.data_map)
    result.infile = args.out_name
    result.outfile = args.out_name
    #
    print('Percentiles of data_map1 - data_map2')
    output_percentile_set(result, args)
    #
    # checking if data is to be normalized and/or absolute
    if args.post_abs:
        result.data_map = sp.absolute(result.data_map)
        result.data_vector = sp.absolute(result.data_vector)
    #
    if args.post_normalize:
        result.data_map = result.data_map/sp.amax(sp.absolute(result.data_map))
        result.data_vector = sp.ravel(result.data_map)
    #
    return result


def output_percentile_set(data_field, args):
    r"""
    Does three sets of percentiles and stacks them as columns: raw data,
    absolute value data, normalized+absolute value
    """
    data = {}
    #
    # outputting percentiles of initial subtraction to screen
    field = data_field.clone()
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['raw'] = pctle.processed_data
    #
    # normalizing data
    field = data_field.clone()
    field.data_map = field.data_map/sp.amax(sp.absolute(field.data_map))
    field.data_vector = sp.ravel(field.data_map)
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['norm'] = pctle.processed_data
    #
    # taking absolute value of data
    field = data_field.clone()
    field.data_map = sp.absolute(field.data_map)
    field.data_vector = sp.absolute(field.data_vector)
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['abs'] = pctle.processed_data
    #
    # absolute value + normed
    field.data_map = field.data_map/sp.amax(field.data_map)
    field.data_vector = sp.ravel(field.data_map)
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['abs+norm'] = pctle.processed_data
    #
    # outputting stacked percentiles
    fmt = '    {:>6.2f}\t{: 0.6e}\t{: 0.6e}\t{: 0.6e}\t{: 0.6e}\n'
    content = 'Percentile\tRaw Data\tAbsolute\tNormalized\tNorm+abs\n'
    data = zip(args.perc, data['raw'].values(),
               data['abs'].values(),
               data['norm'].values(),
               data['abs+norm'].values())
    #
    for row in data:
        content += fmt.format(*row)
    content += '\n'
    print(content)


if __name__ == '__main__':
    apm_subtract_data_maps()
