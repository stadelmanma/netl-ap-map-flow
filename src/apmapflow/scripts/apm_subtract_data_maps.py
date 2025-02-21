r"""
Description: Reads in an aperture map and then two data maps to subtract
them. Any region of zero aperture is set to zero for the comparisons. The
data maps can be normalized both before and after if desired and the final
calculated data map is output.

For usage information run: ``apm_subtract_data_maps -h``

| Written By: Matthew stadelman
| Date Written: 2016/10/27
| Last Modfied: 2017/04/23

|

"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import numpy as np
from apmapflow import _get_logger, set_main_logger_level, DataField
from apmapflow.data_processing import Percentiles


# setting up logger
set_main_logger_level('info')
logger = _get_logger('apmapflow.scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help="prints debug messages (default: %(default)s)")

parser.add_argument('-f', '--force', action='store_true',
                    help="can overwrite existing files (default: %(default)s)")

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs files to the specified
                    directory, sub-directories are created as needed''')

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


def main():
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
    filename = os.path.join(args.output_dir, args.out_name)
    np.savetxt(filename, result.data_map, delimiter='\t')


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
    logger.info(msg + os.path.basename(args.data_file1))
    output_percentile_set(data_map1, args)
    #
    logger.info(msg + os.path.basename(args.data_file2))
    output_percentile_set(data_map2, args)
    #
    # masking zero aperture zones
    data_map1 = data_map1.data_vector
    data_map2 = data_map2.data_vector
    data_map1[np.where(aper_map.data_vector == 0)] = 0
    data_map2[np.where(aper_map.data_vector == 0)] = 0
    #
    # normalizing data maps if desired
    if args.pre_normalize:
        data_map1 = data_map1 / np.amax(np.absolute(data_map1))
        data_map2 = data_map1 / np.amax(np.absolute(data_map2))
    #
    # reshaping data maps back into 2-D arrays
    data_map1 = np.reshape(data_map1, aper_map.data_map.shape)
    data_map2 = np.reshape(data_map2, aper_map.data_map.shape)
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
    result = data_map1 - data_map2
    result = DataField(result)
    result.infile = args.out_name
    result.outfile = args.out_name
    #
    logger.info('Percentiles of data_map1 - data_map2')
    output_percentile_set(result, args)
    #
    # checking if data is to be normalized and/or absolute
    if args.post_abs:
        result._data_map = np.absolute(result.data_map)
    #
    if args.post_normalize:
        result._data_map = result.data_map/np.amax(np.absolute(result.data_map))
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
    field = DataField(data_field.data_map)
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['raw'] = pctle.processed_data
    #
    # normalizing data
    field = DataField(data_field.data_map)
    field._data_map = field.data_map/np.amax(np.absolute(field.data_map))
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['norm'] = pctle.processed_data
    #
    # taking absolute value of data
    field = DataField(data_field.data_map)
    field._data_map = np.absolute(field.data_map)
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['abs'] = pctle.processed_data
    #
    # absolute value + normed
    field._data_map = field.data_map/np.amax(field.data_map)
    pctle = Percentiles(field, percentiles=args.perc)
    pctle.process()
    data['abs+norm'] = pctle.processed_data
    #
    # outputting stacked percentiles
    fmt = '    {:>6.2f}\t{: 0.6e}\t{: 0.6e}\t{: 0.6e}\t{: 0.6e}\n'
    content = '\nPercentile\tRaw Data\tAbsolute\tNormalized\tNorm+abs\n'
    data = zip(args.perc, data['raw'].values(),
               data['abs'].values(),
               data['norm'].values(),
               data['abs+norm'].values())
    #
    for row in data:
        content += fmt.format(*row)
    content += '\n'
    logger.info(content)
