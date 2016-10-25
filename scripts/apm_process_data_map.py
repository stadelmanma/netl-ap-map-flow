#!/usr/bin/env python3
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
import os
import re
import sys
from ApertureMapModelTools import _get_logger, set_main_logger_level, DataField
from ApertureMapModelTools import DataProcessing
#
########################################################################
#
desc_str = r"""
Description: Processes data maps using the desired DataProcessing class
and either writes data to file or prints to screen.

Written By: Matthew stadelman
Date Written: 2015/10/01
Last Modfied: 2016/10/25
"""
#
# fetching logger
logger = _get_logger('ApertureMapModelTools.Scripts')
#
# setting up the argument parser
parser = argparse.ArgumentParser(description=desc_str,
                                 formatter_class=RawDesc)
#
# defining main arguments
parser.add_argument('-v', '--verbose', action='store_true',
                    help="prints debug messages (default: %(default)s)")
parser.add_argument('-f', '--force', action='store_true',
                    help="can overwrite existing files (default: %(default)s)")
parser.add_argument('-w', '--write', action='store_true', default=True,
                    help="writes data to CSV file (default: %(default)s)")
parser.add_argument('-W', '--no-write', action='store_true',
                    help="does not write data to file (default: %(default)s)")
parser.add_argument('-s', '--screen', action='store_true',
                    help="print data to screen (default: %(default)s)")
#
# defining sub-parsers
subparse_parent = argparse.ArgumentParser(add_help=False)
subparse_parent.add_argument('-files', type=os.path.realpath, required=True,
                             help='data file to process')
subparsers = parser.add_subparsers(dest='processor',
                                   title='Data Processing Commands',
                                   metavar='')
for cls in DataProcessing:
    print(cls)
    cls._add_subparser(subparsers, subparse_parent)


cmd_str = r"""
commands:
    eval_chans: "EvalChannels", processes the data to determine
        the number and widths of any channels present.
        (only really useful for flow data)

    hist: "Histogram", does a full min -> max val histogram of
        each input file

    hist_range: "HistogramRange", does a histrogram for the
        provided percentile range, i.e. 10th - 90th percentile

    hist_logscale: "HistogramLogscale" full range of data with logarithmic
        bin sizes

    profile: "Profile", outputs a vector of cells in either the x or z
        direction straight from the data file. Location is based on percentage
        from the bottom or left sides. i.e. locs=10,90 will output a profile
        at 1cm and 9cm if the axis is 10cm long.

    pctle: "Percentiles", outputs one or more percentiles from the data map
"""
#
########################################################################


def apm_process_data_map():
    r"""
    Parses command line arguments and delegates tasks to helper functions
    for actual data processing
    """
    args = parser.parse_args()
    #
    if args.verbose:
        set_main_logger_level('debug')
    #
    print(args)


#==============================================================================
#
# def process_files(arg_dict, data_proc_cls, files):
#     r"""
#     Reads in each file into a DataField object and then passes it off
#     to the specified data processor class
#     """
#     data_fields = apm.load_infile_list(files)
#     data_processors = [data_proc_cls(field) for field in data_fields]
#     print('')
#     #
#     for data_proc in data_processors:
#         #
#         # checking if args passed validation test
#         data_proc.set_args(arg_dict)
#         if not data_proc.validated:
#             print('')
#             continue
#         #
#         data_proc.process()
#         #
#         # printing to screen
#         if (arg_dict['flags']['v']):
#             data_proc.gen_output(delim='\t')
#             data_proc.print_data()
#         #
#         # writting data
#         if (arg_dict['flags']['w'] and not arg_dict['flags']['W']):
#             data_proc.gen_output(delim=',')
#             exists = os.path.isfile(data_proc.outfile_name)
#             if (exists and not arg_dict['flags']['f']):
#                 msg = 'Error: Outfile - {} already exists. '
#                 msg += 'The -f or --force flags need to be added to allow'
#                 msg += ' overwritting of an existing file.'
#                 eprint(msg.format(data_proc.outfile_name))
#                 continue
#             #
#             data_proc.write_data()
#==============================================================================

if __name__ == '__main__':
    apm_process_data_map()
